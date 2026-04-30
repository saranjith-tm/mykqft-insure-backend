import os
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services.extraction_service import ExtractionService

router = APIRouter(tags=["Extraction"])
extraction_service = ExtractionService()

class ExtractionResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    page_images_count: int
    fallback_logs: List[Dict[str, Any]]
    message: Optional[str] = None

@router.post("/extract", response_model=ExtractionResponse)
async def extract_document(
    file: UploadFile = File(...),
    use_vlm_fallback: bool = Form(True)
):
    """
    Extract data from a document (PDF/Image) using Azure Document Intelligence 
    with Agno Agentic VLM fallback.
    """
    try:
        file_bytes = await file.read()
        filename = file.filename
        
        # Use model ID from environment variables
        azure_model_id = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_MODEL_ID", "prebuilt-document")
        
        merged_data, page_images, fallback_logs = await extraction_service.run_extraction(
            file_bytes=file_bytes,
            filename=filename,
            model_id=azure_model_id,
            use_vlm_fallback=use_vlm_fallback
        )
        
        return ExtractionResponse(
            success=True,
            data=merged_data,
            page_images_count=len(page_images),
            fallback_logs=fallback_logs
        )

    except Exception as e:
        return ExtractionResponse(
            success=False,
            data={},
            page_images_count=0,
            fallback_logs=[],
            message=f"Extraction failed: {str(e)}"
        )
