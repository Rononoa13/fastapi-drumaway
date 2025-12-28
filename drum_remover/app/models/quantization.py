from pydantic import BaseModel, Field
from typing import Literal

class Hit(BaseModel):
    time: float = Field(..., ge=0)
    label: str

class QuantizedHit(BaseModel):
    beat: float = Field(..., ge=0)
    label: str
    original_time: float
    