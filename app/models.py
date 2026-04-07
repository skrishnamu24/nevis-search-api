from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field

class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    description: Optional[str] = None
    social_links: list[str] = Field(default_factory=list)

class Client(ClientCreate):
    id: str

class DocumentCreate(BaseModel):
    title: str
    content: str

class Document(DocumentCreate):
    id: str
    client_id: str
    created_at: datetime
    summary: Optional[str] = None

class SearchResult(BaseModel):
    type: Literal['client', 'document']
    score: float
    id: str
    title: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    snippet: Optional[str] = None
    summary: Optional[str] = None
    client_id: Optional[str] = None
