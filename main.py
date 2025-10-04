from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import shutil

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

uploaded_files = {}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = f"file_{int(time.time())}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_id)

        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read content for analysis
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        uploaded_files[file_id] = {
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
            "size": uploaded_files[file_id]["size"]
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error uploading file: {str(e)}"})

@app.post("/query")
async def process_query(query: str = Form(...)):
    try:
        if not uploaded_files:
            return JSONResponse(status_code=400, content={"detail": "No file uploaded. Please upload a file first."})
        
        latest_file_id, latest_file = list(uploaded_files.items())[-1]
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

# Clear history & delete all files
@app.post("/clear")
async def clear_history():
    try:
        # Delete all files in UPLOAD_DIR
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Clear memory
        uploaded_files.clear()

        return {"message": "Upload history cleared successfully. All files deleted from uploads folder."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error clearing history: {str(e)}"})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DevOps Cloud Query System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)