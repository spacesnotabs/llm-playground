const socket = io();
const chatBox = document.getElementById('chat-box');
const directoryExplorer = document.getElementById('directory-explorer');
let treeView;

document.getElementById('send-btn').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    const message = input.value;
    marked.use({gfm: true, breaks: false});
    chatBox.innerHTML += `<div class="user-message"><span>User:</span> ${marked.parse(message)}</div>`;
    input.value = '';

    let filePaths = new Set();
    if (treeView) {
        files = treeView.getSelectedNodes();
        root = treeView.getRoot();
        files.forEach(node => {
            const path = new TreePath(root, node);
            const parts = path.getPath();
            let fullPath = '.';
            parts.forEach(part => {
                fullPath = fullPath + "/" + part.getUserObject();
            })
            console.log('fullPath=' + fullPath);
            filePaths.add(fullPath);
        })
    }

    let contextFiles = new Set();
    socket.emit('send_message', {
        user_input:message,
        files_to_modify: Array.from(filePaths),
        context_files: Array.from(contextFiles)
    });
});

document.getElementById('clear-btn').addEventListener('click', function() {
    chatBox.innerHTML = '';
    socket.emit('clear_history');
});

document.getElementById('set-model-btn').addEventListener('click', function() {
    const model = document.getElementById('model-select').value;
    fetch('/set_model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model })
    });
});

document.getElementById('load-directory-btn').addEventListener('click', function() {
    const directoryPath = document.getElementById('directory-path').value;
    loadDirectory(directoryPath);
});

function loadDirectory(path) {
    return fetch('/get_directory_contents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory: path })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return null;
        }

        function buildTreeNode(item) {
            const node = new TreeNode(item.name);
            if (item.type === 'folder' && Array.isArray(item.children)) {
                item.children.forEach(child => {
                    node.addChild(buildTreeNode(child));
                });
            }
            return node;
        }

        const root = buildTreeNode(data);

        if (treeView) {
            treeView.setRoot(root);
            treeView.reload();
        } else {
            treeView = new TreeView(root, directoryExplorer);
            treeView.reload();
        }

        return data;
    })
    .catch(error => {
        console.error('Error:', error);
        return null;
    });
}

let currentAgentResponse = null;

socket.on('post_message', function (data) {
    displayPrompt(data);
});

function displayPrompt(data) {
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
        if (data.system == true) {
            // received a system message
            systemResponse = document.createElement('div');
            systemResponse.classList.add("system-message");
            marked.use({gfm: true, breaks: false});
            systemResponse.innerHTML = marked.parse(data.response);
            chatBox.appendChild(systemResponse);
        } else {
            if (!currentAgentResponse) {
                currentAgentResponse = document.createElement('div');
                currentAgentResponse.classList.add("agent-message");
                currentAgentResponse.innerHTML = `<span>Agent:</span> `;
                chatBox.appendChild(currentAgentResponse);
            }

//            let formattedResponse = marked.parse(data.response);
//            currentAgentResponse.insertAdjacentHTML('beforeend', formattedResponse);
            currentAgentResponse.insertAdjacentHTML('beforeend', data.response);

        }
        // Keep scrolling the chat box down
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    chatBox.scrollTop = chatBox.scrollHeight;
};

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
