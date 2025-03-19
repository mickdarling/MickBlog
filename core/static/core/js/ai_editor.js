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
                
                // Call the dedicated config endpoint
                generateConfig(userInput.value.trim());
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
        
        // Function to directly generate config
        function generateConfig(message) {
            // Show loading spinner
            if (loadingSpinner) {
                loadingSpinner.style.display = 'flex';
            }
            
            console.log('Generating config for:', message);
            
            // Call the dedicated config endpoint with new path
            fetch('/ai_config/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    message: message
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Config API returned status ${response.status}`);
                }
                return response.json();
            })
            .then(response => {
                console.log('Config response received:', response);
                
                // Hide loading spinner
                if (loadingSpinner) {
                    loadingSpinner.style.display = 'none';
                }
                
                if (response.error) {
                    const errorMessage = response.detail ? `${response.error}\n${response.detail}` : response.error;
                    console.error("Config API Error:", response);
                    throw new Error(errorMessage);
                }
                
                // Update config if available
                if (response.config && configEditor) {
                    console.log('Config response content: ' + response.config.substring(0, 30) + '...');
                    
                    // Set the config content
                    configEditor.value = response.config;
                    
                    // Add system message
                    addMessage('Configuration changes have been updated in the editor. Review and click "Apply Changes" to save them.', 'system');
                } else {
                    console.log('No config received from API');
                }
            })
            .catch(error => {
                console.error('Error generating config:', error);
                
                // Hide loading spinner
                if (loadingSpinner) {
                    loadingSpinner.style.display = 'none';
                }
                
                // Show error
                addMessage('Error generating configuration: ' + error.message, 'system');
            });
        }
        
        // Function to send message to AI
        function sendMessage() {
            if (!userInput || !chatMessages) return;
            
            const message = userInput.value.trim();
            
            if (!message) {
                return;
            }
            
            // Add user message to chat
            addMessage(message, 'user');
            
            // Clear input
            userInput.value = '';
            
            // Show loading spinner
            if (loadingSpinner) {
                loadingSpinner.style.display = 'flex';
            }
            
            // Add to message history
            messageHistory.push({
                role: 'user',
                content: message
            });
            
            // Step 1: First make the conversation request
            console.log("Making CONVERSATION API call");
            fetch('/ai_message/', {
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
                if (response.error) {
                    const errorMessage = response.detail ? `${response.error}\n${response.detail}` : response.error;
                    console.error("API Error:", response);
                    throw new Error(errorMessage);
                }
                
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
                
                // Step 2: Make a separate request to the config endpoint
                console.log("Making CONFIG API call to dedicated endpoint");
                
                return fetch('/ai_config/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        message: message  // Just send the original user message
                    })
                });
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Config API returned status ${response.status}`);
                }
                return response.json();
            })
            .then(configResponse => {
                // Log the config response
                console.log("CONFIG RESPONSE:", configResponse);
                
                // Return the response to continue the chain
                return configResponse;
            })
            .then(response => {
                // Hide loading spinner
                if (loadingSpinner) {
                    loadingSpinner.style.display = 'none';
                }
                
                // Update config if available
                if (response.config && configEditor) {
                    console.log("Received configuration from dedicated API call");
                    
                    // Log the first 100 chars of the config for debugging
                    console.log(`Config content (first 100 chars): "${response.config.substring(0, 100)}..."`);
                    
                    // Add the configuration to the editor
                    configEditor.value = response.config;
                    
                    // Add system message about configuration
                    addMessage('Configuration changes have been updated in the editor. Review and click "Apply Changes" to save them.', 'system');
                } else {
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
        
        // Function to add message to chat
        function addMessage(content, role) {
            if (!chatMessages) return;
            
            // Create message element
            const messageElement = document.createElement('div');
            messageElement.className = 'message ' + role;
            
            // Handle AI assistant messages specifically to extract configs and clean up display
            if (role === 'assistant') {
                console.log("Processing assistant message for markdown blocks");
                // Check for markdown blocks in assistant messages
                if (content.includes('```markdown')) {
                    let cleanedContent = content;
                    let markdownBlock = null;
                    
                    console.log("Found markdown block indicator in message");
                    
                    // Use regex to more reliably extract the markdown block
                    const markdownRegex = /```markdown\s*([\s\S]*?)\s*```/;
                    const match = content.match(markdownRegex);
                    
                    if (match && match[1]) {
                        markdownBlock = match[1].trim();
                        console.log("Extracted markdown block using regex:", markdownBlock.substring(0, 50) + "...");
                        
                        // Clean up the display text by replacing the large code block with a notice
                        cleanedContent = content.replace(markdownRegex, 
                            '<em>[Configuration changes available in the editor]</em>');
                        
                        console.log("Cleaned content for display:", cleanedContent.substring(0, 100) + "...");
                        
                        // Update the config editor if we found a valid block
                        if (markdownBlock && configEditor) {
                            console.log("Updating editor with extracted markdown");
                            configEditor.value = markdownBlock;
                        }
                    } else {
                        console.log("Failed to extract markdown block with regex");
                    }
                    
                    // Use the cleaned content for display
                    content = cleanedContent;
                }
            }
            
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