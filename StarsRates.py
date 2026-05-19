# meta developer: @AssaMods
# meta banner: https://raw.githubusercontent.com/codermasochist/AsModules/refs/heads/main/assets/fragment-stars.png
# requires: telegram-stars-rates

import asyncio, aiohttp
from .. import loader, utils
from telegram_stars_rates import get_stars_rate

@loader.tds
class StarsRates(loader.Module):
    """узнать курс тг звезд. (fragment.com)"""
    
    strings = {
        "name": "Stars Rates",
        "error": "<blockquote><emoji document_id=6050773179557745617>🫡</emoji> <b><i>ошибка получения курса... попробуйте позже.</i></b></blockquote>",
        "result": "<blockquote><emoji document_id=5951762148886582569>⭐️</emoji> <code>{stars}</code> <b>stars</b> <emoji document_id=5897692655273383739>⭐</emoji> ≈ <code>{ton:.6f}</code> <b>ton</b>  <emoji document_id=5402104393396931859>⭐️</emoji>  <code>{usdt:.2f}</code> <b>usdt</b> <emoji document_id=5814556334829343625>🪙</emoji> <code>{rub:.2f}</code> rub<emoji document_id=5231449120635370684>💸</emoji></blockquote>",
        "result_ton": "<blockquote><emoji document_id=5424912684078348533>❤️</emoji> <code>{ton}</code> <emoji document_id=5402104393396931859>⭐️</emoji> ≈ <code>{stars:.2f}</code> <b>stars</b> <emoji document_id=5897692655273383739>⭐</emoji> <code>{usdt:.2f}</code> <b>usdt</b> <emoji document_id=5814556334829343625>🪙</emoji> <code>{rub:.2f}</code> rub<emoji document_id=5231449120635370684>💸</emoji></blockquote>",
        "invalid": "<blockquote><emoji document_id=6037514847443227774>⭐️</emoji> <b><i>укажите правильное количество звёзд (число)</i></b></blockquote>",
        "invalid_ton": "<blockquote><emoji document_id=6037514847443227774>💎</emoji> <b><i>укажите правильное количество TON (число)</i></b></blockquote>",
        "loading": "<blockquote><emoji document_id=6014655953457123498>💱</emoji><b> <i>получаю курс звёзд...</i></b></blockquote>",
        "loading_ton": "<blockquote><emoji document_id=6014655953457123498>💎</emoji><b> <i>конвертирую TON в звёзды...</i></b></blockquote>"
    }
    
    async def get_ton_to_usdt(self):
        url = "https://tonapi.io/v2/rates?tokens=ton&currencies=usdt"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url) as resp:
                    data = await resp.json()
                    return data["rates"]["TON"]["prices"]["USDT"]        
        except:
            return None
            
    async def get_usdt_to_rub(self):
        url = "https://tonapi.io/v2/rates?tokens=usdt&currencies=rub"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    return data["rates"]["USDT"]["prices"]["RUB"]
        except:
            return None

    async def stars_to_all_currencies(self, amount):
        usd_to_rub = await self.get_usdt_to_rub()
        ton_to_usdt = await self.get_ton_to_usdt()
        if usd_to_rub is None or ton_to_usdt is None:
             return None
             
        result = await utils.run_sync(get_stars_rate)
        ton_per_star = result["ton_per_star"]
        
        ton = ton_per_star * amount
        usdt = ton * ton_to_usdt
        rub = usdt * usd_to_rub
        
        return {
            "stars": amount,
            "ton": ton,
            "usdt": usdt,
            "rub": rub
            }

    async def ton_to_all_currencies(self, amount_ton):
        usd_to_rub = await self.get_usdt_to_rub()
        ton_to_usdt = await self.get_ton_to_usdt()
        if usd_to_rub is None or ton_to_usdt is None:
            return None

        result = await utils.run_sync(get_stars_rate)
        ton_per_star = result["ton_per_star"]

        stars = amount_ton / ton_per_star
        usdt = amount_ton * ton_to_usdt
        rub = usdt * usd_to_rub

        return {
            "ton": amount_ton,
            "stars": stars,
            "usdt": usdt,
            "rub": rub
        }
    
    async def srcmd(self, m):
        """— <amount> stars."""
        args = utils.get_args_raw(m)
        if not args:
            await utils.answer(m, self.strings("invalid"))
            return
        try:
            amount = float(args)
        except ValueError:
            await utils.answer(m, self.strings("invalid"))
            return

        loading = await utils.answer(m, self.strings["loading"])
        converted = await self.stars_to_all_currencies(amount)
        
        if not converted:
            await utils.answer(m, self.strings("error"))
            return
            
        await utils.answer(loading, self.strings("result").format(stars=converted["stars"], ton=converted["ton"], usdt=converted["usdt"], rub=converted["rub"]))
    
    async def tsrcmd(self, m):
        """— <amount> ton. (TON to Stars)."""
        args = utils.get_args_raw(m)
        if not args:
            await utils.answer(m, self.strings("invalid_ton"))
            return
        try:
            amount = float(args)
        except ValueError:
            await utils.answer(m, self.strings("invalid_ton"))
            return

        loading = await utils.answer(m, self.strings["loading_ton"])
        converted = await self.ton_to_all_currencies(amount)
        
        if not converted:
            await utils.answer(m, self.strings("error"))
            return
            
        await utils.answer(loading, self.strings("result_ton").format(ton=converted["ton"], stars=converted["stars"], usdt=converted["usdt"], rub=converted["rub"]))
