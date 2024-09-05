function clearChat() {
    // Make an API call to send the message
    fetch(`/agents/chat/clear`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('HTTP error! Status: ${response.status}');
      }
      return response.json();
    })
   .then(data => {
      const chatOutput = document.getElementById('chat-output');
      chatOutput.innerHtml = "";
      console.log('Chat cleared successfully:', data);
    })
    .catch(error => {
      // Handle errors during the fetch or from the API
      console.error('Error clearing chat:', error);
    });
}

function sendMessage() {
    const message = document.getElementById('user-input').value;
    const model = document.getElementById('model-select').value;

    if (message.trim() === '') {
        return;
    }

    appendMessage('User', message);
    document.getElementById('user-input').value = '';

    // Make an API call to send the message
    fetch(`/agents/chat/chat_agent`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'prompt': message
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.response) {
            appendMessage(model, data.response);
        } else if (data.error) {
            appendMessage('Error', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        appendMessage('Error', 'An error occurred while processing the request.');
    });
}

function appendMessage(sender, message) {
    const chatOutput = document.getElementById('chat-output');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender === 'User' ? 'user-message' : 'agent-message');
    messageDiv.innerHTML = `<strong>${sender}:</strong><br>${formatMessage(message)}`;
    chatOutput.appendChild(messageDiv);
    chatOutput.scrollTop = chatOutput.scrollHeight;
}

function formatMessage(message) {
    if (typeof message === 'string') {
        return message.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, lang, code) => {
            const language = Prism.languages[lang] ? lang : 'python';
            return `<pre><code class="language-${language}">${Prism.highlight(code.trim(), Prism.languages[language], language)}</code></pre>`;
        });
    } else {
        return JSON.stringify(message, null, 2);
    }
}

function createTaskFlow() {
    // Implement logic to create a task flow.
    // You can use a form or any other method to collect task flow data
    // For now, we'll just add a placeholder message to the task flow container.
    const taskFlowContainer = document.getElementById('task-flow-container');
    taskFlowContainer.innerHTML += '<p>Task Flow Placeholder - Implement logic to create tasks.</p>';
}

function runTaskFlow() {
    // Implement logic to run the task flow.
    // You will need to send an API request to the '/agents/{agent_name}/tasks' endpoint
    // with the task flow data.
    const taskFlowContainer = document.getElementById('task-flow-container');
    taskFlowContainer.innerHTML += '<p>Running Task Flow Placeholder - Implement API call to run tasks.</p>';
}
