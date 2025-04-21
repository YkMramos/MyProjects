

import asyncio
from aiogram import Bot
import logging
from app.settings.base import WEBHOOK_URL, BOT_TOKEN
# from myapp.settings.local import WEBHOOK_URL, BOT_TOKEN





logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TOKEN = BOT_TOKEN


"""export DJANGO_SETTINGS_MODULE=myproject.settings - выполни перед установкой хука"""



async def setup_webhook():
    bot = Bot(token=TOKEN)
    try:
        # Сначала удалим текущий webhook
        await bot.delete_webhook() 
        logger.info("Старый webhook удален")
        
        # Установим новый webhook с расширенными параметрами
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True,  # Игнорировать обновления, накопившиеся за время неактивности
            allowed_updates=['message', 'callback_query'],  # Типы обновлений, которые мы хотим получать
        )
        logger.info(f"Webhook установлен на {WEBHOOK_URL}")
        
        # Проверим информацию о webhook
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Webhook информация: {webhook_info}")
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()



if __name__ == '__main__':
    asyncio.run(setup_webhook())