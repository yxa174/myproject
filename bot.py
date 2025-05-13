import os
import django
from telegram.ext import Application, CommandHandler
from telegram import Update
from asgiref.sync import sync_to_async
from myapp.option import token
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Subscriber
TOKEN = token

@sync_to_async
def add_subscriber(chat_id, username):
    Subscriber.objects.get_or_create(chat_id=chat_id, defaults={'username': username})

async def start(update: Update, context):
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    await add_subscriber(chat_id, username)
    await update.message.reply_text("✅ Вы подписались на уведомления!")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
