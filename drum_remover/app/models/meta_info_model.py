from pydantic import BaseModel, Field
from typing import Tuple


class NotationMeta(BaseModel):
    tempo: int = Field(..., gt=0)
    time_signature: Tuple[int, int] = Field(..., description="e.g. (4,4)")
    swing: bool = False