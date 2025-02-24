from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
from app.services.redis_service import RedisService

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pika
import json
import asyncio
from datetime import datetime
from app.workers.email_worker import EmailWorker
from app.services.rabbit_service import RabbitMQService
from app.services.email_service import EmailService
from app.core.config import settings
from app.core.rabbit_listner import start_listener
from app.model.item import create_db_and_tables
from app.model.item import EmailCreate , get_email

app = FastAPI()

# Dependency to get the Redis service
def get_redis_service():
    return RedisService(redis_url="redis://localhost:6379")

@app.post("/emails/", response_model=str)
def create_email(email: EmailCreate, redis_service: RedisService = Depends(get_redis_service)):
    email_id = redis_service.save_email(email)
    return email_id
@app.get("/")
def get_email_status(email_id: int):
    email = get_email(email_id)
    return email


@app.get("/emails/pending", response_model=List[dict])
async def get_pending_emails(redis_service: RedisService = Depends(get_redis_service)):
    pending_emails = await redis_service.get_pending_emails()
    return pending_emails

# Models for request bodies
class EmailUpdate(BaseModel):
    status: str

# Function to process pending emails
async def process_pending_emails():
    redis_service = get_redis_service()
    pending_emails = await redis_service.get_pending_emails()
    
    # RabbitMQ connection setup
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='email_service')

    for email in pending_emails:
        # Add your email processing logic here
        print(f"Processing email: {email['recipient']}")
        
        # Convert datetime fields to timestamps
        email['created_at'] = int(email['created_at'].timestamp())
        if 'sent_at' in email and email['sent_at']:
            email['sent_at'] = int(email['sent_at'].timestamp())
        
        # Publish message to RabbitMQ
        channel.basic_publish(
            exchange='',
            routing_key='email_service',
            body=json.dumps(email)
        )
        
        redis_service.redis.delete(f"email:{email['id']}")
    
    connection.close()

# Scheduler setup
scheduler = AsyncIOScheduler()
scheduler.add_job(process_pending_emails, 'interval', minutes=.2)
scheduler.start()

# Ensure the scheduler is shut down properly when the application exits
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


@app.on_event("startup")
def startup_event():
    create_db_and_tables()



# async def main():
#     worker = EmailWorker(
#         RabbitMQService(settings.RABBITMQ_URL),
#         RedisService(settings.REDIS_URL),
#         EmailService()
#     )
#     await worker.start()


# if __name__ == "main":
#     start_listener()