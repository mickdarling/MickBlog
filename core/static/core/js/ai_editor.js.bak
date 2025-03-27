/* AI Editor JavaScript */
// We'll use both jQuery and vanilla JS to be safe
(function() {
    console.log('AI Editor JS starting...');
    
    // Wait for DOM to be loaded
    document.addEventListener('DOMContentLoaded', function() {
        console.log('AI Editor: DOM content loaded, starting initialization');
        initAIEditor();
    });
    
    // Function to initialize the AI editor
    function initAIEditor() {
        console.log('AI Editor: Initializing...');
        
        // DOM elements
        const chatMessages = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');
        const sendButton = document.getElementById('sendButton');
        const generateConfigButton = document.getElementById('generateConfigButton');
        const applyChangesButton = document.getElementById('applyChangesButton');
        const undoChangesButton = document.getElementById('undoChangesButton');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const configEditor = document.getElementById('configEditor');
        
        // Store the original configuration for undo functionality
        let originalConfig = configEditor ? configEditor.value : '';
        
        // Log DOM elements found
        console.log('AI Editor: DOM elements found:', {
            chatMessages: !!chatMessages,
            userInput: !!userInput,
            sendButton: !!sendButton,
            generateConfigButton: !!generateConfigButton,
            applyChangesButton: !!applyChangesButton,
            undoChangesButton: !!undoChangesButton,
            loadingSpinner: !!loadingSpinner,
            configEditor: !!configEditor
        });
        
        // Add welcome message
        if (chatMessages) {
            addMessage('Welcome to the AI Editor! I can help you update your site configuration. How would you like to customize your site?', 'system');
        }
        
        // Chat history for context management
        let messageHistory = [];
        
        // Send message when button is clicked
        if (sendButton) {
            sendButton.addEventListener('click', sendMessage);
        }
        
        // Add a separate button for generating config directly
        if (generateConfigButton) {
            generateConfigButton.addEventListener('click', function() {
                if (!userInput || userInput.value.trim() === '') {
                    alert('Please enter a request first');
                    return;
                }
                
                // Call the combined AI/config endpoint
                processAiRequest(userInput.value.trim());
            });
        }
        
        // Send message when Enter is pressed (but allow Shift+Enter for new lines)
        if (userInput) {
            userInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
        }
        
        // Apply changes button
        if (applyChangesButton) {
            console.log('Setting up apply changes button listener');
            applyChangesButton.addEventListener('click', function() {
                console.log('Apply changes button clicked');
                
                if (!configEditor) {
                    console.error('Config editor element not found!');
                    showNotification('Error: Config editor not found', 'error');
                    return;
                }
                
                const config = configEditor.value;
                console.log('Config editor value available:', !!config);
                
                if (!config || config.trim() === '') {
                    showNotification('No configuration to apply', 'error');
                    return;
                }
                
                // Show loading spinner
                loadingSpinner.style.display = 'flex';
                
                console.log('Applying changes with config:', config.substring(0, 50) + '...');
                // Call the apply changes endpoint using fetch API with new path
                fetch('/apply_changes/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        config: config
                    })
                })
                .then(response => response.json())
                .then(response => {
                    loadingSpinner.style.display = 'none';
                    
                    if (response.success) {
                        showNotification('Configuration updated successfully', 'success');
                        
                        // Update original config to match the newly applied config
                        originalConfig = config;
                        
                        // Add system message
                        addMessage('Changes applied successfully! The site configuration has been updated.', 'system');
                    } else {
                        showNotification(response.error || 'Error applying changes', 'error');
                    }
                })
                .catch(error => {
                    loadingSpinner.style.display = 'none';
                    showNotification('Error applying changes: ' + error, 'error');
                });
            });
        }
        
        // Undo changes button
        if (undoChangesButton) {
            console.log('Setting up undo changes button listener');
            undoChangesButton.addEventListener('click', function() {
                console.log('Undo changes button clicked');
                console.log('Original config available:', !!originalConfig);
                if (configEditor && originalConfig) {
                    configEditor.value = originalConfig;
                    showNotification('Changes undone', 'info');
                } else {
                    console.error('Cannot undo changes: configEditor available:', !!configEditor, 'originalConfig available:', !!originalConfig);
                }
            });
        }
        
        // Function to get CSRF token from cookies
        function getCsrfToken() {
            const cookieValue = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='))
                ?.split('=')[1];
            return cookieValue || '';
        }
        
        // Function to process AI request (combines chat and config)
        function processAiRequest(message, isUserMessage = true) {
            // Show loading spinner
            if (loadingSpinner) {
                loadingSpinner.style.display = 'flex';
            }
            
            // If this is a user message, add it to the chat
            if (isUserMessage && chatMessages) {
                addMessage(message, 'user');
                
                // Add to message history
                messageHistory.push({
                    role: 'user',
                    content: message
                });
                
                // Clear input field
                if (userInput) {
                    userInput.value = '';
                }
            }
            
            console.log('Processing AI request:', message);
            
            // Call the single combined endpoint
            fetch('/ai_config/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    message: message,
                    history: messageHistory
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API returned status ${response.status}`);
                }
                return response.json();
            })
            .then(response => {
                console.log('Combined response received:', response);
                
                // Hide loading spinner
                if (loadingSpinner) {
                    loadingSpinner.style.display = 'none';
                }
                
                // Check for error
                if (response.error) {
                    const errorMessage = response.detail ? `${response.error}\n${response.detail}` : response.error;
                    console.error("API Error:", response);
                    throw new Error(errorMessage);
                }
                
                // Handle the natural language response
                if (response.reply) {
                    // Add AI response to chat
                    addMessage(response.reply, 'assistant');
                    
                    // Add to message history
                    messageHistory.push({
                        role: 'assistant',
                        content: response.reply
                    });
                    
                    // Scroll to bottom of chat
                    if (chatMessages) {
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }
                }
                
                // Handle the configuration response
                if (response.config && configEditor && !response.no_changes) {
                    // Log the first 100 chars of the config for debugging
                    console.log(`Config content (first 100 chars): "${response.config.substring(0, 100)}..."`);
                    
                    // Add the configuration to the editor
                    configEditor.value = response.config;
                    
                    // Only add system message if not added by natural language response
                    if (!response.reply) {
                        addMessage('Configuration changes have been updated in the editor. Review and click "Apply Changes" to save them.', 'system');
                    }
                } else if (response.no_changes) {
                    // This is a case where the AI understood the request but determined no changes were needed
                    console.log("No changes needed for this request");
                    // No need to add a system message as the AI response should explain this
                } else if (!response.config) {
                    console.log("No config received from API");
                    addMessage('No configuration changes were generated for this request', 'system');
                }
            })
            .catch(error => {
                // Hide loading spinner
                if (loadingSpinner) {
                    loadingSpinner.style.display = 'none';
                }
                
                const errorMsg = 'Error: ' + error.message;
                console.error(errorMsg);
                addMessage(errorMsg, 'system');
                showNotification(errorMsg, 'error');
            });
        }
        
        // Function to send message via the combined endpoint
        function sendMessage() {
            if (!userInput || !chatMessages) return;
            
            const message = userInput.value.trim();
            
            if (!message) {
                return;
            }
            
            // Process the request using the combined endpoint
            processAiRequest(message);
        }
        
        // Function to add message to chat
        function addMessage(content, role) {
            if (!chatMessages) return;
            
            // Create message element
            const messageElement = document.createElement('div');
            messageElement.className = 'message ' + role;
            
            // Process markdown-like formatting for chat display
            let formattedContent = content
                .replace(/```([\s\S]*?)```/g, '<pre>$1</pre>')  // Code blocks
                .replace(/`([^`]+)`/g, '<code>$1</code>')  // Inline code
                .replace(/\n/g, '<br>');  // Line breaks
            
            const paragraph = document.createElement('p');
            paragraph.innerHTML = formattedContent;
            messageElement.appendChild(paragraph);
            
            chatMessages.appendChild(messageElement);
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // Function to show notification
        function showNotification(message, type) {
            console.log('Showing notification:', message, 'Type:', type);
            
            // Remove any existing notifications
            const existingNotifications = document.querySelectorAll('.notification');
            existingNotifications.forEach(function(notification) {
                notification.remove();
            });
            
            // Create notification element
            const notification = document.createElement('div');
            notification.className = 'notification ' + type;
            notification.textContent = message;
            
            // Add to body
            document.body.appendChild(notification);
            
            // Alert for testing
            console.log('Notification created and added to DOM');
            
            // Remove after 3 seconds
            setTimeout(function() {
                console.log('Removing notification');
                notification.style.animation = 'notificationFadeOut 0.3s forwards';
                
                setTimeout(function() {
                    notification.remove();
                }, 300);
            }, 5000);
        }
    }
})();