import os
import uuid
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

from pdf_service import generate_pdf_with_progress

app = FastAPI(title="Markdown PDF Export Service")

# Allow CORS for local development and frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

class ExportRequest(BaseModel):
    html: str
    theme: str
    filename: str
    styles: Optional[str] = ""

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

async def cleanup_file_after_delay(file_path: str, delay: int = 300):
    """Delete a temporary file after a certain delay (default 5 minutes)."""
    await asyncio.sleep(delay)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {e}")

@app.post("/api/export/pdf")
async def export_pdf(request: ExportRequest, background_tasks: BackgroundTasks):
    file_id = str(uuid.uuid4())
    pdf_filename = f"{request.filename}_{file_id}.pdf"
    pdf_path = os.path.join(TEMP_DIR, pdf_filename)

    async def event_generator():
        try:
            # Yield initial stage
            yield f"data: {json.dumps({'progress': 5, 'stage': 'Starting', 'detail': 'Initializing backend browser...'})}\n\n"
            await asyncio.sleep(0.1)

            # We pass a progress callback to our generator service
            async for progress_update in generate_pdf_with_progress(
                html_content=request.html,
                theme=request.theme,
                pdf_path=pdf_path,
                custom_styles=request.styles,
                title=request.filename.replace("_", " ")
            ):
                yield f"data: {json.dumps(progress_update)}\n\n"
                await asyncio.sleep(0.05)

            # Check if file was successfully generated
            if os.path.exists(pdf_path):
                # Schedule cleanup in background tasks
                background_tasks.add_task(cleanup_file_after_delay, pdf_path, 300)
                download_url = f"/api/download/{pdf_filename}"
                yield f"data: {json.dumps({'progress': 100, 'stage': 'Complete', 'detail': 'PDF generated successfully!', 'download_url': download_url})}\n\n"
            else:
                yield f"data: {json.dumps({'progress': 100, 'error': 'PDF generation completed but file was not found.'})}\n\n"

        except Exception as e:
            print(f"Error in PDF generation stream: {e}")
            yield f"data: {json.dumps({'progress': 100, 'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    # Security check to prevent directory traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(TEMP_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or has expired")

    return FileResponse(
        path=file_path,
        filename=safe_filename.split("_")[0] + ".pdf",
        media_type="application/pdf"
    )
