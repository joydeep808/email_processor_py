import json
from datetime import datetime
import redis
# from app.model.email import EmailCreate
from app.model.item import EmailCreate, save_email , get_email

class RedisService:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
    
    def save_email(self, email: EmailCreate) -> str:
        email_dict = email.model_dump()
        email_dict["created_at"] = datetime.utcnow().timestamp()
        # Generate UUID and use it as the key
        email_dict["id"] = str(email_dict["id"])
        # Store the UUID in the hash
        redis_key =f"email:{str(email_dict['id'])}"
        Email_Service().save_email(email=email_dict) # type: ignore
        self.redis.hset(redis_key, mapping=email_dict)
        save_email(email)
        return redis_key
    
    async def get_pending_emails(self):
        keys = self.redis.keys("email:*")
        if not keys:
            return []

        pipeline = self.redis.pipeline()
        for key in keys: # type: ignore
            pipeline.hgetall(key)
        
        emails_data = pipeline.execute()
        pending_emails = []

        for email_data in emails_data:
            if email_data.get("status") == "pending":
            # Convert timestamps back to datetime
                email_data["created_at"] = datetime.fromtimestamp(float(email_data["created_at"]))
                if email_data.get("sent_at"):
                    email_data["sent_at"] = datetime.fromtimestamp(float(email_data["sent_at"]))
                pending_emails.append(email_data)
        
        return pending_emails
    
    async def update_email_status(self, email_id: str, status: str):
        self.redis.hset(email_id, "status", status)
        if status == "sent":
            self.redis.hset(email_id, "sent_at", str(datetime.utcnow().timestamp()))
    
    def delete_email(self, email_id: str):
        self.redis.delete(email_id)
        