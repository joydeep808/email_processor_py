
from fastapi import APIRouter, Depends, HTTPException
from app.services.redis_service import RedisService
from app.services.rabbit_service import RabbitMQService
from typing import List
from app.model.email import EmailCreate, EmailResponse

router = APIRouter()

@router.post("/email/", response_model=EmailResponse)
async def create_email(
    email: EmailCreate,
    redis_service: RedisService = Depends(),
    rabbit_service: RabbitMQService = Depends()
):
    # Save to Redis
    email_id = int(redis_service.save_email(email))
    
    # Publish to RabbitMQ
    await rabbit_service.publish_email({
        "id": email_id,
        **email.dict()
    })
    
    # return EmailResponse(id=email_id, **email.dict())

@router.get("/emails/", response_model=List[EmailResponse])
async def get_pending_emails(
    redis_service: RedisService = Depends()
):
    return redis_service.get_pending_emails()