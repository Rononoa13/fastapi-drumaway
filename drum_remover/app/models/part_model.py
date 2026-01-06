from pydantic import BaseModel, Field
from typing import List
from drum_remover.app.models.measure_model import Measure
class Part(BaseModel):
    id: str = Field(..., description="Instrument part id, e.g. 'drums'")
    measures: List[Measure]