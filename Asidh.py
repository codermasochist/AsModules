# meta developer: @codermasochist

from telethon import events
from .. import loader, utils

@loader.tds
class AsidhMod(loader.Module):
    """Приветствие с ID. by @codermasochist"""

    strings = {"name": "As welcome ID"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

        @self.client.on(events.ChatAction(func=lambda e: e.user_joined or e.user_added))
        async def handler(event):
            user = await event.get_user()
            chat = await event.get_chat()
            welcome_chat_id = self.db.get(self.strings["name"], "welcome_chat_id")

            if chat.id == welcome_chat_id:
                await self.client.send_message(
                    chat,
                    f"<b><emoji document_id=5454390891466726015>👋</emoji> Добро пожаловать, {utils.escape_html(user.first_name)}!</b>\n"
                    f"<b><emoji document_id=5936017305585586269>🪪</emoji> Ваш ID:</b> <code>{user.id}</code>"
                )

    @loader.command()
    async def onidcmd(self, message):
        """— включает приветствие с ID."""
        chat_id = utils.get_chat_id(message)
        current_status = self.db.get(self.strings["name"], "welcome_chat_id", None)

        if current_status == chat_id:
            await message.respond("<b><emoji document_id=4918354603281482671>👋</emoji> Приветствие с ID включено.</b>")
        else:
            self.db.set(self.strings["name"], "welcome_chat_id", chat_id)
            await message.respond("<b><emoji document_id=4918354603281482671>👋</emoji> Приветствие с ID включено.</b>")

    @loader.command()
    async def offidcmd(self, message):
        """— отключает приветствие с ID"""
        chat_id = utils.get_chat_id(message)
        current_status = self.db.get(self.strings["name"], "welcome_chat_id", None)

        if current_status is None:
            await message.respond("<b><emoji document_id=5465665476971471368>❌</emoji> Приветствие не было включено.</b>")
        else:
            self.db.set(self.strings["name"], "welcome_chat_id", None)
            await message.respond("<b><emoji document_id=5877477244938489129>🚫</emoji> Приветствие с ID отключено!</b>")
