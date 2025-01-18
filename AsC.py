# meta developer: @codermasochist

from .. import loader, utils

@loader.tds
class AsCode(loader.Module):
    """сохраняет текст в файл и читает содержимое файлов. by @codermasochist"""
    
    strings = {
        "name": "AsC",
    }
    
    async def sfcmd(self, message):
        """
        — сохраняет в файл.
        """
        args = utils.get_args_raw(message)
        
        reply = await message.get_reply_message()
        if not reply:
            return await message.reply("<emoji document_id=6327816922544997828>💀</emoji> бро, надо реплай на соо...")
        
        code_text = reply.message
        
        file_name = args if args else "code.txt"
        
        with open(file_name, "w") as f:
            f.write(code_text)
        
        await self.client.send_file(message.peer_id, file_name)

    async def rfcmd(self, message):
        """
        — достает содержимое файла.
        """
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            return await message.reply("<emoji document_id=6327816922544997828>💀</emoji> бро, надо реплай на файл...")
        
        file = await reply.download_media()
        
        with open(file, "r") as f:
            file_content = f.read()

        formatted_content = file_content
        
        max_length = 4096
        total_length = len(formatted_content)

        for i in range(0, total_length, max_length):
            part = formatted_content[i:i + max_length]
            await message.reply(f"```\n{part}\n```", parse_mode="markdown")
