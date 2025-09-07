from pathlib import Path
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from demucs.separate import main as demucs_main
from config import OUTPUT_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Demucs processor class
class AudioProcessor:
    def __init__(self, output_dir: str = OUTPUT_DIR, model: str = "htdemucs"):
        '''
        Args:
            input_file -> Path to input audio file
            output_dir -> directory to save seperated tracks. seperated/
        Returns:
            Path to separated drums file
        '''
        self.model = model
        self.output_dir = output_dir

    def _run_demucs(self, input_file: str):
        """
            Run Demucs separation for drums + rest.
        """
        args = [
            "--two-stems", "drums",
            "-n", self.model,
            "-o", str(self.output_dir),
            "--shifts", "5",           # Adds shift trick for better quality
            "--overlap", "0.25",       # Prevents boundary artifacts
            str(input_file)
        ]
        try:
            demucs_main(args)
        except Exception as e:
            raise RuntimeError(f"Demucs failed: {e}")
        
    def _get_output_paths(self, input_file: Path) -> dict:
        # Get base information
        song_name = input_file.stem
        print("song_name -> ", song_name)
        model_dir = self.output_dir / self.model / song_name

        # Create standard paths
        drums_path = self.output_dir / f"{song_name}_drums.wav"
        rest_path = self.output_dir / f"{song_name}_no_drums.wav"

        # Flatten files
        # Handle model directory files if they exist
        if model_dir.exists(): # First check: does the model's directory exist?
            orig_drums = model_dir / "drums.wav"
            print("orig_drums -> ", orig_drums)
            orig_rest = model_dir / "no_drums.wav"
            print("orig_rest -> ", orig_rest)

            if orig_drums.exists(): # Second check: does drums.wav exist?
                orig_drums.rename(drums_path) # Move/rename if it exists

            if orig_rest.exists():  # Third check: does no_drums.wav exist?
                orig_rest.rename(rest_path)  # Move/rename if it exists
        
        return {"drums": drums_path, "rest": rest_path}
    
    def separate_drums(self, input_file: str) -> dict:
        """
        Synchronously separate drums from input file.
        Returns dictionary with paths to drums and rest.
        """
        input_file = Path(input_file)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        self._run_demucs(input_file)
        output_paths = self._get_output_paths(input_file)

        logger.info("✅ Separation complete. Files saved: %s", output_paths)
        return output_paths
    
    async def separate_drums_async(self, input_file: str) -> dict:
        """
        Async wrapper to run separation in a thread pool.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.separate_drums, input_file)

# 
'''
Demucs may fail if FFmpeg is missing. You can auto-convert MP3 → WAV using pydub as a fallback:
def _ensure_wav(self, file_path: Path) -> Path:
'''