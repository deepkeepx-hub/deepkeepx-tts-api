from pydantic import BaseModel, Field
from typing import Optional

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="The text to synthesize")
    voice: str = Field("af_heart", description="Kokoro voice ID")
    lang_code: Optional[str] = Field(None, description="Language code")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    output_format: str = Field("wav", pattern="^(wav|flac)$", description="Audio output format")
    return_base64: bool = Field(True, description="Whether to return the audio as a base64 string")