from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.model.connection import engine
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class EmailBase(BaseModel):
    recipient: EmailStr  # Using EmailStr for email validation
    subject: str
    body: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None

class EmailCreate(BaseModel):
    recipient: EmailStr
    subject: str
    body: str

class EmailUpdate(BaseModel):
    recipient: Optional[EmailStr] = None
    subject: Optional[str] = None
    body: Optional[str] = None

class Email(EmailBase, SQLModel, table=True):
    __tablename__ = "emails"  # type: ignore # Explicitly define table name
    id: int = Field(default=None, primary_key=True)
    recipient: str = Field(..., index=True)  # Index email field for faster queries
    subject: str = Field(...)
    body: str = Field(...)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(default=None)

from typing import Generator
connect_args = {"check_same_thread": False}
engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres", connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]


def save_email(email: EmailCreate, session: Session = Depends(get_session)):
    db_email = Email(**email.dict())
    session.add(db_email)
    session.commit()
    session.refresh(db_email)
    return db_email

def get_email(email_id: int, session: Session = Depends(get_session)):
    db_email = session.get(Email, email_id)
    if not db_email:
        raise HTTPException(status_code=404, detail="Email not found")
    return db_email