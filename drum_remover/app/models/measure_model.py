from pydantic import BaseModel, Field
from typing import List
from drum_remover.app.models.voice_model import Voice

class Measure(BaseModel):
    number: int = Field(..., ge=1)
    voices: List[Voice]