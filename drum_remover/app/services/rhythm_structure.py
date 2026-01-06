# After quantization
# 
from typing import List, Dict
import math

class RhythmStructurer:
    def __init__(self, beats_per_measure: int = 4, subdivisions_per_beat: int = 4):
        self.beats_per_measure = beats_per_measure
        self.subdivisions_per_beat = subdivisions_per_beat

    def structure(self, quantized_hits: List[Dict]) -> List[Dict]:
        """
        Input:
            [{ "beat": float, "label": str }]
        Output:
            [{
                "measure": int,
                "beat": int,
                "subdivision": float,
                "label": str
            }]
        """
        structured = []

        for hit in quantized_hits:
            beat_pos = hit.beat
            label = hit.label

            # Measure index
            measure = int(beat_pos // self.beats_per_measure) + 1
            # Beat within measure
            beat_in_measure = int(beat_pos % self.beats_per_measure) + 1
            # Subdivision
            fractional = beat_pos - math.floor(beat_pos)
            subdivision = int(round(fractional * self.subdivisions_per_beat))

            structured.append({
                "measure": measure,
                "beat": beat_in_measure,
                "subdivision": subdivision,
                "label": label
            })
        return structured