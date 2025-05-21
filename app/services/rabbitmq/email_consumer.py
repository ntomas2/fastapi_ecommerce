import aio_pika
import json
from email.message import EmailMessage
import smtplib
from settings import EMAIL_FROM, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, RABBITMQ_URL



async def consume_email_queue():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("email_queue", durable=True)
    
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    email_data = json.loads(message.body.decode())
                    await send_email(
                        email_data["to"],
                        email_data["subject"],
                        email_data["body"]
                    )
                except Exception as e:
                    print(f"Ошибка при обработке email: {e}")

async def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to
    
    try:
        with smtplib.SMTP(
            host=SMTP_HOST,
            port=int(SMTP_PORT)
        ) as server:
            server.starttls()
            server.login(
                SMTP_USER,
                SMTP_PASSWORD
            )
            server.send_message(msg)
        print(f"Email отправлен на {to}")
    except Exception as e:
        print(f"Ошибка отправки email: {e}")