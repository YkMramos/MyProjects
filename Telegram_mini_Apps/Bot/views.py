from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

import logging
import json

from .command.start import start
from .command.info import info

from app.settings.base import BOT_TOKEN




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




@csrf_exempt
async def webhook_handler(request):
    logger.info(f"Получен {request.method} запрос")
    logger.info(f"Headers: {request.headers}")
    
    if request.method == 'POST':
        try:
            logger.info(f"Raw body: {request.body.decode()}")
            data = json.loads(request.body.decode('utf-8'))

            
            logger.info(f"Получен webhook: {data}")
            if data['message']['text'] == '/start':
                await start(data)
            else:
                await info(data)
          
            return HttpResponse('ok')
        
        except Exception as e:
            logger.error(f"Ошибка обработки webhook: {e}", exc_info=True)
            return HttpResponse(str(e), status=500)
    else:
        return JsonResponse({
            'status': 'webhook active',
            'method': request.method
        })
    