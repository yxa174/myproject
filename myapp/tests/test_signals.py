from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from unittest.mock import patch, MagicMock
from myapp.models import Subscriber
from myapp import signals

class TelegramSignalsTests(TestCase):
    def setUp(self):
        # Создаем тестового админа
        self.admin = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            is_staff=True
        )
        
        # Создаем тестового подписчика (chat_id как строка)
        self.subscriber = Subscriber.objects.create(
            chat_id='123456',
            username='test_subscriber'
        )

    @patch('myapp.signals.send_telegram_message')
    def test_admin_login_handler(self, mock_send):
        """Тест отправки уведомления при входе админа"""
        # Создаем фейковый request
        request = MagicMock()
        request.user = self.admin
        
        # Вызываем сигнал вручную
        signals.admin_login_handler(
            sender=self.__class__,
            request=request,
            user=self.admin
        )
        
        # Проверяем что send_telegram_message вызвался
        self.assertTrue(mock_send.called)
        
        # Проверяем аргументы вызова
        called_args = mock_send.call_args[0]
        
        # Проверяем chat_id (как строку)
        self.assertEqual(str(called_args[0]), '123456')

        
        # Проверяем содержимое сообщения
        message = called_args[1]
        self.assertIn('Админ вошёл в систему', message)
        self.assertIn(self.admin.username, message)

    @patch('myapp.signals.send_telegram_message')
    def test_non_admin_login(self, mock_send):
        """Тест что уведомление не отправляется для не-админов"""
        regular_user = User.objects.create_user(
            username='regular',
            password='testpass123',
            is_staff=False
        )
        request = MagicMock()
        request.user = regular_user
        
        signals.admin_login_handler(
            sender=self.__class__,
            request=request,
            user=regular_user
        )
        
        self.assertFalse(mock_send.called)

    @patch('myapp.signals.httpx.post')
    def test_send_telegram_message_success(self, mock_post):
        """Тест успешной отправки сообщения"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        signals.send_telegram_message('123456', 'Test message')
        
        self.assertTrue(mock_post.called)
        mock_post.assert_called_once()

    @patch('myapp.signals.httpx.post')
    @patch('myapp.signals.logger.error')
    def test_send_telegram_message_failure(self, mock_logger, mock_post):
        """Тест обработки ошибки при отправке"""
        mock_post.side_effect = Exception("Test error")
        
        signals.send_telegram_message('123456', 'Test message')
        
        mock_logger.assert_called_with("Неизвестная ошибка: Test error")
