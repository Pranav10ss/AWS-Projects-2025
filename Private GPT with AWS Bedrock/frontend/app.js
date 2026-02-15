// Replace this with your API Gateway endpoint after deployment
// You'll get this URL from Terraform output after running: terraform output api_url
const API_ENDPOINT = window.APP_CONFIG.API_ENDPOINT;;

function addMessage(content, type = 'assistant', citations = null) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    if (citations && citations.length > 0) {
        const citationsDiv = document.createElement('div');
        citationsDiv.className = 'citations';
        citationsDiv.innerHTML = '<strong>Sources:</strong> ' + citations.length + ' reference(s) found';
        contentDiv.appendChild(citationsDiv);
    }
    
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function setLoading(isLoading) {
    const button = document.getElementById('sendButton');
    const buttonText = document.getElementById('buttonText');
    const buttonLoader = document.getElementById('buttonLoader');
    const input = document.getElementById('queryInput');
    
    button.disabled = isLoading;
    input.disabled = isLoading;
    
    if (isLoading) {
        buttonText.style.display = 'none';
        buttonLoader.style.display = 'inline-block';
    } else {
        buttonText.style.display = 'inline';
        buttonLoader.style.display = 'none';
    }
}

async function sendQuery() {
    const input = document.getElementById('queryInput');
    const query = input.value.trim();
    
    if (!query) {
        return;
    }
    
    // Check if API endpoint is configured
    if (API_ENDPOINT.includes('YOUR_API_ENDPOINT_HERE')) {
        addMessage('Please configure your API endpoint in app.js after deploying the infrastructure.', 'error');
        return;
    }
    
    // Add user message
    addMessage(query, 'user');
    input.value = '';
    
    setLoading(true);
    
    try {
        console.log('Sending request to:', API_ENDPOINT);
        console.log('Query:', query);
        
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (response.ok) {
            addMessage(data.answer, 'assistant', data.citations);
        } else {
            addMessage(`Error: ${data.error || 'Unknown error occurred'}`, 'error');
        }
    } catch (error) {
        console.error('Fetch error:', error);
        addMessage(`Error: ${error.message}. Please check the browser console for details.`, 'error');
    } finally {
        setLoading(false);
    }
}

function setQuery(text) {
    document.getElementById('queryInput').value = text;
    document.getElementById('queryInput').focus();
}

// Allow Enter to send (Shift+Enter for new line)
document.getElementById('queryInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendQuery();
    }
});

// Welcome message
window.addEventListener('load', function() {
    addMessage('Hello! I\'m your AWS Solutions Architect Professional (SAP-C02) exam assistant. Ask me anything about the exam!', 'assistant');
});