from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import time
import shutil
from typing import Optional

app = FastAPI(title="DevOps Cloud Query System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store session data in memory
session_data = {}

class QueryRequest(BaseModel):
    query: str
    session_id: str

class ClearRequest(BaseModel):
    session_id: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), session_id: str = Form(...)):
    try:
        # Create session-specific directory
        session_dir = os.path.join(UPLOAD_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        file_id = f"file_{int(time.time())}_{file.filename}"
        file_path = os.path.join(session_dir, file_id)

        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read content for analysis
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Store in session data
        if session_id not in session_data:
            session_data[session_id] = {}
        
        session_data[session_id][file_id] = {
            "filename": file.filename,
            "filepath": file_path,
            "content_type": file.content_type,
            "size": len(content.encode("utf-8", errors="ignore")),
            "content": content,
            "timestamp": time.time()
        }

        return JSONResponse({
            "message": "File uploaded successfully",
            "file_id": file_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": session_data[session_id][file_id]["size"]
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error uploading file: {str(e)}"})

@app.post("/query")
async def process_query(request: QueryRequest):
    try:
        session_id = request.session_id
        query = request.query

        if session_id not in session_data or not session_data[session_id]:
            return JSONResponse(status_code=400, content={"detail": "No file uploaded. Please upload a file first."})
        
        # Get the latest file for this session
        latest_file_id = list(session_data[session_id].keys())[-1]
        latest_file = session_data[session_id][latest_file_id]
        file_content = latest_file["content"]

        response = f"""Query: {query}

File Analysis:
--------------
Filename: {latest_file['filename']}
File Size: {latest_file['size']} bytes

Sample Analysis:
• Total lines in file: {len(file_content.splitlines())}
• File contains configuration data that can be analyzed
• Query processed successfully

Response:
---------
Based on your query "{query}", here are the findings from the uploaded file:

{file_content[:500]}...

(This is a demo response. In production, this would use NLP/AI to provide intelligent answers.)
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
    """Manual clear button - clears current session only"""
    try:
        session_id = request.session_id
        session_dir = os.path.join(UPLOAD_DIR, session_id)

        # Delete session directory and all files
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)

        # Clear session data from memory
        if session_id in session_data:
            del session_data[session_id]

        return {"message": "Upload history cleared successfully. All files deleted from your session."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error clearing history: {str(e)}"})

@app.post("/cleanup-all")
async def cleanup_all_sessions():
    """
    Called when page loads/refreshes. 
    Deletes ALL session folders and clears all memory.
    This ensures every page refresh starts completely fresh.
    """
    try:
        deleted_count = 0
        
        # Delete entire uploads directory and recreate it
        if os.path.exists(UPLOAD_DIR):
            # Get all items in uploads directory
            for item in os.listdir(UPLOAD_DIR):
                item_path = os.path.join(UPLOAD_DIR, item)
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        deleted_count += 1
                    elif os.path.isfile(item_path):
                        os.remove(item_path)
                        deleted_count += 1
                except Exception as e:
                    print(f"Error removing {item_path}: {e}")
        
        # Clear all session data from memory
        session_data.clear()
        
        return {
            "message": f"All sessions cleaned up successfully. Removed {deleted_count} items.",
            "deleted_count": deleted_count
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error cleaning up all sessions: {str(e)}"})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DevOps Cloud Query System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)