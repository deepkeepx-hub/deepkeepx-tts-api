import os
import time
import hashlib
import base64
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from schemas import TTSRequest
from response import success_response, fail_response
from tts_engine import engine

# ==========================================
# Background task to clean up old audio files
# ==========================================
DATA_DIR = "/app/data"

async def cleanup_old_files():
    """
    Periodically delete files in DATA_DIR that are older than 2 hours.
    Runs every 10 minutes.
    """
    while True:
        try:
            now = time.time()
            if os.path.exists(DATA_DIR):
                for filename in os.listdir(DATA_DIR):
                    filepath = os.path.join(DATA_DIR, filename)
                    if os.path.isfile(filepath):
                        # Check if file modification time is older than 2 hours (7200 seconds)
                        if now - os.path.getmtime(filepath) > 7200:
                            os.remove(filepath)
                            print(f"Deleted expired file: {filename}")
        except Exception as e:
            print(f"Error during cleanup task: {e}")
        
        # Sleep for 10 minutes before next cleanup
        await asyncio.sleep(600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    # Start the background cleanup task
    cleanup_task = asyncio.create_task(cleanup_old_files())
    yield
    # Cancel the task on shutdown
    cleanup_task.cancel()

app = FastAPI(title="TTS API", version="1.0.0", lifespan=lifespan)

# Mount static files directory to serve audio files via URL
app.mount("/audio", StaticFiles(directory=DATA_DIR), name="audio")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=200, content=fail_response(msg=str(exc)).model_dump())

@app.get("/health")
async def health():
    return success_response(data={"status": "ok", "device": engine.device})

@app.post("/tts")
async def tts(req: TTSRequest, request: Request):
    try:
        audio_bytes, sample_rate = engine.synthesize(
            text=req.text, voice=req.voice, lang_code=req.lang_code,
            speed=req.speed, output_format=req.output_format,
        )
    except Exception as e:
        return fail_response(msg=f"Generation failed: {e}")

    # Generate a deterministic MD5 hash based on the input parameters
    hash_input = f"{req.text}_{req.voice}_{req.speed}".encode('utf-8')
    file_hash = hashlib.md5(hash_input).hexdigest()
    filename = f"{file_hash}.{req.output_format}"
    filepath = os.path.join(DATA_DIR, filename)

    # Write the file to the mounted data directory
    with open(filepath, "wb") as f:
        f.write(audio_bytes)

    # Generate the full access URL dynamically based on the incoming request
    base_url = str(request.base_url).rstrip("/")
    audio_url = f"{base_url}/audio/{filename}"

    data = {
        "format": req.output_format, 
        "sample_rate": sample_rate,
        "voice": req.voice, 
        "lang_code": req.lang_code or engine._infer_lang_code(req.voice),
        "audio_url": audio_url, 
        "file_path": filepath, 
    }

    if req.return_base64:
        data["audio_base64"] = base64.b64encode(audio_bytes).decode("utf-8")

    return success_response(data=data)

@app.get("/voices")
async def list_voices():
    voices = {
        "american_english_female": ["af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica", "af_kore", "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky"],
        "american_english_male": ["am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam", "am_michael", "am_onyx", "am_puck", "am_santa"],
        "british_english_female": ["bf_alice", "bf_emma", "bf_isabella", "bf_lily"],
        "british_english_male": ["bm_daniel", "bm_fable", "bm_george", "bm_lewis"],
        "chinese_female": ["zf_xiaobei", "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi"],
        "chinese_male": ["zm_yunjian", "zm_yunxi", "zm_yunxia", "zm_yunyang"],
        "spanish_female": ["ef_dora"],
        "spanish_male": ["em_alex", "em_santa"],
        "french_female": ["ff_siwis"],
        "hindi_female": ["hf_alpha", "hf_beta"],
        "hindi_male": ["hm_omega", "hm_psi"],
        "italian_female": ["if_sara"],
        "italian_male": ["im_nicola"],
        "japanese_female": ["jf_alpha", "jf_gongitsune", "jf_nezumi", "jf_tebukuro"],
        "japanese_male": ["jm_kumo"],
        "portuguese_female": ["pf_dora"],
        "portuguese_male": ["pm_alex", "pm_santa"]
    }
    return success_response(data=voices)