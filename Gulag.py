# meta developer: @AssaMods

import asyncio
import time

from herokutl.tl.functions.channels import EditBannedRequest
from herokutl.tl.types import ChatBannedRights

from .. import loader, utils

@loader.tds
class Gulag(loader.Module):
    """Democratic justice system for your chat. Let the people decide who goes to gulag!"""

    strings = {
        "name": "GULAG",
        "vote": "🗳 <b>Vote for punishment</b>\n\n👤 <b>Defendant:</b> <a href='tg://user?id={}'>{}</a>\n\n<i>Choose action below</i>",
        "gulag": "GULAG {}/{}",
        "forgive": "Forgive {}/{}",
        "banned": "⚖️ <a href='tg://user?id={}'>{}</a> <b>banned</b>",
        "kicked": "⚖️ <a href='tg://user?id={}'>{}</a> <b>kicked</b>",
        "muted": "⚖️ <a href='tg://user?id={}'>{}</a> <b>muted for {} min</b>",
        "forgiven": "⚖️ <a href='tg://user?id={}'>{}</a> <b>forgiven</b>",
        "no_reply": "<emoji document_id=6114014038960638990>❌</emoji> <b>Reply to the message..</b>",
        "no_rights": "😭 <b>Not enough rights</b>",
        "already": "Already voted for this!",
        "switched": "Vote switched!",
        "ended": "Vote ended!",
        "not_chat": "<emoji document_id=5019523782004441717>❌</emoji> <b>Only in chats!</b>",
    }

    strings_ru = {
        "vote": "🗳 <b>Голосование за наказание</b>\n\n👤 <b>Подсудимый:</b> <a href='tg://user?id={}'>{}</a>\n\n<i>Выберите действие</i>",
        "gulag": "ГУЛАГ {}/{}",
        "forgive": "Простить {}/{}",
        "banned": "⚖️ <a href='tg://user?id={}'>{}</a> <b>забанен</b>",
        "kicked": "⚖️ <a href='tg://user?id={}'>{}</a> <b>кикнут</b>",
        "muted": "⚖️ <a href='tg://user?id={}'>{}</a> <b>замучен на {} мин</b>",
        "forgiven": "⚖️ <a href='tg://user?id={}'>{}</a> <b>прощён</b>",
        "no_reply": "<emoji document_id=6114014038960638990>❌</emoji> <b>Ответьте на сообщение..</b>",
        "no_rights": "😭 <b>Недостаточно прав</b>",
        "already": "Уже голосовали за это!",
        "switched": "Голос переключён!",
        "ended": "Голосование окончено!",
        "not_chat": "<emoji document_id=5019523782004441717>❌</emoji> <b>Только в чатах!</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("votes", 5, lambda: "Votes required", validator=loader.validators.Integer(minimum=1)),
            loader.ConfigValue("punishment", "ban", lambda: "Punishment type", validator=loader.validators.Choice(["ban", "kick", "mute"])),
            loader.ConfigValue("mute_minutes", 60, lambda: "Mute duration in minutes", validator=loader.validators.Integer(minimum=1)),
        )
        self._votes: dict = {}

    def _build_markup(self, vote_id: str, gulag_count: int, forgive_count: int) -> list:
        return [[{"text": self.strings["gulag"].format(gulag_count, self.config["votes"]), "callback": self._handle_vote, "args": (vote_id, "gulag")}, {"text": self.strings["forgive"].format(forgive_count, self.config["votes"]), "callback": self._handle_vote, "args": (vote_id, "forgive")}]]

    async def _apply_punishment(self, chat_id: int, user_id: int) -> None:
        punishment = self.config["punishment"]
        if punishment == "ban":
            await self._client(EditBannedRequest(chat_id, user_id, ChatBannedRights(until_date=True, view_messages=True)))
        elif punishment == "kick":
            await self._client.kick_participant(chat_id, user_id)
        elif punishment == "mute":
            until = time.time() + (self.config["mute_minutes"] * 60)
            await self._client(EditBannedRequest(chat_id, user_id, ChatBannedRights(until_date=until, send_messages=True)))

    async def _get_result_text(self, user_id: int, name: str) -> str:
        punishment = self.config["punishment"]
        if punishment == "ban":
            return self.strings["banned"].format(user_id, name)
        elif punishment == "kick":
            return self.strings["kicked"].format(user_id, name)
        return self.strings["muted"].format(user_id, name, self.config["mute_minutes"])

    @loader.command(ru_doc="<reply> - начать голосование")
    async def gulag(self, message):
        """<reply> - start voting"""
        if not message.is_group:
            return await utils.answer(message, self.strings["not_chat"])

        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, self.strings["no_reply"])

        user = await self._client.get_entity(reply.sender_id)
        vote_id = f"{message.chat_id}_{user.id}"

        self._votes[vote_id] = {"gulag": set(), "forgive": set(), "user_id": user.id, "chat_id": message.chat_id, "name": user.first_name}

        await utils.answer(message, self.strings["vote"].format(user.id, user.first_name), reply_markup=self._build_markup(vote_id, 0, 0), disable_security=True)

    async def _handle_vote(self, call, vote_id: str, vote_type: str) -> None:
        if vote_id not in self._votes:
            return await call.answer(self.strings["ended"])

        data = self._votes[vote_id]
        voter_id = call.from_user.id
        other_type = "forgive" if vote_type == "gulag" else "gulag"

        if voter_id in data[vote_type]:
            return await call.answer(self.strings["already"])

        if voter_id in data[other_type]:
            data[other_type].discard(voter_id)
            data[vote_type].add(voter_id)
            await call.answer(self.strings["switched"])
        else:
            data[vote_type].add(voter_id)

        gulag_count, forgive_count = len(data["gulag"]), len(data["forgive"])

        if gulag_count >= self.config["votes"]:
            del self._votes[vote_id]
            await call.edit(await self._get_result_text(data["user_id"], data["name"]))
            try:
                await self._apply_punishment(data["chat_id"], data["user_id"])
            except Exception:
                pass
            return

        if forgive_count >= self.config["votes"]:
            del self._votes[vote_id]
            return await call.edit(self.strings["forgiven"].format(data["user_id"], data["name"]))

        await call.edit(text=self.strings["vote"].format(data["user_id"], data["name"]), reply_markup=self._build_markup(vote_id, gulag_count, forgive_count))