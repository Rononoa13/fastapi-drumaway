from pathlib import Path
import json

import librosa
import numpy as np

from services.onset_detector import OnsetDetector
from services.cnn_preparer import CNNPreparer
from services.drum_classifier import DrumClassifier
from services.midi_writer import MIDIWriter

detector = OnsetDetector()
cnn = CNNPreparer()
dclassifier = DrumClassifier()

def detect_onsets_task(drum_path: Path):
    """
    Background task to detect onsets for a drum stem.
    Saves results to a JSON file with same name as drum stem.
    """
    try:
        y, sr = detector.load_audio(drum_path)
        if y.size == 0:
            print(f"[OnsetTask] Empty audio {drum_path}")
            return
        # Detect onsets
        onset_times = detector.detect_onsets(y, sr)

        # Save to JSON
        out_json = drum_path.with_suffix(".onsets.json")
        with open(out_json, "w") as f:
            json.dump({"onsets": onset_times}, f)

        print(f"✅ Onset detection complete: {len(onset_times)} hits saved to {out_json}")

        # CNN PREP (MEL WINDOWS EXTRACTION)
        print(f"[Task] Running CNN preparation...")
        cnn_batch = cnn.prepare_for_cnn(drum_path, onset_times)
        cnn_out_path = drum_path.with_suffix(".mel_windows.npy")
        np.save(cnn_out_path, cnn_batch)

        # Drum Classification
        print(f"[Task] Classifying drum hits...")
        labels = dclassifier.classify_batch(cnn_batch)

        # Combine times + labels
        hits = [{"time": t, "label": l} for t, l in zip(onset_times, labels)]
        hits_json_path = drum_path.with_suffix(".hits.json")
        with open(hits_json_path, "w") as f:
            json.dump(hits, f)
        print(f"✅ Drum hits classified and saved: {hits_json_path}")

        # --- DETECT SONG BPM DYNAMICALLY ---
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = float(tempo)  # <-- convert from numpy scalar to Python float
        print(f"[INFO] Detected BPM: {tempo:.2f}")

        # --- GENERATE MIDI ---
        midi_writer = MIDIWriter(bpm=tempo)                # Pass dynamic BPM
        midi_path = drum_path.with_suffix(".mid")          # same filename but .mid
        midi_writer.write(hits, midi_path)
        print(f"✅ MIDI drum track generated at {tempo:.2f} BPM → {midi_path}")

    except Exception as e:
        print(f"[OnsetTask] Failed for {drum_path}: {e}")
