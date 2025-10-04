# DevOps Cloud Query System

A stunning, hackathon-ready web application with DevOps/Kubernetes theme for uploading files and querying them intelligently.

## 📁 Project Structure

```
devops-query-app/
├── main.py                 # FastAPI backend
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # HTML template
├── static/
│   ├── style.css          # CSS styles
│   └── script.js          # JavaScript functionality
└── README.md              # This file
```

## 🚀 Setup Instructions

### 1. Create Project Structure

```bash
mkdir devops-query-app
cd devops-query-app
mkdir templates static
```

### 2. Copy Files

Copy the following files to their respective locations:
- `main.py` → Root directory
- `requirements.txt` → Root directory
- `index.html` → `templates/` folder
- `style.css` → `static/` folder
- `script.js` → `static/` folder

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install fastapi uvicorn python-multipart
```

### 4. Run the Application

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## ✨ Features

- **Eye-Catching UI**: Cyberpunk-themed design with animated backgrounds
- **File Upload**: Drag-and-drop support for any file type
- **File Analysis**: Displays file metadata (name, type, size, timestamp)
- **Query Interface**: Ask questions about your uploaded files
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Feedback**: Loading states and success messages

## 🎯 How to Use

1. **Upload a File**: Click the upload zone or drag a file (YAML, JSON, TXT, LOG, etc.)
2. **View Details**: File information is automatically displayed
3. **Enter Query**: Type your question in the text area
4. **Get Response**: Click "Ask Question" to process and view results

## 🛠️ Customization

### Modify Colors
Edit `static/style.css` to change the color scheme:
- Primary: `#00f5ff` (Cyan)
- Secondary: `#00ff88` (Green)
- Background: `#0f2027` to `#2c5364` (Dark gradient)

### Add AI Integration
Replace the mock response in `main.py` `/query` endpoint with:
- OpenAI API
- Anthropic Claude API
- Local