"""
	1.	Load your trained CNN model
	2.	Take (mel_windows.npy)
	3.	Predict class per window
	4.	Save result next to the file:
"""
# IMPORTANT NOTE: THIS IS MVP VERSION! SO NO ML IS USED
# services/drum_classifier.py
import numpy as np
from typing import List, Dict

# Labels supported by the MVP classifier
CLASS_LABELS = ["kick", "snare", "hihat", "tom1", "tom2", "tom3", "crash", "ride"]

class DrumClassifier:
    """
    Rule-based (heuristic) drum classifier for MVP.
    Input: mel-window (H x W x 1) or batch (N, H, W, 1).
    Output: label per window.
    """

    def __init__(self):
        self.labels = CLASS_LABELS

    def _energy_bands(self, mel: np.ndarray) -> Dict[str, float]:
        """
        Split mel spectrogram into coarse frequency bands and return mean energy.
        Assumes mel.shape = (n_mels, n_frames)
        """
        n_mels = mel.shape[0]
        # Define approximate band indices (these are heuristics; tune per your n_mels)
        # We assume n_mels is ~64; adapt if different.
        low_end = int(n_mels * 0.12)      # ~ <200Hz region
        low_mid_end = int(n_mels * 0.30)  # toms / mid
        mid_end = int(n_mels * 0.60)      # snare region / mid-high
        high_mid_end = int(n_mels * 0.80) # high-mid
        # bands
        low = mel[:low_end].mean() if low_end > 0 else 0.0
        low_mid = mel[low_end:low_mid_end].mean() if low_mid_end > low_end else 0.0
        mid = mel[low_mid_end:mid_end].mean() if mid_end > low_mid_end else 0.0
        high_mid = mel[mid_end:high_mid_end].mean() if high_mid_end > mid_end else 0.0
        high = mel[high_mid_end:].mean() if n_mels > high_mid_end else 0.0

        return {
            "low": float(low),
            "low_mid": float(low_mid),
            "mid": float(mid),
            "high_mid": float(high_mid),
            "high": float(high),
        }

    def predict_window(self, window: np.ndarray) -> str:
        """
        Predict label for a single window.
        window: shape (H, W, 1) or (H, W)
        Returns a string label.
        """
        if window.ndim == 3:
            mel = window[:, :, 0]
        else:
            mel = window

        bands = self._energy_bands(mel)

        low = bands["low"]
        low_mid = bands["low_mid"]
        mid = bands["mid"]
        high_mid = bands["high_mid"]
        high = bands["high"]

        # Basic heuristics (ratios) — tune these if needed.

        # Kick: strong low energy relative to others
        if low > max(low_mid * 1.2, mid * 1.4, high * 1.5):
            return "kick"

        # Hi-hat: very strong high energy
        if high > max(high_mid * 1.1, mid * 1.5, low * 2.0):
            return "hihat"

        # Crash: wideband high/sting and longer decay — captured as strong high_mid + high
        # Heuristic: both high_mid and high significant relative to mid
        if (high + high_mid) > mid * 1.6 and (high + high_mid) > low_mid * 1.2:
            return "crash"

        # Snare: mid + high_mid prominent
        if (mid + high_mid) > low_mid * 1.2 and mid > low * 0.9:
            return "snare"

        # Toms: energy concentrated in low-mid / mid (different relative thresholds)
        # High tom: higher low_mid
        if low_mid > mid * 1.1 and low_mid > low * 1.0:
            return "tom1"

        # Mid tom:
        if low_mid > low and mid > low_mid * 0.8:
            return "tom2"

        # Floor tom: more low than low_mid
        if low > low_mid * 1.1 and low_mid > mid * 0.8:
            return "tom3"

        # Fallbacks: prefer snare if mid present, else hihat if high present, else unknown->kick
        if mid > low or high_mid > low:
            return "snare"
        if high > 0.01:
            return "hihat"
        return "kick"

    def classify_batch(self, batch: np.ndarray) -> List[str]:
        """
        batch: (N, H, W, 1)
        returns list of labels length N
        """
        labels = []
        for win in batch:
            labels.append(self.predict_window(win))
        return labels

    def classify_from_file(self, cnn_file_path) -> List[str]:
        batch = np.load(str(cnn_file_path))
        return self.classify_batch(batch)
    