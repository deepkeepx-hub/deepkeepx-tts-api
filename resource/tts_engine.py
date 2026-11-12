import io
import os
import threading
from typing import Optional, Tuple

import numpy as np
import soundfile as sf
import torch
from kokoro import KPipeline

# Force HuggingFace to offline mode since models are pre-packaged in the image
os.environ["HF_HUB_OFFLINE"] = "1"

class KokoroTTSEngine:
    """
    Wrapper for the Kokoro KPipeline.
    Supports lazy loading and automatic device detection (CPU/GPU).
    """

    def __init__(self):
        self._pipelines: dict[str, KPipeline] = {}
        self._lock = threading.Lock()
        # Automatically detect if CUDA (GPU) is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def _get_pipeline(self, lang_code: str) -> KPipeline:
        if lang_code not in self._pipelines:
            with self._lock:
                if lang_code not in self._pipelines:
                    self._pipelines[lang_code] = KPipeline(lang_code=lang_code, device=self.device)
        return self._pipelines[lang_code]

    @staticmethod
    def _infer_lang_code(voice: str) -> str:
        prefix_map = {
            "af": "a", "am": "a", "bf": "b", "bm": "b", 
            "ef": "e", "em": "e", "ff": "f", "hf": "h", "hm": "h", 
            "if": "i", "im": "i", "jf": "j", "jm": "j", "pf": "p", "pm": "p", 
            "zf": "z", "zm": "z",
        }
        prefix = voice[:2] if len(voice) >= 2 else ""
        if prefix not in prefix_map:
            raise ValueError(f"Cannot infer language from voice='{voice}'. Please provide lang_code explicitly.")
        return prefix_map[prefix]

    def synthesize(self, text: str, voice: str = "af_heart", lang_code: Optional[str] = None, speed: float = 1.0, output_format: str = "wav") -> Tuple[bytes, int]:
        if lang_code is None:
            lang_code = self._infer_lang_code(voice)

        pipeline = self._get_pipeline(lang_code)
        segments: list[np.ndarray] = []
        sample_rate = 24000
        
        for _, _, audio in pipeline(text, voice=voice, speed=speed):
            if isinstance(audio, torch.Tensor):
                audio = audio.cpu().numpy()
            segments.append(audio)

        if not segments:
            raise RuntimeError("Kokoro generated no audio segments.")

        waveform = np.concatenate(segments)
        buffer = io.BytesIO()
        sf.write(buffer, waveform, sample_rate, format=output_format.upper())
        
        return buffer.getvalue(), sample_rate

engine = KokoroTTSEngine()