from database import *
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import Depends, FastAPI, File, UploadFile, HTTPException, status, Body
from amount import calc, calc_file
from pydantic import BaseModel

from fastapi.security import  OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

import json

Base.metadata.create_all(bind=engine)

#Работа с безопасностью

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: Optional[str] = None
    
class User(BaseModel):
    username: str
    
    class Config:
        orm_mode = True

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/create_users")
def create_person(data = Body(...,
        example={
            "name": "Foo",
            "password": "",    
        },
        ), 
        db: Session = Depends(get_db)):
    password = get_password_hash(data["password"])
    person = Person(name=data["name"], hashed_password=password)
    db.add(person)
    db.commit()
    db.refresh(person)
    return person.name

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    user = db.query(Person).filter(Person.name == username).first()
    return user

def authenticate_user(username: str, password: str, db):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    elif user is not None:
        user.token = token
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

#Основной код задания

class Item(BaseModel):
    collections: Dict[str, list]

@app.post("/amount")       
def computing(item: Item) -> dict:
    calculeted = calc(item.collections)
    return {"amount": calculeted}
            
@app.post("/async")
async def async_computing(item: Item, 
                          current_user: User = Depends(get_current_active_user), 
                          db: Session = Depends(get_db)) -> dict:
    calculeted = calc(item.collections)
    history = HistorySession(username=current_user.name, 
                             datain = str(item.collections), 
                             dataout = calculeted, 
                             date_request = datetime.now(),
                             token_user = current_user.token)
    db.add(history)
    db.commit()
    db.refresh(history)
    return {"amount": calculeted, "token": current_user.token}

@app.post("/async/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), 
                             current_user: User = Depends(get_current_active_user), 
                             db: Session = Depends(get_db)) -> dict:
    read_file = await file.read()
    calculeted_file = calc_file(read_file)
    history = HistorySession(username=current_user.name, 
                             datain = str(json.loads(read_file.decode("UTF-8"))), 
                             dataout = calculeted_file, 
                             date_request = datetime.now(),
                             token_user = current_user.token)
    db.add(history)
    db.commit()
    db.refresh(history)
    return {"calculeted_file": calculeted_file, "token": current_user.token}