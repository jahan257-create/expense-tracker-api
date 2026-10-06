from pydantic import BaseModel, Field
from datetime import date
from typing import Literal, Optional

class UserRegister(BaseModel):
    username: str = Field()
    email: str
    password: str = Field(min_length=4, max_length=72)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TransactionCreate(BaseModel):
    title: str
    amount: float = Field(gt=0)
    type:Literal["income", "expense"]
    category: str
    date: date


class TransactionResponse(BaseModel):
    id: int
    title: str
    amount: float
    type: str
    category: str
    date: date
    owner_id: int


class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    date: Optional[date] = None