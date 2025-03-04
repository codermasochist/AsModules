# meta developer: @codermasochist

from asyncio import sleep
import re
from .. import loader, utils

@loader.tds
class Asdistributor(loader.Module):
    """Рассылка в чат. by @codermasochist"""

    strings = {
        "name": "As distributor"
    }

    def __init__(self):
        self.running = False
        self.interval = 600
        self.chat_ids = set()

    def parse_time(self, time_str):
        match = re.match(r"(\d+)([smh])", time_str)
        if not match:
            return None
        value, unit = int(match.group(1)), match.group(2)
        if unit == "s":
            return value
        elif unit == "m":
            return value * 60
        elif unit == "h":
            return value * 60 * 60
        return None

    async def send_or_edit(self, message, text):
        owner = await self._client.get_me()
        owner_ids = owner.id
        if message.sender_id == owner_ids:
            await message.edit(text)
        else:
            await message.respond(text)

    @loader.command()
    async def sitcmd(self, message):
        """— 1s, 1m, 1h"""
        args = utils.get_args_raw(message)
        if not args:
            await self.send_or_edit(message, "<emoji document_id=5877477244938489129>🚫</emoji><b> неверный формат. используйте: 1s, 1m, 1h.</b>")
            return
        interval = self.parse_time(args)
        if interval is None:
            await self.send_or_edit(message, "<emoji document_id=5877477244938489129>🚫</emoji><b> неверный формат. используйте: 1s, 1m, 1h.</b>")
            return
        self.interval = interval
        await self.send_or_edit(message, f"<emoji document_id=5123230779593196220>⏰</emoji> <b>интервал рассылки установлен на</b> {args}")

    @loader.command()
    async def dobrcmd(self, message):
        """— ид чата"""
        args = utils.get_args_raw(message)
        if not args:
            await self.send_or_edit(message, "❗ Укажите  ид чатов через пробел.")
            return

        try:
            chat_ids = {int(chat_id) for chat_id in args.split()}
            self.chat_ids.update(chat_ids)
            await self.send_or_edit(message, f"✅ Добавлено чатов: {len(chat_ids)}. Всего чатов: {len(self.chat_ids)}.")
        except ValueError:
            await self.send_or_edit(message, "❗ Убедитесь, что указаны только числовые ID чатов.")

    @loader.command()
    async def delccmd(self, message):
        """— ид чата"""
        args = utils.get_args_raw(message)
        if not args:
            await self.send_or_edit(message, "❗ Укажите ID чатов для удаления.")
            return

        try:
            chat_ids = {int(chat_id) for chat_id in args.split()}
            self.chat_ids.difference_update(chat_ids)
            await self.send_or_edit(message, f"✅ Удалено чатов: {len(chat_ids)}. Осталось чатов: {len(self.chat_ids)}.")
        except ValueError:
            await self.send_or_edit(message, "❗ Убедитесь, что указаны только числовые ID чатов.")

    @loader.command()
    async def listrcmd(self, message):
        """— показывает список"""
        if not self.chat_ids:
            await self.send_or_edit(message, "❗ Список чатов пуст.")
            return
        chat_list = "\n".join(str(chat_id) for chat_id in self.chat_ids)
        await self.send_or_edit(message, f"<emoji document_id=5956561916573782596>📄</emoji> <b>список чатов</b>:\n{chat_list}")

    @loader.command()
    async def rslcmd(self, message):
        """— <текст или реплай на соо>"""
        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        chat_id = message.chat_id
        
        try:
            count = 999999
            self.running = True

            if reply:
                mess = reply

                await message.delete()
                await reply.delete()

                for _ in range(count):
                    if not self.running:
                        break
                    mess = await self.client.send_message(chat_id, mess)
                    await sleep(self.interval)

            else:
                mess = args

                await message.delete()

                if message.media:
                    for _ in range(count):
                        if not self.running:
                            break
                        message = await self.client.send_file(chat_id, message.media, caption=mess)
                        await sleep(self.interval)
                else:
                    for _ in range(count):
                        if not self.running:
                            break
                        await self.client.send_message(chat_id, mess)
                        await sleep(self.interval)

        except Exception as e:
            await self.send_or_edit(message, f"⚠ Ошибка: {e}")

    @loader.command()
    async def orslcmd(self, message):
        """— <реплай> """
        reply = await message.get_reply_message()
        if not reply:
            await self.send_or_edit(message, "<emoji document_id=5384233476859896660>😳</emoji> <b>Реплайни на сообщение, которое хочешь рассылать в режиме оригинал.</b>")
            return

        self.running = True
        await self.send_or_edit(message, "<emoji document_id=5256182535917940722>⤵️</emoji> <b>Рассылка запущена в режиме оригинал.</b>")
        try:
            while self.running:
                await reply.forward_to(message.chat_id)
                await sleep(self.interval)
        except Exception as e:
            await self.send_or_edit(message, f"<emoji document_id=5440660757194744323>‼️</emoji> Ошибка: {e}")

    @loader.command()
    async def startrcmd(self, message):
        """— <текст или реплай>."""
        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)

        if not self.chat_ids:
            await self.send_or_edit(message, "<emoji document_id=5879813604068298387>❗️</emoji> список чатов пуст.")
            return

        if not args and not reply:
            await self.send_or_edit(message, "<emoji document_id=5420323339723881652>⚠️</emoji> <b>укажи текст или реплай на соо.</b>")
            return

        content = reply or args
        self.running = True
        await self.send_or_edit(message, "<emoji document_id=5256182535917940722>⤵️</emoji> <b>distributor startled</b>.")
        
        try:
            while self.running:
                for chat_id in self.chat_ids:
                    if not self.running:
                        break

                    try:
                        if reply:
                            await reply.forward_to(chat_id)
                        else:
                            await self.client.send_message(chat_id, content)
                        await sleep(self.interval)
                    except Exception as e:
                        print(f"Ошибка при отправке в чат {chat_id}: {e}")
        except Exception as e:
            await self.send_or_edit(message, f"⚠ Ошибка: {e}")

    @loader.command()
    async def stoprcmd(self, message):
        """— стоп рассылки."""
        self.running = False
        await self.send_or_edit(message, "<emoji document_id=5319090522470495400>⭕️</emoji> <b>distributor stopped.</b>")
