from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    vendeur = "vendeur"


class AdminLogin(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    role: RoleEnum = RoleEnum.vendeur


class AdminOut(BaseModel):
    id: str
    username: str
    role: str
    actif: bool
