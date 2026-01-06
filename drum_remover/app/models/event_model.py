from pydantic import BaseModel, Field
from typing import Optional, Literal

class NotationEvent(BaseModel):
    type: Literal["note", "rest"]
    duration: str = Field(
        ...,
        description=""
    )
    # Only for notes
    instrument: Optional[str] = Field(
        None,
        description="Drum instrument label (snare, kick, hihat)"
    )
    velocity: Optional[str] = Field(
        None,
        ge=0, le=127,
        description="MIDI velocity (optional)"
    )
    articulation:Optional[str] = Field(
        None,
        description="Accent, ghost, flam etc."
    )