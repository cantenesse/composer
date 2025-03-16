from pydantic import BaseModel
from typing import List

class SentMail(BaseModel):
    id: str
    recipients: List[str]
    date: str
    subject: str
    message: str
    embeddings: List[float]
