# meta developer: @codermasochist

from .. import loader, utils
from telethon.tl.functions.photos import UploadProfilePhotoRequest

@loader.tds
class SetAva(loader.Module):
    """set avatar. by @codermasochist."""

    strings = {"name": "set ava"}

    async def avascmd(self, message):
        """— ответом на медиа/гиф"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            return await utils.answer(message, "<blockquote><emoji document_id=5471909397347191760>🐱</emoji> ответьте на фото или гиф. ^‿^</blockquote>")

        media = await self.client.upload_file(await message.client.download_media(reply.media))
        if not media:
            return await utils.answer(message, "<blockquote><emoji document_id=5471877459970379952>😺</emoji> не смогла установить аву, извините хозяин. >_</blockquote>")

        await self.client(UploadProfilePhotoRequest(file=media))
        await utils.answer(message, "<blockquote><emoji document_id=5377809374016192785>🔝</emoji> я установила вашу новую аватарку, хозяин! \^o^/</blockquote>")
