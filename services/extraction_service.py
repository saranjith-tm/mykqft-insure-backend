import json
import base64
import re
from typing import Dict, Any, List, Tuple
from agno.agent import Agent
from agno.media import Image
from agents.orchestrator_agent import get_orchestrator_agent
from agents.vlm_specialist_agent import get_vlm_agent
from agents.tools.pdf_processor import pdf_to_images
from agents.tools.image_processor import crop_and_enhance_region
from agents.tools.azure_client import extract_with_azure
from agents.tools.azure_processor import process_azure_result

class ExtractionService:
    def __init__(self):
        self.orchestrator = get_orchestrator_agent()
        self.vlm_agent = get_vlm_agent()

    async def run_extraction(
        self, 
        file_bytes: bytes, 
        filename: str, 
        model_id: str = "prebuilt-document",
        use_vlm_fallback: bool = True
    ) -> Tuple[Dict[str, Any], List[bytes], List[Dict[str, Any]]]:
        
        is_pdf = filename.lower().endswith(".pdf")
        page_images = pdf_to_images(file_bytes) if is_pdf else [file_bytes]
        
        # 1. Run Azure via Orchestrator (direct tool call for pipeline efficiency)
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
                # Run VLM Fallback
                try:
                    page_num = region["page_number"]
                    if page_num <= len(page_images):
                        page_img = page_images[page_num - 1]
                        
                        # Find page dimensions from Azure result
                        page_info = next((p for p in azure_pages if p["page_number"] == page_num), None)
                        if page_info:
                            crop_bytes = crop_and_enhance_region(
                                page_img, 
                                region["polygon"], 
                                page_info["width"], 
                                page_info["height"]
                            )
                            
                            prompt = (
                                f"Please extract the specific text value for the field '{key}' from this cropped image region. "
                                "Return a JSON object with exactly two keys: 'value' (the extracted text) and 'confidence' (a number between 0.0 and 1.0 indicating your certainty)."
                            )
                            
                            vlm_response = self.vlm_agent.run(prompt, images=[Image(content=crop_bytes)])
                            
                            # Parse VLM response
                            try:
                                content = vlm_response.content.replace("```json", "").replace("```", "").strip()
                                vlm_resp = json.loads(content)
                                if "value" in vlm_resp and "confidence" in vlm_resp:
                                    vlm_val = str(vlm_resp["value"])
                                    vlm_conf = float(vlm_resp["confidence"])
                                    
                                    fallback_logs.append({
                                        "field": clean_key,
                                        "azure_val": value,
                                        "azure_conf": conf,
                                        "vlm_val": vlm_val,
                                        "vlm_conf": vlm_conf,
                                        "crop_image_b64": base64.b64encode(crop_bytes).decode('utf-8'),
                                        "selected": "vlm" if vlm_conf > conf else "azure"
                                    })
                                    
                                    if vlm_conf > conf:
                                        value = vlm_val
                                        conf = vlm_conf
                            except Exception as e:
                                print(f"Error parsing VLM response: {e}")
                except Exception as e:
                    print(f"VLM Fallback Error: {e}")

            merged_data[clean_key] = value
            field_confidences[clean_key] = round(conf, 4)
            confidences.append(conf)

        avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0
        merged_data["extraction_confidence"] = round(avg_confidence, 4)
        merged_data["_field_confidences"] = field_confidences
        
        return merged_data, page_images, fallback_logs
