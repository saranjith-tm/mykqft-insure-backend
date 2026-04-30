# Insurance Document Extraction Server (Agentic Framework)

This is a high-performance, modular FastAPI server designed for autonomous document extraction from insurance forms, ID cards, and other documents. It combines the precision of **Azure Document Intelligence** with the reasoning power of the **Agno (Phidata) Agentic Framework**.

## 🚀 Features

- **Multi-Layer Extraction**: Uses Azure Document Intelligence as the primary extraction engine.
- **Agentic VLM Fallback**: Automatically triggers a specialized Vision-Language Model (VLM) agent when Azure's confidence scores fall below 0.80.
- **Vision-Grounded Reasoning**: The VLM agent analyzes high-resolution, enhanced crops of document regions to verify and correct data.
- **Flexible LLM Support**: Support for OpenRouter, OpenAI, and Google (Gemini) providers, configurable entirely via environment variables.
- **Modular Architecture**: Clean separation between agents, tools, services, and routes for maximum maintainability.
- **FastAPI Powered**: High-performance asynchronous API endpoints.

---

## 🏗️ Project Architecture

The codebase follows a structured, modular design:

- **`agents/`**:
    - `orchestrator_agent.py`: Orchestrates the overall extraction flow.
    - `vlm_specialist_agent.py`: Specialist agent for visual verification.
    - **`prompts/`**: Centralized agent instructions and prompts.
    - **`tools/`**: Specialized tools for Azure API, PDF processing, and Image manipulation.
    - **`llm_clients/`**: Model factories supporting multiple providers (OpenRouter, OpenAI, Google).
- **`services/`**: Core business logic (`ExtractionService`) that bridges agents and tools.
- **`routes/`**: API endpoint definitions.
- **`main.py`**: Server entry point and application initialization.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
Ensure you have **UV** installed (the ultra-fast Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:

```env
# Azure Document Intelligence Configuration
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_endpoint
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key
AZURE_DOCUMENT_INTELLIGENCE_MODEL_ID=your_model_id (e.g., prebuilt-document)

# LLM Configuration
LLM_PROVIDER=openrouter  # options: openrouter, openai, google
LLM_MODEL_KEY=your_llm_api_key
LLM_MODEL=openai/gpt-4o  # or your preferred model
```

### 3. Install Dependencies
```bash
uv sync
```

---

## 🚦 Running the Server

Start the FastAPI server using UV:

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at `http://localhost:8000`. You can access the interactive Swagger documentation at `http://localhost:8000/docs`.

---

## 📡 API Documentation

### `POST /extract`

Extract data from a document (PDF or Image).

**Request Parameters (Multipart/Form-Data):**
- `file`: The document file (PDF, PNG, JPG, etc.).
- `use_vlm_fallback`: (Optional, Boolean) Whether to use the Agentic VLM for low-confidence fields. Default: `true`.

**Example Usage (cURL):**
```bash
curl -X POST "http://localhost:8000/extract" \
     -F "file=@/path/to/document.pdf" \
     -F "use_vlm_fallback=true"
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "field_name": "extracted_value",
    "extraction_confidence": 0.92,
    "_field_confidences": { ... }
  },
  "page_images_count": 1,
  "fallback_logs": [
    {
      "field": "policy_number",
      "azure_val": "123-X",
      "azure_conf": 0.45,
      "vlm_val": "123-Y",
      "vlm_conf": 0.95,
      "selected": "vlm"
    }
  ]
}
```

---

## 🧪 Testing

You can use the provided Swagger UI (`/docs`) to upload files and see the agentic fallback logs in real-time. The logs will detail exactly which fields were corrected by the VLM agent.
# mykqft-insure-backend
