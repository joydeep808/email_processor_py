import emails
from typing import Dict
from app.core.config import settings
from email.utils import formataddr
class EmailService:
    def __init__(self):
        self.smtp_settings = {
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
            "user": settings.SMTP_USER,
            "password": settings.SMTP_PASSWORD,
            "tls": True
        }

    
    def send_email(self, email_data: Dict) -> bool:
        message = emails.Message(
            subject=email_data["subject"],
            html=email_data["body"],
            mail_from = formataddr(("Joydeep Debnath", settings.SMTP_FROM_EMAIL))
        )

        response = message.send(
            to=email_data["recipient"],
            smtp=self.smtp_settings
        )

        return response.status_code == 250