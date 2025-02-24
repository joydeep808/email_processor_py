from sqlmodel import create_engine , SQLModel
from app.core.config import settings

DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Create the SQLAlchemy engine to interact with the PostgreSQL database
engine = create_engine(DATABASE_URL)

# If you want to create tables (if they don't exist already), you can use:
SQLModel.metadata.create_all(engine)
