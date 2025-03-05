import asyncio
import json
import pika 
from app.services.email_service import EmailService
from app.model.email_db import update_record_by_id
def process_email(ch, method, _, body):
    email = json.loads(body)
    print(f"Processing email: {email['recipient']}")
    update_record_by_id(email["id"].split(":")[1],)
    EmailService().send_email(email)
    
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)





class RabbitMQService:
    def __init__(self, rabbitmq_url: str , queue:str) :
        self.url = rabbitmq_url
        self.connection = None
        self.channel = None
        self.queue_name = queue

    def connect(self):
        if not self.connection:
            connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
            self.connection = connection
            channel = connection.channel()
            self.channel = channel
            channel.queue_declare(
                self.queue_name,
                durable=True
            )
            asyncio.run_coroutine_threadsafe(self.start_listner(), asyncio.get_event_loop()) # type: ignore

    def publish_message(self , message:str):    
        self.channel.basic_publish( # type: ignore
            exchange='',
            routing_key=self.queue_name,
            body=message
        )
    # It will consume the messages from the queue
    # def get_messages(self):
         # type: ignore

    def start_listner(self):
        if self.channel:
            self.channel.basic_consume( # type: ignore
            queue=self.queue_name,
            on_message_callback=process_email,
            auto_ack=True
        )
        self.channel.start_consuming() # type: ignore

    def close(self):
        if self.connection:
            self.connection.close()
    
