from typing import List, Dict
import math

class NotationBuilder:
    def __init__(self, subdivisions_per_beat: int = 4, beats_per_measure: int = 4):
        self.subdivision_per_beat = subdivisions_per_beat
        self.beats_per_measure = beats_per_measure

    def build(self, structured_hits: List[Dict]) -> Dict[int, List[Dict]]:
        """
        Convert structured hits into notation-ready events per measure.
        Returns:
         {measure_number: [{instrument, duration, is_rest}, ...]}
        """
        measures = {}

        # Sort hits just in case
        hits_sorted = sorted(
            structured_hits,
            key=lambda h: (h["measure"], h["beat"], h["subdivision"])
        )

        # Process each hit
        for i, hit in enumerate(hits_sorted):
            measure = hit["measure"]
            if measure not in measures:
                measures[measure] = []
            
            # Compute duration: difference to next hit or end of measure
            if i + 1 < len(hits_sorted):
                next_hit = hits_sorted[i + 1]
                delta_beats = (
                    (next_hit["measure"] - measure) * self.beats_per_measure
                    + (next_hit["beat"] - hit["beat"])
                    + (next_hit["subdivision"] - hit["subdivision"]) / self.subdivision_per_beat
                )
            else:
                delta_beats = 1 / self.subdivision_per_beat  # Last note default to one subdivision

            # Map delta_beats to standard notation duration
            duration = self._beat_to_duration(delta_beats)

            measures[measure].append({
                "instrument": hit["label"],
                "duration": duration,
                "is_rest": False
            })

        # Optional: Fill gaps with rests (later enhancement)
        return measures

    def _beat_to_duration(self, beats: float) -> str:
        """
        Map fractional beats to VexFlow note duration strings
        (simplified for 4/4, 16th subdivisions)
        """
        if math.isclose(beats, 1):
            return "q"  # quarter note
        elif math.isclose(beats, 0.5):
            return "8"  # eighth note
        elif math.isclose(beats, 0.25):
            return "16"  # sixteenth note
        elif beats > 1:
            return f"{int(beats)}"  # approximate longer durations
        else:
            return "16"  # fallback
        