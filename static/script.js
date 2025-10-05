// Session Management - Generates new session on every page load
function getSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

let currentSessionId = null;

document.addEventListener('DOMContentLoaded', async function() {
    currentSessionId = getSessionId();
    console.log('🔵 New Session Started:', currentSessionId);

    // Cleanup server-side to ensure fresh state (optional)
    try {
        const response = await fetch('/cleanup-all', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        const data = await response.json();
        console.log('🧹 cleanup-all:', data);
    } catch (err) {
        console.error('Error calling cleanup-all:', err);
    }

    const queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) submitQuery();
        });
        queryInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
});

// Called from HTML upload-zone onclick
function onZoneClick() {
    const zone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    // If disabled, don't open file dialog
    if (zone.classList.contains('disabled') || fileInput.disabled) return;
    fileInput.click();
}

async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const zone = document.getElementById('uploadZone');

    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert('Please select a file');
        return;
    }

    // If already disabled, safeguard
    if (fileInput.disabled || zone.classList.contains('disabled')) {
        alert('File already uploaded for this session. Reload or clear to upload again.');
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', currentSessionId);

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        const data = await response.json();

        if (response.ok) {
            // UI updates
            const successMessage = document.getElementById('successMessage');
            successMessage.style.display = 'block';
            setTimeout(() => { successMessage.style.display = 'none'; }, 2500);

            document.getElementById('fileDetails').style.display = 'block';
            document.getElementById('fileName').textContent = data.filename;
            document.getElementById('fileType').textContent = data.content_type || '-';
            document.getElementById('fileSize').textContent = formatBytes(data.size || 0);
            document.getElementById('uploadTime').textContent = new Date().toLocaleString();

            document.getElementById('chatContainer').style.display = 'block';
            clearChatUI();

            // Disable further uploads (frontend)
            fileInput.disabled = true;
            zone.classList.add('disabled');
            document.getElementById('uploadNotice').style.display = 'block';
        } else {
            alert('Upload failed: ' + (data.detail || JSON.stringify(data)));
        }
    } catch (error) {
        alert('Error uploading file: ' + error.message);
    }
}

async function submitQuery() {
    const query = document.getElementById('queryInput').value.trim();
    if (!query) { alert('Please enter a query'); return; }

    const askBtn = document.getElementById('askBtn');
    askBtn.disabled = true; askBtn.classList.add('loading');

    addMessageToChat(query, 'user');
    document.getElementById('queryInput').value = '';
    const loadingId = addLoadingMessage();

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, session_id: currentSessionId })
        });
        const data = await response.json();
        removeLoadingMessage(loadingId);

        if (response.ok) addMessageToChat(data.response, 'assistant');
        else alert('Query failed: ' + (data.detail || JSON.stringify(data)));
    } catch (error) {
        removeLoadingMessage(loadingId);
        alert('Error processing query: ' + error.message);
    } finally {
        askBtn.disabled = false; askBtn.classList.remove('loading');
    }
}

function addMessageToChat(content, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const emptyState = chatMessages.querySelector('.empty-chat-state');
    if (emptyState) emptyState.remove();

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
    if (loadingDiv) loadingDiv.remove();
}

async function clearHistory() {
    if (!confirm('Are you sure you want to clear chat history and uploaded files?')) return;

    try {
        const response = await fetch('/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId })
        });
        const data = await response.json();

        if (response.ok) {
            clearChatUI();
            document.getElementById('chatContainer').style.display = 'none';
            document.getElementById('fileDetails').style.display = 'none';
            document.getElementById('fileName').textContent = '-';
            document.getElementById('fileType').textContent = '-';
            document.getElementById('fileSize').textContent = '-';
            document.getElementById('uploadTime').textContent = '-';

            // re-enable upload input
            const fileInput = document.getElementById('fileInput');
            const zone = document.getElementById('uploadZone');
            fileInput.value = '';
            fileInput.disabled = false;
            zone.classList.remove('disabled');
            document.getElementById('uploadNotice').style.display = 'none';

            alert(data.message);
        } else {
            alert('Failed to clear history: ' + (data.detail || JSON.stringify(data)));
        }
    } catch (error) {
        alert('Error clearing history: ' + error.message);
    }
}

function clearChatUI() {
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
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}
