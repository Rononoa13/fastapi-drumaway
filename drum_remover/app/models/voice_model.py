from pydantic import BaseModel, Field
from typing import List

from drum_remover.app.models.event_model import NotationEvent


class Voice(BaseModel):
    voice: int = Field(..., ge=1)
    events: List[NotationEvent]