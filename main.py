from fastapi import FastAPI, Depends , HTTPException 
from pydantic import BaseModel
from typing import List
from app.services.redis_service import RedisService
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pika
import json
import asyncio
from datetime import datetime
from app.services.email_service import EmailService
from app.core.config import settings
from app.model.email_db import create_db_and_tables, get_record_by_id, update_record_by_id
from app.model.email_db import EmailCreate , get_email
from app.api.deps import get_rabbitmq_service
from app.services.scheduler_service import check_records_and_publish

app = FastAPI()


# Dependency to get the Redis service
def get_redis_service():
    return RedisService()

@app.post("/emails/", response_model=str)
def create_email(email: EmailCreate, redis_service: RedisService = Depends(get_redis_service)):
    email_id = redis_service.save_email(email)
    return email_id
@app.get("/:email_id", response_model=EmailCreate)
def get_email_status(email_id: str):
    email = get_email(email_id)
    return email

@app.get("/emails/pending", response_model=List[dict])
def get_pending_emails(redis_service: RedisService = Depends(get_redis_service)):
    pending_emails = redis_service.get_pending_emails()
    return pending_emails
@app.get("/id:id")
def get_email_record(id:int):
    return update_record_by_id(id)

# @app.exception_handler()

def test():
    try:    
        raise HTTPException(status_code=404, detail="Item not found")
    except HTTPException as e:
        print("error")
        raise HTTPException(status_code=404, detail="Item not found")

# Models for request bodies
class EmailUpdate(BaseModel):
    status: str


# Scheduler setup
scheduler = AsyncIOScheduler()
scheduler.add_job(check_records_and_publish, 'interval', minutes=.1)
scheduler.start()

# Ensure the scheduler is shut down properly when the application exits
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    

@app.on_event("startup")
def startup_event():
    create_db_and_tables()
    connection = get_rabbitmq_service()
    connection.connect()

# async def main():
#     worker = EmailWorker(
#         RabbitMQService(settings.RABBITMQ_URL),
#         RedisService(settings.REDIS_URL),
#         EmailService()
#     )
#     await worker.start()

