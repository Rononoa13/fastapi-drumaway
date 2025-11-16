import numpy as np
import librosa
from pathlib import Path

class OnsetDetector:
    def __init__(self, hop: int = 256, n_mels: int = 128, fmax: int = 12000,
                 delta: float = 0.15, wait: int = 3):
        """
        Args:
            hop: hop length for onset detection
            n_mels: mel bins for onset envelope
            fmax: max frequency for spectral flux
            delta: sensitivity threshold
            wait: minimum frames between onsets
        """
        self.hop = hop
        self.n_mels = n_mels
        self.fmax = fmax
        self.delta = delta
        self.wait = wait

    def load_audio(self, path: Path, sr: int = None) -> tuple[np.ndarray, int]:
        """
        Load an audio file into memory as a waveform
        """
        try:
            y, sr = librosa.load(path, sr=sr, mono=True)
            return y, sr
        except Exception as e:
            print(f"Failed to load audio {Path}: {e}")
            return np.array([]), 0
        
    def detect_onsets(self, y: np.ndarray, sr: int) -> list[float]:
        """
        Detect onsets from a waveform.
        Returns list of onset times in seconds.
        """
        if y.size == 0 or sr == 0:
            return []
        
        # Compute onset envelope using spectral fux with median filteing
        onset_env = librosa.onset.onset_strength(
            y=y,
            sr=sr,
            hop_length = self.hop,
            aggragate=np.median,
            n_mels=self.n_mels,
            fmax=self.fmax  # Capture cymbal and snare crack
        )

        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            hop_length=self.hop,
            backtrack=True,
            units='frames',
            delta=self.delta,
            wait=self.wait  # prevent double hits but allow flams/rolls
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop)
        return onset_times.tolist()
