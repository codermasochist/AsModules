# meta developer: @codermasochist

from .. import loader, utils

@loader.tds
class AsID(loader.Module):
    """
    получает ID по реплаю. by @codermasochist
    """
    strings = {"name": "AsID"}

    async def идcmd(self, message):
        """
        — работает без префа, просто "ид".
        """
        reply = await message.get_reply_message()
        args = utils.get_args(message)

        if not reply:
            if not args:
                user = await message.client.get_entity(message.sender_id)
                link = '<a href="t.me/{}">{}</a>'.format(user.username, user.first_name) if user.username else '<a href="tg://openmessage?user_id={}">{}</a>'.format(user.id, user.first_name)
                return await message.reply(
                    f"<emoji document_id=5780683340810030158>✈️</emoji> {link}\n"
                    f"<emoji document_id=4918133202012340741>👤</emoji> <code>@{user.id}</code>"
                )
            user = await message.client.get_entity(args[0])
            link = '<a href="t.me/{}">{}</a>'.format(user.username, user.first_name) if user.username else '<a href="tg://openmessage?user_id={}">{}</a>'.format(user.id, user.first_name)
            return await message.reply(
                f"<emoji document_id=5780683340810030158>✈️</emoji> {link}\n"
                f"<emoji document_id=4918133202012340741>👤</emoji> <code>{user.id}</code>"
            )

        user = await message.client.get_entity(reply.sender_id)
        link = '<a href="t.me/{}">{}</a>'.format(user.username, user.first_name) if user.username else '<a href="tg://openmessage?user_id={}">{}</a>'.format(user.id, user.first_name)
        return await message.reply(
            f"<emoji document_id=5780683340810030158>✈️</emoji> {link}\n"
            f"<emoji document_id=4918133202012340741>👤</emoji> <code>{user.id}</code>"
        )

    async def watcher(self, message):
        """
        ну тут пон
        """
        if message.sender_id != (await message.client.get_me()).id:
            return

        text = message.raw_text.strip().lower()

        if text == "ид":
            reply = await message.get_reply_message()
            if not reply:
                user = await message.client.get_entity(message.sender_id)
                link = '<a href="t.me/{}">{}</a>'.format(user.username, user.first_name) if user.username else '<a href="tg://openmessage?user_id={}">{}</a>'.format(user.id, user.first_name)
                return await message.reply(
                    f"<emoji document_id=5780683340810030158>✈️</emoji> {link}\n"
                    f"<emoji document_id=4918133202012340741>👤</emoji> <code>{user.id}</code>"
                )

            user = await message.client.get_entity(reply.sender_id)
            link = '<a href="t.me/{}">{}</a>'.format(user.username, user.first_name) if user.username else '<a href="tg://openmessage?user_id={}">{}</a>'.format(user.id, user.first_name)
            return await message.reply(
                f"<emoji document_id=5780683340810030158>✈️</emoji> {link}\n"
                f"<emoji document_id=4918133202012340741>👤</emoji> <code>{user.id}</code>"
            )
