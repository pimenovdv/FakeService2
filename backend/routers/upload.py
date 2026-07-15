from fastapi import APIRouter, UploadFile, File
import uuid

router = APIRouter(prefix="/api", tags=["upload"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Mocking file upload and returning a fake URL/ID
    file_id = str(uuid.uuid4())
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_id": file_id,
        "url": f"/mock-uploads/{file_id}/{file.filename}"
    }
