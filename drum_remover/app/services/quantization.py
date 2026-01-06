from typing import List
from models.quantization import Hit, QuantizedHit

class RhythmQuantizer:
    def __init__(self, bpm: float, allowed_division=(1, 0.5, 0.25, 1/3, 1/6), tolerance_ms=40):
        if bpm <= 0:
            raise ValueError("BPM must be > 0")
        self.bpm = float(bpm)
        self.seconds_per_beat = 60.0 / self.bpm
        self.allowed_divisions = allowed_division
        self.tolerance_beats = (tolerance_ms / 1000) / self.seconds_per_beat
    
    def _nearest_grid(self, beat_pos: float) -> float:
        candidates = []
        for div in self.allowed_divisions:
            grid = round(beat_pos / div) * div
            candidates.append(grid)
        return min(candidates, key=lambda g: abs(g - beat_pos))
    
    def quantize(self, hits: List[Hit]) -> List[QuantizedHit]:
        quantized = []

        for hit in hits:
            beat_pos = hit["time"] / self.seconds_per_beat
            snapped = self._nearest_grid(beat_pos)

            if abs(snapped - beat_pos) <= self.tolerance_beats:
                final_beat = beat_pos
            else:
                final_beat = beat_pos
            quantized.append(
                QuantizedHit(
                    beat=round(final_beat, 4),
                    label=hit["label"],
                    original_time=hit["time"]
                )
            )
        return quantized