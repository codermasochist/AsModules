#                                                  
#                                                  
#   ,---,                                          
#  '  .' \                                         
# /  ;    '.                                       
#:  :       \    .--.--.    .--.--.                
#:  |   /\   \  /  /    '  /  /    '    ,--.--.    
#|  :  ' ;.   :|  :  /`./ |  :  /`./   /       \   
#|  |  ;/  \   \  :  ;_   |  :  ;_    .--.  .-. |  
#'  :  | \  \ ,'\  \    `. \  \    `.  \__\/: . .  
#|  |  '  '--'   `----.   \ `----.   \ ," .--.; |  
#|  :  :        /  /`--'  //  /`--'  //  /  ,.  |  
#|  | ,'       '--'.     /'--'.     /;  :   .'   \ 
#`--''           `--'---'   `--'---' |  ,     .-./ 
#                                     `--`---'     
#                                                  
# meta developer: @AssaMods

from .. import loader, utils
import asyncio
from herokutl.tl.functions.payments import GetSavedStarGiftsRequest, SaveStarGiftRequest
from herokutl.tl.types import SavedStarGift, StarGiftUnique, StarGift, InputSavedStarGiftUser

@loader.tds
class GiftsVisibility(loader.Module):
    """Hidden & Shows Gifts.
    -l лимитированные
    -g обычные
    -n уникальные (NFT)
    без аргументов — все"""
    
    strings = {
        "name": "GiftsVisibility",
        "loading": "<blockquote><emoji document_id=5382178536872223059>💫</emoji> <b>получаю подарки...</b></blockquote>",
        "no_gifts": "<blockquote><emoji document_id=5334667445435120027>☹️</emoji>  <b>У вас нет подарков</b>.</blockquote>",
        "processing": "<blockquote><emoji document_id=5382178536872223059>💫</emoji> <b>обрабатываю </b><code>{}</code><b> подарков...</b></blockquote>",
        "done_hidden": "<blockquote><emoji document_id=5332533929020761310>✅</emoji> <b>скрыто </b><code>{}</code><b> подарков.</b></blockquote>",
        "done_shown": "<blockquote><emoji document_id=5893224751119208859>✅</emoji> <b>показано </b><code>{}</code><b> подарков.</b></blockquote>",
        "errors": "<blockquote><emoji document_id=5253864872780769235>❗️</emoji> <b>ошибка при обработке подарков:</b> {}</blockquote>",
        "no_selection": "<blockquote><emoji document_id=5334667445435120027>☹️</emoji> <b>нет подходящих подарков для выбранных флагов.</b></blockquote>"
    }

    async def _fetch_all_saved(self):
        first = await self.client(GetSavedStarGiftsRequest(peer="me", offset="", limit=100))
        gifts = list(first.gifts) if getattr(first, "gifts", None) else []
        total = getattr(first, "count", len(gifts))
        if total > len(gifts):
            pages = (total + 99) // 100
            for i in range(1, pages):
                next_page = await self.client(GetSavedStarGiftsRequest(peer="me", offset=str(100 * i).encode(), limit=100))
                gifts.extend(next_page.gifts)
        return gifts

    async def _process(self, message, unsave: bool):
        args = utils.get_args_raw(message).lower()
        nft, gifts, limited = False, False, False
        if "-nft" in args or "-n" in args: args = args.replace("-nft", "").replace("-n", ""); nft = True
        if "-gifts" in args or "-g" in args: args = args.replace("-gifts", "").replace("-g", ""); gifts = True
        if "-limited" in args or "-l" in args: args = args.replace("-limited", "").replace("-l", ""); limited = True
        await utils.answer(message, self.strings["loading"])
        gifts_list = await self._fetch_all_saved()
        if not gifts_list:
            await utils.answer(message, self.strings["no_gifts"])
            return
        candidates = []
        for gift in gifts_list:
            if not isinstance(gift, SavedStarGift) or not gift.msg_id:
                continue
            is_unique = isinstance(gift.gift, StarGiftUnique)
            is_star = isinstance(gift.gift, StarGift)
            is_limited = getattr(gift.gift, "limited", False) if is_star else False
            if not (nft or gifts or limited):
                candidates.append(gift)
            elif (is_unique and nft) or (is_star and is_limited and limited) or (is_star and not is_limited and gifts):
                candidates.append(gift)
        if not candidates:
            await utils.answer(message, self.strings["no_selection"])
            return
        await utils.answer(message, self.strings["processing"].format(len(candidates)))
        processed, errors = 0, 0
        for g in candidates:
            try:
                await self.client(SaveStarGiftRequest(stargift=InputSavedStarGiftUser(msg_id=g.msg_id), unsave=unsave))
                processed += 1
                await asyncio.sleep(0.15)
            except:
                errors += 1
                await asyncio.sleep(0.2)
        result = self.strings["done_hidden"].format(processed) if unsave else self.strings["done_shown"].format(processed)
        if errors:
            result += "\n" + self.strings["errors"].format(errors)
        await utils.answer(message, result)

    @loader.command()
    async def hgifts(self, message):
        """— [-l | -g | -n ] скрыть подарки."""
        await self._process(message, True)

    @loader.command()
    async def sgifts(self, message):
        """[ -l |-g |-n ] показать подарки."""
        await self._process(message, False)
