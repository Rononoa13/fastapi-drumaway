"""
	1.	Load your trained CNN model
	2.	Take (mel_windows.npy)
	3.	Predict class per window
	4.	Save result next to the file:
"""
# IMPORTANT NOTE: THIS IS MVP VERSION! SO NO ML IS USED
import numpy as np
from pathlib import Path
from typing import List, Literal, Dict, Optional

# All supported drum classes
DrumLabel = Literal[
    "kick",
    "snare",
    "hihat",
    "tom1",
    "tom2",
    "tom3",
    "crash",
    "ride"
]

class DrumClassifier:
    def __init__(self, model_path: Optional[Path] = None):
        """
        Args:
            model_path: Optional path to a trained CNN model.
                        If missing → runs in mock mode (useful for MVP)
        """
        self.model_path = model_path
        self.model = None

        if model_path is not None:
            self._load_model(model_path)
        else:
            print("⚠️ DrumClassifier running in MOCK MODE (no ML yet).")

        self.class_labels: List[DrumLabel] = [
            "kick", "snare", "hihat",
            "tom1", "tom2", "tom3",
            "crash", "ride"
        ]

    # -----------------------------
    # Loading model (real CNN later)
    # -----------------------------
    def _load_model(self, model_path: Path):
        print(f"Loading model from {model_path}…")
        # TODO: load TensorFlow model
        # from tensorflow.keras.models import load_model
        # self.model = load_model(model_path)
        raise NotImplementedError("Model loading not implemented yet.")

    # -----------------------------
    # Prediction
    # -----------------------------
    def predict_window(self, window: np.ndarray) -> DrumLabel:
        """
        Predict a single drum hit window.
        For MVP → returns random classes.
        """
        if self.model is None:
            # MOCK MODE: return fake label
            return np.random.choice(self.class_labels)

        # REAL MODE:
        # probs = self.model.predict(window[np.newaxis, ...])[0]
        # idx = np.argmax(probs)
        # return self.class_labels[idx]

    def classify(self, windows: np.ndarray, onset_times: List[float]) -> List[Dict]:
        """
        Args:
            windows: (N, H, W, 1) prepared mel-spec windows
            onset_times: list of floats matching each window
        Returns:
            [{ "time": t, "label": "snare" }, ...]
        """
        results = []

        for window, t in zip(windows, onset_times):
            label = self.predict_window(window)
            results.append({"time": t, "label": label})

        return results
    