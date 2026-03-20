"""
schemas.py — Pydantic models for request/response validation.
"""

from pydantic import BaseModel
from typing import List, Optional


class OCRResponse(BaseModel):
    text: str
    summary: str
    headings: List[str]
    cer: Optional[float] = None
    wer: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello World\nThis is a handwritten note.",
                "summary": "Hello World. This is a handwritten note.",
                "headings": ["HELLO WORLD"],
                "cer": 0.05,
                "wer": 0.10
            }
        }
