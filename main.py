from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import time
import shutil
import re
from typing import Optional

app = FastAPI(title="DevOps Cloud Query System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static files (css/js)
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global structures
session_data = {}       # filename -> metadata (content, size, etc.)
session_uploaded = {}   # session_id -> filename

# Initialize file counter from existing files (so we don't overwrite)
def init_file_counter():
    max_n = 0
    for fname in os.listdir(UPLOAD_DIR):
        m = re.match(r"^File(\d+)(\..+)?$", fname)
        if m:
            try:
                n = int(m.group(1))
                if n > max_n:
                    max_n = n
            except Exception:
                pass
    return max_n

file_counter = init_file_counter()

def next_filename(ext: str):
    global file_counter
    file_counter += 1
    return f"File{file_counter}{ext}"

class QueryRequest(BaseModel):
    query: str
    session_id: str

class ClearRequest(BaseModel):
    session_id: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), session_id: str = Form(...)):
    """
    Saves files directly into uploads/ as File1.ext, File2.ext, ...
    Enforces: one upload per session_id (prevents multiple uploads from same page load).
    """
    try:
        # Backend guard: one upload per session
        if session_id in session_uploaded:
            return JSONResponse(
                status_code=400,
                content={"detail": "This session already uploaded a file. Reload page or clear to upload again."}
            )

        # Safely handle filename and extension
        original_name = file.filename or ""
        _, ext = os.path.splitext(original_name)
        if ext is None:
            ext = ""

        new_name = next_filename(ext)
        file_path = os.path.join(UPLOAD_DIR, new_name)

        # Save file bytes
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read content for basic analysis (text read only, ignore errors)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            content = ""

        # Size in bytes (real file size)
        try:
            size_bytes = os.path.getsize(file_path)
        except Exception:
            size_bytes = len(content.encode("utf-8", errors="ignore"))

        # Save metadata
        session_data[new_name] = {
            "filename": new_name,
            "filepath": file_path,
            "content_type": file.content_type,
            "size": size_bytes,
            "content": content,
            "timestamp": time.time()
        }

        # mark this session as already uploaded
        session_uploaded[session_id] = new_name

        return JSONResponse({
            "message": "File uploaded successfully",
            "filename": new_name,
            "content_type": file.content_type,
            "size": size_bytes
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error uploading file: {str(e)}"})

@app.post("/query")
async def process_query(request: QueryRequest):
    try:
        session_id = request.session_id
        query = request.query

        # Prefer file uploaded in this session
        latest_file = None
        if session_id in session_uploaded:
            fname = session_uploaded.get(session_id)
            latest_file = session_data.get(fname)
            if not latest_file:
                # fall back to global latest if metadata missing
                latest_file = None

        if not latest_file:
            # If no session-specific file, use the most recent global file
            if not session_data:
                return JSONResponse(status_code=400, content={"detail": "No file uploaded. Please upload a file first."})
            latest_name = list(session_data.keys())[-1]
            latest_file = session_data.get(latest_name)

        if not latest_file:
            return JSONResponse(status_code=400, content={"detail": "No valid file found. Please upload a file again."})

        file_content = latest_file.get("content", "")

        response = f"""Query: {query}

File Analysis:
--------------
Filename: {latest_file['filename']}
File Size: {latest_file['size']} bytes

Sample Analysis:
• Total lines in file: {len(file_content.splitlines())}
• File contains configuration/log data that can be analyzed
• Query processed successfully

Response:
---------
Based on your query \"{query}\", here are the findings from the uploaded file:

{file_content[:500]}...

(This is a demo response. In production, this would use an NLP/AI component.)
"""
        return JSONResponse({
            "response": response,
            "query": query,
            "file_analyzed": latest_file["filename"]
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error processing query: {str(e)}"})

@app.post("/clear")
async def clear_history(request: ClearRequest):
    """
    Clear all uploaded files and reset server state.
    """
    try:
        deleted_count = 0
        for fname in os.listdir(UPLOAD_DIR):
            item_path = os.path.join(UPLOAD_DIR, fname)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    deleted_count += 1
            except Exception:
                pass

        session_data.clear()
        session_uploaded.clear()
        global file_counter
        file_counter = 0

        return {"message": f"Upload history cleared successfully. Deleted {deleted_count} files."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error clearing history: {str(e)}"})

@app.post("/cleanup-all")
async def cleanup_all_sessions():
    """
    Called on page load to ensure a fresh start (deletes all files).
    """
    try:
        deleted_count = 0
        for fname in os.listdir(UPLOAD_DIR):
            item_path = os.path.join(UPLOAD_DIR, fname)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    deleted_count += 1
            except Exception:
                pass

        session_data.clear()
        session_uploaded.clear()
        global file_counter
        file_counter = 0

        return {
            "message": f"All files cleaned up successfully. Removed {deleted_count} items.",
            "deleted_count": deleted_count
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error cleaning up all sessions: {str(e)}"})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DevOps Cloud Query System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
