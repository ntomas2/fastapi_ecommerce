from pydantic import EmailStr
import json
from .utils import publish_message

async def send_welcome_email(email: EmailStr, username: str):
    subject = "Добро пожаловать!"
    body = f"""
    Приветствуем, {username}!
    
    Спасибо за регистрацию в нашем сервисе.
    
    С уважением,
    Команда проекта
    """
    
    email_data = {
        "to": email,
        "subject": subject,
        "body": body
    }
    
    # Отправляем сообщение в RabbitMQ для асинхронной обработки
    await publish_message("email_queue", json.dumps(email_data))