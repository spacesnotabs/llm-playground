const socket = io();
const chatBox = document.getElementById('chat-box');

document.getElementById('send-btn').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    const message = input.value;
    chatBox.innerHTML += `<div class="user-message"><span>User:</span> ${message}</div>`;
    input.value = '';
    socket.emit('send_message', { message });
});

document.getElementById('set-model-btn').addEventListener('click', function() {
    const model = document.getElementById('model-select').value;
    fetch('/set_model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model })
    });
});

let currentAgentResponse = null;

socket.on('receive_message', function (data) {
    if (data.end === true) {
        if (currentAgentResponse) {
            currentAgentResponse.classList.add("complete");
            console.log(currentAgentResponse.innerHTML);
            currentText = currentAgentResponse.innerHTML;

            // replace code blocks with correct tags
            currentText = currentText.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
              return `<pre><code class="language-${lang || ''}">${escapeHtml(code.trim())}</code></pre>`;
            });
            currentAgentResponse.innerHTML = currentText;

            marked.use({gfm: true, breaks: false});
            currentAgentResponse.innerHTML = marked.parse(currentText);

            // Apply syntax highlighting
            document.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });

            currentAgentResponse = null;
        }
    } else {
        if (!currentAgentResponse) {
            currentAgentResponse = document.createElement('div');
            currentAgentResponse.classList.add("agent-message");
            currentAgentResponse.innerHTML = `<span>Agent:</span> `;
            chatBox.appendChild(currentAgentResponse);
        }

        let formattedResponse = data.response;
        currentAgentResponse.insertAdjacentHTML('beforeend', formattedResponse)

        // Keep scrolling the chat box down
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    chatBox.scrollTop = chatBox.scrollHeight;
});

// Function to escape HTML characters inside code blocks (for markdown-style)
function escapeHtml(unsafe) {
    return unsafe.replace(/[&<"']/g, function (m) {
        switch (m) {
            case '&':
                return '&amp;';
            case '<':
                return '&lt;';
            case '>':
                return '&gt;';
            case '"':
                return '&quot;';
            case "'":
                return '&#039;';
        }
    });
}
