from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

#creating database engine

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True, #checks if the connection is valid before using it and keeps connection alive
)

#session factory
SessionLocal = sessionmaker(autocommit=False, autoFlush=False, bind=engine)

#Base class for all models to inherit from
Base = declarative_base()

#dependancy to get db session in FastAPI routes

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()