from pydantic import BaseModel, Field
from typing import List
from drum_remover.app.models.meta_info_model import NotationMeta
from drum_remover.app.models.part_model import Part

class DrumNotation(BaseModel):
    version: int = Field(1, const=True)
    meta: NotationMeta
    parts: List[Part]