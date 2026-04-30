import json
import base64
from typing import List, Dict, Any, Tuple
from agno.media import Image
from agents.tools.image_processor import crop_and_enhance_region

async def run_vlm_fallback(
    vlm_agent,
    key: str,
    clean_key: str,
    value: str,
    conf: float,
    region: Dict[str, Any],
    page_images: List[bytes],
    azure_pages: List[Dict[str, Any]],
    fallback_logs: List[Dict[str, Any]]
) -> Tuple[str, float]:
    """
    Performs VLM fallback for a specific field if confidence is low.
    Updates fallback_logs and returns the (possibly updated) value and confidence.
    """
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
                
                vlm_response = vlm_agent.run(prompt, images=[Image(content=crop_bytes)])
                
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
                            return vlm_val, vlm_conf
                except Exception as e:
                    print(f"Error parsing VLM response: {e}")
    except Exception as e:
        print(f"VLM Fallback Error: {e}")
        
    return value, conf
