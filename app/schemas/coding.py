import uuid
from pydantic import BaseModel


class RunRequest(BaseModel):
    problem_id: uuid.UUID
    language: str
    source_code: str
    stdin: str = ""


class SubmitRequest(BaseModel):
    problem_id: uuid.UUID
    language: str
    source_code: str
