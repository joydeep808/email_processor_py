from typing import Generator, AsyncGenerator
from fastapi import Depends
from sqlmodel import Session, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.redis_service import RedisService
from app.services.rabbit_service import RabbitMQService
from app.services.email_service import EmailService

# PostgreSQL
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async PostgreSQL
async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True,
    future=True
)

from sqlalchemy.ext.asyncio import async_sessionmaker

AsyncSessionLocal = async_sessionmaker(
    async_engine, expire_on_commit=False
)

# Dependencies
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session

def get_redis_service() -> RedisService:
    return RedisService(settings.REDIS_URL)

async def get_rabbitmq_service() -> RabbitMQService:
    service = RabbitMQService(settings.RABBITMQ_URL)
    await service.connect()
    return service

def get_email_service() -> EmailService:
    return EmailService()