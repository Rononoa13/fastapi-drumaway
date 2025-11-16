from pathlib import Path
import json
from services.onset_detector import OnsetDetector

detector = OnsetDetector()

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
    except Exception as e:
        print(f"[OnsetTask] Failed for {drum_path}: {e}")
