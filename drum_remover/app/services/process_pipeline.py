import json
from pathlib import Path
from typing import Optional

import numpy as np

from services.onset_detector import OnsetDetector
from services.cnn_preparer import CNNPreparer
from services.drum_classifier import DrumClassifier
from services.midi_writer import MIDIWriter

# Instantiate reusable objects
_detector = OnsetDetector()
_cnn_preparer = CNNPreparer()
_classifier = DrumClassifier()

def run_full_pipeline(
    drums_path: Path,
    *,
    force_rerun_onsets: bool = False,
    force_rerun_cnnprep: bool = False,
    save_midi: bool = True,
    midi_bpm: int = 120
) -> dict:
    """
    Run the pipeline end-to-end for a given drum stem file.

    Produces:
      - <stem>.onsets.json    (list of onset times)
      - <stem>.mel_windows.npy (N, H, W, 1)
      - <stem>.hits.json      (list of {time, label})
      - <stem>.drums.mid      (if save_midi True)

    Returns a dict with paths and counts.
    """
    drums_path = Path(drums_path)
    if not drums_path.exists():
        raise FileNotFoundError(f"Drums stem not found: {drums_path}")
    
    # ---------------------------
    # 1) Onsets (detect or load)
    # ---------------------------
    onsets_json = drums_path.with_suffix(".onsets.json")
    if onsets_json.exists() and not force_rerun_onsets:
        with open(onsets_json, "r") as f:
            data = json.load(f)
            onset_times = data.get("onsets", [])
        print(f"[Pipeline] Loaded {len(onset_times)} onsets from {onsets_json}")
    else:
        # load audio and detect
        y, sr = _detector.load_audio(drums_path)
        onset_times = _detector.detect_onsets(y, sr)
        with open(onsets_json, "w") as f:
            json.dump({"onsets": onset_times}, f)
        print(f"[Pipeline] Detected {len(onset_times)} onsets and saved to {onsets_json}")
    # ---------------------------
    # 2) CNN preparation (mel windows)
    # ---------------------------
    mel_npy = drums_path.with_suffix(".mel_windows.npy")
    if mel_npy.exists() and not force_rerun_cnnprep:
        batch = np.load(mel_npy, allow_pickle=False)
        print(f"[Pipeline] Loaded CNN batch from {mel_npy} shape={batch.shape}")
    else:
        batch = _cnn_preparer.prepare_for_cnn(drums_path, onset_times)
        np.save(mel_npy, batch)
        print(f"[Pipeline] Prepared CNN batch shape={batch.shape} saved to {mel_npy}")
    # ---------------------------
    # 3) Classification
    # ---------------------------
    hits_json = drums_path.with_suffix(".hits.json")
    if hits_json.exists() and not (force_rerun_onsets or force_rerun_cnnprep):
        with open(hits_json, "r") as f:
            hits = json.load(f).get("hits", [])
        print(f"[Pipeline] Loaded existing hits: {len(hits)}")
    else:
        if batch.shape[0] == 0:
            hits = []
            print("[Pipeline] No windows to classify.")
        else:
            labels = _classifier.classify_batch(batch)
            hits = [{"time": float(t), "label": str(l)} for t, l in zip(onset_times, labels)]
            with open(hits_json, "w") as f:
                json.dump({"hits": hits}, f)
            print(f"[Pipeline] Classified {len(hits)} hits and saved to {hits_json}")
    # ---------------------------
    # 4) MIDI export
    # ---------------------------
    midi_path = drums_path.with_suffix(".drums.mid")
    if save_midi and (not midi_path.exists() or force_rerun_onsets or force_rerun_cnnprep):
        writer = MIDIWriter(bpm=midi_bpm)
        writer.write(hits, midi_path)

    return {
        "onsets_json": str(onsets_json),
        "mel_npy": str(mel_npy),
        "hits_json": str(hits_json),
        "midi": str(midi_path) if save_midi else None,
        "num_onsets": len(onset_times),
        "num_windows": int(batch.shape[0])
    }