from django.db import models

class Subscriber(models.Model):
    chat_id = models.BigIntegerField(unique=True)  # ID чата в Telegram
    username = models.CharField(max_length=100, blank=True, null=True)  # Опционально: имя пользователя
    subscribed_at = models.DateTimeField(auto_now_add=True)  # Дата подписки

    def __str__(self):
        return f"{self.chat_id} ({self.username})"
