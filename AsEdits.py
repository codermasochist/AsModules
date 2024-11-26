#meta developer: @codermasochist

import random
from telethon.tl.types import InputMessagesFilterVideo, Message
from telethon.errors import RPCError, FileReferenceExpiredError
from .. import loader, utils

@loader.tds
class AsEditsMod(loader.Module):
    """Модуль кидает ахуенные эдиты. by @codermasochist"""

    strings = {
        "name": "AsEdits",
        "choosi_video": "<emoji document_id=5328311576736833844>🔴</emoji> Ловим топовый эдит...",
        "no_channel": "<b>Канал не указан, укажи его в конфиге.</b>",
        "no_videos_found": "<b>Здесь пусто.</b>",
        "selected_edit": "подобрал эдит"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "change_channel",
                None,
                doc=lambda: "Вбей сюда юзер канала, откуда будет тащить эдиты",
            ),
        )
        self.video_queue = []

    async def update_video_queue(self, channel: str):
        self.video_queue = [
            msg.id async for msg in self.client.iter_messages(
                channel,
                limit=5000,
                filter=InputMessagesFilterVideo,
            )
        ]

    async def get_next_video(self, channel: str):
        if not self.video_queue:
            await self.update_video_queue(channel)
        
        if not self.video_queue:
            return None
        
        video_id = random.choice(self.video_queue)
        self.video_queue.remove(video_id)
        return await self.client.get_messages(channel, ids=video_id)

    async def send_video(self, message: Message, channel: str):
        status_message = await utils.answer(message, self.strings["choosi_video"])

        try:
            video_message = await self.get_next_video(channel)

            if not video_message:
                await utils.answer(message, self.strings["no_videos_found"])
                return

            reply = await message.get_reply_message()
            reply_id = reply.id if reply else None

            try:
                await utils.answer_file(
                    message,
                    video_message,
                    video_message.text or self.strings["selected_edit"],
                    reply_to=reply_id,
                )
            except FileReferenceExpiredError:
                await self.update_video_queue(channel)
                video_message = await self.get_next_video(channel)
                if video_message:
                    await utils.answer_file(
                        message,
                        video_message,
                        video_message.text or self.strings["selected_edit"],
                        reply_to=reply_id,
                    )
                else:
                    await utils.answer(message, self.strings["no_videos_found"])

            if message.out:
                await message.delete()

            await status_message.delete()

        except RPCError as e:
            await utils.answer(message, str(e))
        except Exception:
            await utils.answer(message, self.strings["no_videos_found"])
            await status_message.delete()

    @loader.command()
    async def asedit(self, message: Message):
        """кидает эдиты с канала разработчика. @makimalove"""
        await self.send_video(message, "makimalove")

    @loader.command()
    async def edit(self, message: Message):
        """кидает рандомный эдит с канала, указанного в конфиге."""
        change_channel = self.config["change_channel"]

        if not change_channel:
            await utils.answer(message, self.strings["no_channel"])
            return

        await self.send_video(message, change_channel)
