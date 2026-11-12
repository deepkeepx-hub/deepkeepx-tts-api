from typing import Any, Optional
from pydantic import BaseModel

class ApiResponse(BaseModel):
    code: int = 0
    msg: str = ""
    data: Optional[Any] = None
    success: bool = True

def success_response(data: Any = None, msg: str = "") -> ApiResponse:
    return ApiResponse(code=0, msg=msg, data=data, success=True)

def fail_response(msg: str = "Generation failed", code: int = 1, data: Any = None) -> ApiResponse:
    return ApiResponse(code=code, msg=msg, data=data, success=False)