import uuid
from pydantic import BaseModel


class TopicCreateRequest(BaseModel):
    title: str  # e.g. "Java Arrays" -- the ONLY thing the student types


class TopicResponse(BaseModel):
    id: uuid.UUID
    title: str
    status: str

    class Config:
        from_attributes = True
