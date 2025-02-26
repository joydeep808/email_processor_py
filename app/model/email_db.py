from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Any, Optional

from sqlalchemy import Row
from app.model.connection import engine
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, text , select

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

engine = create_engine("postgresql://joydeep:joydeep122@localhost:5432/email_service")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def save_email_in_db(email: EmailCreate):
    session:SessionDep = next(get_session())
    db_email = Email(**email.model_dump())
    session.add(db_email , False)
    session.commit()
    session.refresh(db_email)
    return db_email

def get_email(recipient: str):
    session:SessionDep = next(get_session())
    result = session.exec(select(Email).offset(0).limit(10)).all()
    db_email = result  # Use fetchone() for a single record, or fetchall() for multiple results
    if not db_email:
        raise HTTPException(status_code=404, detail="Email not found")
    return db_email
def get_record_by_id(id:int):
    session:SessionDep = next(get_session())
    result = session.exec(select(Email).where(Email.id == id)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Email not found")
    return result.model_dump()

def update_record_by_id(id:int):
    session:SessionDep = next(get_session())
    result = session.exec(select(Email).where(Email.id == id)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Email not found")
    result.status = "sent"
    result.sent_at = datetime.utcnow()
    session.add(result)
    session.commit()
    session.refresh(result)
    return result