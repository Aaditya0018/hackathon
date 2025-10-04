from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time

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

uploaded_files = {}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_id = f"file_{int(time.time())}"
        uploaded_files[file_id] = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "content": content.decode('utf-8', errors='ignore'),
            "timestamp": time.time()
        }
        return JSONResponse({
            "message": "File uploaded successfully",
            "file_id": file_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content)
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error uploading file: {str(e)}"})

@app.post("/query")
async def process_query(query: str = Form(...)):
    try:
        if not uploaded_files:
            return JSONResponse(status_code=400, content={"detail": "No file uploaded. Please upload a file first."})
        
        latest_file = list(uploaded_files.values())[-1]
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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DevOps Cloud Query System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)