from app.workers.email_worker import EmailWorker
from app.services.rabbit_service import RabbitMQService
from app.core.config import settings
from app.services.redis_service import RedisService
from app.services.email_service import EmailService
import asyncio
import emails
import json
import pika
from typing import Dict

def send_email(email_data: Dict) -> bool:
        smtp = {
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
            "user": "Joydeep Debnath",
            "password": settings.SMTP_PASSWORD,
            "tls": True
        }
        message = emails.Message(
            subject=email_data["subject"],
            html=email_data["body"],
            mail_from=settings.SMTP_FROM_EMAIL
        )

        response = message.send(
            to=email_data["recipient"],
            smtp=smtp
        )

        return response.status_code == 250

def process_email(ch, method, properties, body):
    email = json.loads(body)
    print(f"Processing email: {email['recipient']}")
    send_email(email)
    
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_listener():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='email_service')

    channel.basic_consume(queue='email_service', on_message_callback=process_email)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == 'rabbit_listener':
    start_listener()