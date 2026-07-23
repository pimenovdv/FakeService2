from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/translate", tags=["Translation"])

class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: str | None = None

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str

@router.post("", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    # Mock translation
    prefix = f"[{request.target_language.upper()}] "
    translated_text = prefix + request.text

    source_lang = request.source_language if request.source_language else "auto"

    return TranslationResponse(
        translated_text=translated_text,
        source_language=source_lang,
        target_language=request.target_language
    )
