import re
from typing import Dict, Any, List, Tuple
from agents.orchestrator_agent import get_orchestrator_agent
from agents.vlm_specialist_agent import get_vlm_agent
from agents.tools.pdf_processor import pdf_to_images
from agents.tools.azure_client import extract_with_azure
from agents.tools.azure_processor import process_azure_result
from services.helpers.vlm_helper import run_vlm_fallback

class ExtractionService:
    def __init__(self):
        self.orchestrator = get_orchestrator_agent()
        self.vlm_agent = get_vlm_agent()

    async def run_extraction(
        self, 
        file_bytes: bytes, 
        filename: str, 
        model_id: str,
        use_vlm_fallback: bool = True
    ) -> Tuple[Dict[str, Any], List[bytes], List[Dict[str, Any]]]:
        
        is_pdf = filename.lower().endswith(".pdf")
        page_images = pdf_to_images(file_bytes) if is_pdf else [file_bytes]
        
        # 1. Run Azure extraction
        raw_result = extract_with_azure(file_bytes, model_id)
        processed = process_azure_result(raw_result)
        
        merged_data = {}
        field_confidences = {}
        fallback_logs = []
        confidences = []
        
        azure_pages = processed.get("pages", [])
        
        for field in processed.get("fields", []):
            key = field["key"]
            value = field["value"]
            conf = field["confidence"]
            region = field["region"]
            
            # Sanitize key
            clean_key = re.sub(r'[^a-z0-9]+', '_', key.lower()).strip('_')
            
            if use_vlm_fallback and conf < 0.80 and region:
                # Delegate VLM Fallback to helper
                value, conf = await run_vlm_fallback(
                    vlm_agent=self.vlm_agent,
                    key=key,
                    clean_key=clean_key,
                    value=value,
                    conf=conf,
                    region=region,
                    page_images=page_images,
                    azure_pages=azure_pages,
                    fallback_logs=fallback_logs
                )

            merged_data[clean_key] = value
            field_confidences[clean_key] = round(conf, 4)
            confidences.append(conf)

        avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0
        merged_data["extraction_confidence"] = round(avg_confidence, 4)
        merged_data["_field_confidences"] = field_confidences
        
        return merged_data, page_images, fallback_logs
