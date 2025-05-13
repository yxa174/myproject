from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from myapp.models import Subscriber
from django.utils.timezone import localtime
from django.utils.timezone import now
from django.utils.dateformat import format
from myapp.option import token
import httpx
import logging

logger = logging.getLogger(__name__)
TELEGRAM_TOKEN = token

def send_telegram_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        response = httpx.post(url, data=data, timeout=10)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка Telegram API: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")

@receiver(user_logged_in)
def admin_login_handler(sender, request, user, **kwargs):
    if user.is_staff:
        subscribers = Subscriber.objects.all()
        current_time = localtime(now()).strftime('%d.%m.%Y %H:%M:%S')  # 25.12.2023 14:30:45
        message = (
            f"🔔 Админ вошёл в систему!\n"
            f"👤 Логин: {user.username}\n"
            f"🕒 Время: {current_time}"
        )
        for sub in subscribers:
            send_telegram_message(sub.chat_id, message)
