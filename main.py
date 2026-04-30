from dotenv import load_dotenv
load_dotenv() # Load env vars before anything else imports agents

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.extraction_routes import router as extraction_router

app = FastAPI(
    title="Insurance Document Extraction Server",
    description="FastAPI server for autonomous document extraction using Azure and Agno Agentic Framework",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(extraction_router)

@app.get("/")
async def root():
    return {"status": "online", "message": "Extraction Server is running with Agentic Structure"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
