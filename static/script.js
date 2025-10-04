// script.js

async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Show success message
            document.getElementById('successMessage').style.display = 'block';
            setTimeout(() => {
                document.getElementById('successMessage').style.display = 'none';
            }, 3000);

            // Show file details
            document.getElementById('fileDetails').style.display = 'block';
            document.getElementById('fileName').textContent = data.filename;
            document.getElementById('fileType').textContent = data.content_type;
            document.getElementById('fileSize').textContent = formatBytes(data.size);
            document.getElementById('uploadTime').textContent = new Date().toLocaleString();

            // Show query section
            document.getElementById('querySection').style.display = 'block';
        } else {
            alert('Upload failed: ' + data.detail);
        }
    } catch (error) {
        alert('Error uploading file: ' + error.message);
    }
}

async function submitQuery() {
    const query = document.getElementById('queryInput').value.trim();
    
    if (!query) {
        alert('Please enter a query');
        return;
    }

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('responseSection').style.display = 'none';

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${encodeURIComponent(query)}`
        });

        const data = await response.json();

        // Hide loading
        document.getElementById('loading').style.display = 'none';

        if (response.ok) {
            // Show response
            document.getElementById('responseSection').style.display = 'block';
            document.getElementById('responseContent').textContent = data.response;
            
            // Scroll to response
            document.getElementById('responseSection').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        } else {
            alert('Query failed: ' + data.detail);
        }
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        alert('Error processing query: ' + error.message);
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Allow Ctrl+Enter to submit query
document.addEventListener('DOMContentLoaded', function() {
    const queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                submitQuery();
            }
        });
    }
});

// Select history container
const responseHistory = document.getElementById("responseHistory");

// Initialize history (cleared on page refresh automatically)
let history = [];

// Function to render history in UI
function renderHistory() {
  responseHistory.innerHTML = history
    .map((item, idx) => `
      <div class="history-item">
        <strong>Query ${idx + 1}:</strong> ${item.query}<br>
        <strong>Response:</strong> ${item.response}
      </div>
    `)
    .join("<hr>");
}

// Modify query submission success
document.getElementById("queryForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const queryInput = document.getElementById("queryInput");
  const query = queryInput.value.trim();
  if (!query) return;

  const responseBox = document.getElementById("queryResponse");
  responseBox.textContent = "Processing...";

  try {
    const response = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    const data = await response.json();

    // Update current response
    responseBox.textContent = data.response;

    // Save to history
    history.push({ query, response: data.response });
    renderHistory();

  } catch (error) {
    responseBox.textContent = "Error: " + error.message;
  }
});
