import numpy as np
import librosa
from pathlib import Path
from skimage.transform import resize

class CNNPreparer:
    def __init__(self, target_shape: tuple[int, int]= (256, 256),
                 window_size_sec: float = 0.32,
                 pre_offset_sec: float = 0.03,
                 n_mels: int = 64,
                 fmax: int = 12000):
        """
        Args:
            target_shape: Desired (height, width) for CNN input
            window_size_sec: Total duration of each window
            pre_offset_sec: Time before onset to include in window
            n_mels: Number of mel frequency bins
            fmax: Maximum frequency for mel-spectrogram
        """
        self.target_shape = target_shape
        self.window_size_sec = window_size_sec
        self.pre_offset_sec = pre_offset_sec
        self.n_mels = n_mels
        self.fmax = fmax

    def _extract_window(self, y: np.ndarray, sr: int, onset_time: float) -> np.ndarray:
        """
        Extract a short window of audio around the onset.
        """
        start = int((onset_time - self.pre_offset_sec) * sr)
        start = max(start, 0)
        end = start + int(self.window_size_sec * sr)
        return y[start:end]


    def prepare_for_cnn(self, audio_path: Path, onset_times: list[float]) -> np.ndarray:
        """
        Full pipeline: extract windows → convert to mel-spectrogram → normalize → resize
        Returns:
            Array of shape (num_windows, height, width, 1) ready for CNN
        """
        # Load audio
        y, sr = librosa.load(audio_path, sr=None, mono=True)

        mel_batches = []

        for onset in onset_times:
            # 1 - extract raw audio window
            window = self._extract_window(y, sr, onset)
            if len(window) == 0:
                continue
            # 2 - mel spectrogram
            mel = librosa.feature.melspectrogram(
                y=window,
                sr=sr,
                n_mels=self.n_mels,
                fmax = self.fmax
            )
            mel_db = librosa.power_to_db(mel, ref=np.max)
            # 3 - resize for cnn
            mel_resized = resize(mel_db, self.target_shape, mode="constant")
            # 4 - Normalize 0-1
            mel_norm = (
                mel_resized - mel_resized.min()
            ) / (mel_resized.max() - mel_resized.min() + 1e-6)
            # 5 - Add channel dimension
            mel_norm = np.expand_dims(mel_norm, axis=-1)

            mel_batches.append(mel_norm)

        if not mel_batches:
            return np.empty((0, *self.target_shape, 1))
        
        return np.stack(mel_batches, axis=0)
