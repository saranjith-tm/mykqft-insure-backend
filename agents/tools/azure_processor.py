import re
from typing import Dict, Any, List, Optional

def _extract_field_value(field):
    """Recursively extract the value from an Azure DocumentField."""
    if not field:
        return ""
        
    field_type = getattr(field, "type", getattr(field, "value_type", None))
    
    if field_type == "array":
        arr = getattr(field, "value_array", getattr(field, "value", []))
        return [_extract_field_value(item) for item in (arr or [])]
    elif field_type == "object":
        obj = getattr(field, "value_object", getattr(field, "value", {}))
        return {k: _extract_field_value(v) for k, v in (obj or {}).items()}
    else:
        val = field.content if hasattr(field, "content") else getattr(field, "value", None)
        return val if val is not None else ""

def process_azure_result(result: Any) -> Dict[str, Any]:
    """
    Processes Azure's raw result into a structured format for the agent.
    """
    extracted_fields = []
    
    # Process Key-Value Pairs
    if hasattr(result, "key_value_pairs") and result.key_value_pairs:
        for kvp in result.key_value_pairs:
            if kvp.key and hasattr(kvp.key, "content") and kvp.value and hasattr(kvp.value, "content"):
                key = kvp.key.content.strip()
                value = kvp.value.content.strip()
                conf = kvp.confidence if hasattr(kvp, "confidence") else 0.95
                
                region = None
                if hasattr(kvp.value, "bounding_regions") and kvp.value.bounding_regions:
                    region = kvp.value.bounding_regions[0]
                
                extracted_fields.append({
                    "key": key,
                    "value": value,
                    "confidence": conf,
                    "source": "azure_kvp",
                    "region": {
                        "page_number": region.page_number,
                        "polygon": region.polygon
                    } if region else None
                })

    # Process Fields from Documents
    if hasattr(result, "documents") and result.documents:
        for doc in result.documents:
            if hasattr(doc, "fields") and doc.fields:
                for name, field in doc.fields.items():
                    value = _extract_field_value(field)
                    conf = field.confidence if hasattr(field, "confidence") else 0.95
                    
                    region = None
                    if hasattr(field, "bounding_regions") and field.bounding_regions:
                        region = field.bounding_regions[0]
                        
                    extracted_fields.append({
                        "key": name,
                        "value": value,
                        "confidence": conf,
                        "source": "azure_field",
                        "region": {
                            "page_number": region.page_number,
                            "polygon": region.polygon
                        } if region else None
                    })

    return {
        "fields": extracted_fields,
        "pages": [
            {"page_number": p.page_number, "width": p.width, "height": p.height}
            for p in getattr(result, "pages", [])
        ]
    }
