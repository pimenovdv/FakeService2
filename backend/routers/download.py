from fastapi import APIRouter, Query
from fastapi.responses import Response

router = APIRouter(prefix="/api/download", tags=["download"])

@router.get("/{file_id}")
async def mock_download(file_id: str, format: str = Query("txt", description="The format of the file to download")):
    """
    Mocks a file download by returning simple text/csv/json content based on the requested format.
    """
    format = format.lower()

    if format == "json":
        content = f'{{"id": "{file_id}", "message": "This is a mock JSON file."}}'
        return Response(content=content, media_type="application/json")
    elif format == "csv":
        content = f"id,message\n{file_id},This is a mock CSV file."
        return Response(content=content, media_type="text/csv")
    else:
        # Default to txt
        content = f"File ID: {file_id}\nThis is a mock text file."
        return Response(content=content, media_type="text/plain")
