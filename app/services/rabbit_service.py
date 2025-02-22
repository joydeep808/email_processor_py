import json
import aio_pika
import pika
from typing import Dict

class RabbitMQService:
    def __init__(self, rabbitmq_url: str):
        self.url = rabbitmq_url
        self.connection = None
        self.channel = None
        self.queue_name = "email_queue"

    async def connect(self):
        if not self.connection:
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            await self.channel.declare_queue(
                self.queue_name,
                durable=True
            )
    


    async def publish_email(self, email_data: Dict):
        await self.connect()
        if self.channel is None:
            raise RuntimeError("Channel is not initialized")
        message = aio_pika.Message(
            body=json.dumps(email_data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.channel.default_exchange.publish(
            message,
            routing_key=self.queue_name
        )

    async def process_emails(self, callback):
        await self.connect()
        if self.channel is None:
            raise RuntimeError("Channel is not initialized")
        queue = await self.channel.declare_queue(self.queue_name, durable=True)
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await callback(json.loads(message.body.decode()))