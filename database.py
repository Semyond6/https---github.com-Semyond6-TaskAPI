from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import  Column, Integer, String, Boolean, DateTime

#Работа с БД

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1qazxcvb@db:5432/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

Base = declarative_base()

class Person(Base):
    'Таблица хранения пользователей'
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    disabled = Column(Boolean, default=False)
    hashed_password = Column(String)
    
class HistorySession(Base):
    'Таблица хранения истории запросов'
    __tablename__ = "history"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    datain = Column(String)
    dataout = Column(String)
    date_request = Column(DateTime)
    token_user = Column(String)
        
SessionLocal = sessionmaker(autoflush=False, bind=engine)