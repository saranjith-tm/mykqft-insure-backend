import os
from typing import Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

def extract_with_azure(
    file_bytes: bytes, 
    model_id: str = "prebuilt-document"
) -> Dict[str, Any]:
    """
    Analyzes a document using Azure Document Intelligence.
    Returns the raw result object from Azure.
    """
    azure_endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    azure_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    
    if not azure_endpoint or not azure_key:
        raise ValueError("Azure credentials not configured")

    client = DocumentIntelligenceClient(
        endpoint=azure_endpoint,
        credential=AzureKeyCredential(azure_key)
    )

    poller = client.begin_analyze_document(
        model_id,
        body=file_bytes,
        content_type="application/octet-stream" # Works for both PDF and Images
    )
    return poller.result()
