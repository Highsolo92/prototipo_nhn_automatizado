from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os

DATABASE_URL = os.getenv("DB_URL", "sqlite:///./data/nhn.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    name = Column(String(255))
    email = Column(String(255))
    source = Column(String(100))
    priority = Column(String(20), default="Media")
    status = Column(String(50), default="Nuevo")
    owner = Column(String(100), default=None)
    notes = Column(Text, default="")

def init_db():
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
