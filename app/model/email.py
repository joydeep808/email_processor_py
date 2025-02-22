from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr
from uuid import UUID, uuid4
class EmailBase(SQLModel):
    id: str = Field(default_factory=uuid4)
    recipient: EmailStr
    subject: str
    body: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[int] = 1

class Email(EmailBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class EmailCreate(EmailBase):
    created_at: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    sent_at: Optional[int] = 1

class EmailResponse(EmailBase):
    pass