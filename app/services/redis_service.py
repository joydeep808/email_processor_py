import json
from datetime import datetime
import redis
# from app.model.email import EmailCreate
from app.model.email_db import EmailCreate, get_email, save_email_in_db, SessionDep
from  uuid import uuid4 
from app.core.config import settings

class RedisService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def save_email(self, email: EmailCreate) -> str:
        email_dict = email.model_dump()
        email_dict["created_at"] = datetime.utcnow().timestamp()
        # Generate UUID and use it as the key
        saved_data = save_email_in_db(email)
        # Store the UUID in the hash
        redis_key =f"email:{saved_data.id}"
        email_dict["id"] = redis_key
        self.redis.hset(redis_key, mapping=email_dict)
        return redis_key

    def get_pending_emails(self):
        keys = self.redis.keys("email:*")
        if not keys:
            return []
        pipeline = self.redis.pipeline()
        for key in keys: # type: ignore
            pipeline.hgetall(key)
            
        
        pending_emails = []
        emails_data =  pipeline.execute()
        for email_data in emails_data:
            # Convert timestamps back to datetime
                email_data["created_at"] = datetime.fromtimestamp(float(email_data["created_at"]))
                pending_emails.append(email_data)
        for k in keys: # type: ignore
            self.delete_email(k)
        return pending_emails
    
    def update_email_status(self, email_id: str, status: str):
        self.redis.hset(email_id, "status", status)
        if status == "sent":
            self.redis.hset(email_id, "sent_at", str(datetime.utcnow().timestamp()))
    
    def delete_email(self, email_id: str):
        self.redis.delete(email_id)
        