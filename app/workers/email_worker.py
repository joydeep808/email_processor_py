from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.rabbit_service import RabbitMQService
from app.services.redis_service import RedisService
from app.services.email_service import EmailService

class EmailWorker:
    def __init__(
        self,
        rabbit_service: RabbitMQService,
        redis_service: RedisService,
        email_service: EmailService
    ):
        self.rabbit_service = rabbit_service
        self.redis_service = redis_service
        self.email_service = email_service
        self.scheduler = AsyncIOScheduler()

    async def process_email(self, email_data: dict):
        try:
            # Attempt to send email
            success = await self.email_service.send_email(email_data)
            
            if success:
                # Update status in Redis
                await self.redis_service.update_email_status(
                    email_data["id"],
                    "sent"
                )
            else:
                # Implement retry logic here
                # For now, we'll just mark as failed
               await self.redis_service.update_email_status(
                    email_data["id"],
                    "failed"
                )
        except Exception as e:
            # Log error and implement retry logic
            print(f"Error processing email: {e}")

    async def start(self):
        # Start processing messages from RabbitMQ
        await self.rabbit_service.process_emails(self.process_email)
        
        # Start the scheduler
        self.scheduler.start()