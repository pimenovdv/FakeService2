from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

router = APIRouter(prefix="/api", tags=["extract"])

@router.post("/extract")
async def extract_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None)
):
    """
    Mock endpoint for document extraction.
    Returns structured data based on the document_type or filename.
    """
    filename_lower = file.filename.lower() if file.filename else ""
    doc_type = document_type.lower() if document_type else "unknown"

    if doc_type == "id_card" or "id" in filename_lower:
        return {
            "status": "success",
            "document_type": "id_card",
            "extracted_data": {
                "first_name": "John",
                "last_name": "Doe",
                "id_number": "123456789",
                "date_of_birth": "1990-01-01",
                "expiry_date": "2030-12-31"
            }
        }
    elif doc_type == "invoice" or "invoice" in filename_lower:
        return {
            "status": "success",
            "document_type": "invoice",
            "extracted_data": {
                "invoice_number": "INV-1001",
                "date": "2023-10-15",
                "total_amount": 1500.50,
                "currency": "USD",
                "vendor_name": "Acme Corp"
            }
        }
    else:
        return {
            "status": "success",
            "document_type": "generic",
            "extracted_data": {
                "text": "Simulated extracted text content from generic document.",
                "word_count": 8
            }
        }
