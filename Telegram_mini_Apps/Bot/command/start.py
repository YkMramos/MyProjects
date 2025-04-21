from aiogram import Bot
from app.settings.base import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)



async def start(data):
    try:
        user_id = data['message']['from']['id']
        text = f'Привет! Я бот интернет магазина Bobproject, чтобы перейти в каталог магазина нажмите на кнопку Menu.'
        text += 'Для связи с администрацией по любым вопросам обращайтесь @VVOSKVI4'
        await bot.send_message(user_id, text)
    finally:
        await bot.session.close()


