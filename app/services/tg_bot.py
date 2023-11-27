import aiohttp

from config import load_config

config = load_config(".env")
token = config.tg_bot.bot_token
admin = config.tg_bot.admins


async def send_message(receiver: str | int, text: str):
    params = dict(chat_id=receiver, text=text, parse_mode="HTML", disable_web_page_preview="true")
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.telegram.org/bot{token}/sendMessage', params=params) as resp:
            print(resp)
            return resp.status

