# Create a MIDI file from classified hits!
# services/midi_writer.py
from mido import Message, MidiFile, MidiTrack
from mido import bpm2tempo
from pathlib import Path
from typing import List

# General MIDI drum mapping (standard)
DRUM_MIDI = {
    "kick": 36,
    "snare": 38,
    "hihat": 42,   # closed hi-hat
    "tom1": 48,    # high tom
    "tom2": 45,    # mid tom
    "tom3": 43,    # floor tom
    "crash": 49,
    "ride": 51,
    "unknown": 38,
}

class MIDIWriter:
    def __init__(self, bpm: int = 120):
        self.bpm = bpm
        self.tempo = bpm2tempo(bpm)

    def _seconds_to_ticks(self, seconds: float, mid: MidiFile) -> int:
        """
        Convert seconds to ticks based on mid.ticks_per_beat and bpm.
        ticks_per_second = ticks_per_beat * (bpm / 60)
        """
        tpb = mid.ticks_per_beat
        ticks_per_second = tpb * (self.bpm / 60.0)
        return int(round(seconds * ticks_per_second))

    def write(self, hits: List[dict], out_path: Path):
        """
        hits: [{ "time": float_seconds, "label": "kick" }, ...]
        Saves a MIDI drum track.
        """
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # Ensure hits sorted by time
        hits_sorted = sorted(hits, key=lambda x: x["time"])

        prev_tick = 0
        for hit in hits_sorted:
            t = float(hit["time"])
            note = DRUM_MIDI.get(hit["label"], DRUM_MIDI["unknown"])
            tick = self._seconds_to_ticks(t, mid)
            delta = max(0, tick - prev_tick)
            prev_tick = tick

            # note_on then short note_off
            track.append(Message('note_on', channel=9, note=note, velocity=100, time=delta))
            # small duration in ticks for percussion
            track.append(Message('note_off', channel=9, note=note, velocity=0, time=10))

        mid.save(str(out_path))
        print(f"🎹 MIDI exported → {out_path}")
        