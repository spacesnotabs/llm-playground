const socket = io();
const chatBox = document.getElementById('chat-box');
const directoryExplorer = document.getElementById('directory-explorer');
const fileHolder = document.getElementById('file_holder'); // Get the file_holder element
let treeView;
let selectedFiles = new Set(); // Store selected file names

function clearChatBox() {
    chatBox.innerHTML = ""
}

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
            let fullPath = '';
            parts.forEach(part => {
                fullPath = fullPath + part.getUserObject() + '\\';
            })
            console.log('fullPath=' + fullPath);
            filePaths.add(fullPath);
        })
    }

    let contextFiles = new Set();
    // Send the first selected file in "files_to_modify" and the rest in "context_files"
    let firstFile = null;
    filePaths.forEach(file => {
        if (!firstFile) {
            firstFile = file;
        } else {
            contextFiles.add(file);
        }
    });

    socket.emit('send_message', {
        user_input:message,
        files_to_modify: [firstFile], // Send first selected file
        context_files: Array.from(contextFiles)
    });
});

document.getElementById('clear-btn').addEventListener('click', function() {
    clearChatBox();
    socket.emit('clear_history');
});

document.getElementById('start-workflow-btn').addEventListener('click', function() {
    clearChatBox();
    socket.emit('start_workflow');
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
    console.log(directoryPath)
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

        function buildTreeNode(item, parentNode) {
            // Ignore folders starting with a period
            if (item.type === 'folder' && item.name.startsWith('.')) {
                return null; // Skip building the node
            }

            const node = new TreeNode(item.name, parentNode);
            if (item.type === 'folder' && Array.isArray(item.children)) {
                item.children.forEach(child => {
                    const childNode = buildTreeNode(child, node);
                    if (childNode) { // Only add if not null (skipped hidden folder)
                        node.addChild(childNode);
                        childNode.on('select', (node) => {
                            const fileName = node.getUserObject();
                            selectedFiles.add(fileName); // Add to selected files
                            const span = document.createElement('span');
                            span.textContent = fileName;
                            span.classList.add('file-span'); // Add the file-span class
                            fileHolder.appendChild(span); // Add filename to file_holder div
                        })
                        childNode.on('deselect', (node) => {
                            const fileName = node.getUserObject();
                            selectedFiles.delete(fileName); // Remove from selected files
                            const spans = fileHolder.querySelectorAll('span');
                            spans.forEach(span => {
                                if (span.textContent === fileName) {
                                    span.remove();
                                }
                            });
                        })
                    }
                });
            }
            return node;
        }

        const root = buildTreeNode(data, null);

        if (treeView) {
            // Check if the root is null before setting it
            if (root) {
                treeView.setRoot(root);
                treeView.reload();
            } else {
                console.error("Error: Root node is null. Check directory structure.");
            }

            treeView.collapseAllNodes();
        } else {
            treeView = new TreeView(root, directoryExplorer);
            treeView.reload();
            // Collapse all nodes
        }

        return data;
    })
    .catch(error => {
        console.error('Error:', error);
        return null;
    });
}

let currentAgentResponse = null;

/* Socket Listeners */
socket.on('post_message', function (data) {
    displayPrompt(data);
});

socket.on('model_changed', function(data) {
    clearChatBox();
});

function displayPrompt(data) {
    if (data.end === true) {
        if (currentAgentResponse) {
            currentAgentResponse.classList.add("complete");
            console.log(currentAgentResponse.innerHTML);
            currentText = currentAgentResponse.innerHTML;

            // replace code blocks with correct tags
            currentText = currentText.replace(/```(\w+)? ([\s\S]*?)```/g, (match, lang, code) => {
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