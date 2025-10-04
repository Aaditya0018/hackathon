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

            // Show chat container
            document.getElementById('chatContainer').style.display = 'block';
            
            // Clear any existing messages
            clearChatMessages();
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

    const askBtn = document.getElementById('askBtn');
    const queryInput = document.getElementById('queryInput');
    
    // Disable button and show loader
    askBtn.disabled = true;
    askBtn.classList.add('loading');
    
    // Add user message to chat
    addMessageToChat(query, 'user');
    
    // Clear input
    queryInput.value = '';
    
    // Show loading indicator
    const loadingId = addLoadingMessage();

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `query=${encodeURIComponent(query)}`
        });

        const data = await response.json();

        // Remove loading indicator
        removeLoadingMessage(loadingId);

        if (response.ok) {
            // Add assistant response to chat
            addMessageToChat(data.response, 'assistant');
        } else {
            alert('Query failed: ' + data.detail);
        }
    } catch (error) {
        removeLoadingMessage(loadingId);
        alert('Error processing query: ' + error.message);
    } finally {
        // Re-enable button and hide loader
        askBtn.disabled = false;
        askBtn.classList.remove('loading');
    }
}

function addMessageToChat(content, sender) {
    const chatMessages = document.getElementById('chatMessages');
    
    // Remove empty state if it exists
    const emptyState = chatMessages.querySelector('.empty-chat-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message-bubble', `message-${sender}`);
    
    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const headerText = sender === 'user' ? 'You' : 'Assistant';
    
    messageDiv.innerHTML = `
        <div class="message-header">${headerText}</div>
        <div class="message-content">${escapeHtml(content)}</div>
        <div class="message-time">${timeString}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addLoadingMessage() {
    const chatMessages = document.getElementById('chatMessages');
    
    const loadingDiv = document.createElement('div');
    const loadingId = `loading-${Date.now()}`;
    loadingDiv.id = loadingId;
    loadingDiv.classList.add('message-bubble', 'message-loading');
    
    loadingDiv.innerHTML = `
        <div class="message-header">Assistant</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            <span style="margin-left: 10px; color: #00f5ff;">Thinking...</span>
        </div>
    `;
    
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return loadingId;
}

function removeLoadingMessage(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        clearChatMessages();
        
        // Add empty state back
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="empty-chat-state">
                <div class="empty-icon">💬</div>
                <p>Start a conversation by asking a question about your uploaded file</p>
            </div>
        `;
    }
}

function clearChatMessages() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="empty-chat-state">
            <div class="empty-icon">💬</div>
            <p>Start a conversation by asking a question about your uploaded file</p>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

document.addEventListener('DOMContentLoaded', function() {
    const queryInput = document.getElementById('queryInput');
    if (queryInput) {
        // Submit on Ctrl+Enter
        queryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                submitQuery();
            }
        });
        
        // Auto-resize textarea
        queryInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
});