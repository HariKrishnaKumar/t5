# database/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from models.user import User
from models.conversation import Session, ConversationEntry

# Use the same name everywhere
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:dev2003@localhost:3306/bitewise_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)


# 3. Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base for models
Base = declarative_base()

# 5. Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
