
from aiogram import Bot
from app.settings.base import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)


async def info(data):    
    try:
        user_id = data['message']['from']['id']
        text =f'По любым вопросам обращайтесь в поддержку @VVOSKVI4'
        await bot.send_message(user_id, text)
    finally:
        await bot.session.close()