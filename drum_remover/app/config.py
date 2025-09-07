import os
from pathlib import Path

BASE_DIR=Path(__file__).parent
# print("BASE_DIR ->", BASE_DIR)
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
# print(UPLOAD_DIR)
# print(OUTPUT_DIR)
# Demucs configuration
DEMUXS_MODEL = "music-demucs"
SAMPLE_RATE = 44100