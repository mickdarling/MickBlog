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
        const copyChangesButton = document.getElementById('copyChangesButton');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const currentConfigElement = document.getElementById('currentConfig');
        const suggestedConfigElement = document.getElementById('suggestedConfig');
        
        // Log DOM elements found
        console.log('AI Editor: DOM elements found:', {
            chatMessages: !!chatMessages,
            userInput: !!userInput,
            sendButton: !!sendButton,
            generateConfigButton: !!generateConfigButton,
            applyChangesButton: !!applyChangesButton,
            copyChangesButton: !!copyChangesButton,
            loadingSpinner: !!loadingSpinner,
            currentConfigElement: !!currentConfigElement,
            suggestedConfigElement: !!suggestedConfigElement
        });
        
        // Add welcome message
        if (chatMessages) {
            addMessage('Welcome to the AI Editor! I can help you update your site configuration. How would you like to customize your site?', 'system');
        }
        
        // Chat history for context management
        let messageHistory = [];
        
        // Tab switching functionality using vanilla JS
        const tabButtons = document.querySelectorAll('.tab-button');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                tabButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                this.classList.add('active');
                
                // Get the tab id from the data-tab attribute
                const tabId = this.getAttribute('data-tab');
                
                // Hide all tab content
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show the selected tab content
                document.getElementById(tabId + 'Tab').classList.add('active');
            });
        });
        
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
            applyChangesButton.addEventListener('click', function() {
                const suggestedConfig = suggestedConfigElement.textContent;
                
                if (!suggestedConfig || suggestedConfig === 'No suggested changes yet') {
                    showNotification('No changes to apply', 'error');
                    return;
                }
                
                // Show loading spinner
                loadingSpinner.style.display = 'flex';
                
                console.log('Applying changes with config:', suggestedConfig.substring(0, 50) + '...');
                // Call the apply changes endpoint using fetch API with new path
                fetch('/apply_changes/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        config: suggestedConfig
                    })
                })
                .then(response => response.json())
                .then(response => {
                    loadingSpinner.style.display = 'none';
                    
                    if (response.success) {
                        showNotification('Configuration updated successfully', 'success');
                        
                        // Update current config display
                        currentConfigElement.textContent = suggestedConfig;
                        
                        // Reset the suggested config to prepare for next changes
                        suggestedConfigElement.textContent = "No suggested changes yet";
                        
                        // Disable buttons until new changes are suggested
                        if (applyChangesButton) {
                            applyChangesButton.disabled = true;
                        }
                        
                        if (copyChangesButton) {
                            copyChangesButton.disabled = true;
                        }
                        
                        // Switch back to current tab to show the applied changes
                        const currentTab = document.querySelector('.tab-button[data-tab="current"]');
                        if (currentTab) {
                            currentTab.click();
                        }
                        
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
        
        // Copy to clipboard button
        if (copyChangesButton) {
            copyChangesButton.addEventListener('click', function() {
                const suggestedConfig = suggestedConfigElement.textContent;
                
                if (!suggestedConfig || suggestedConfig === 'No suggested changes yet') {
                    showNotification('No changes to copy', 'error');
                    return;
                }
                
                // Create temporary textarea element to copy from
                const textarea = document.createElement('textarea');
                textarea.value = suggestedConfig;
                document.body.appendChild(textarea);
                textarea.select();
                
                try {
                    document.execCommand('copy');
                    showNotification('Copied to clipboard!', 'success');
                } catch (err) {
                    showNotification('Failed to copy: ' + err, 'error');
                }
                
                document.body.removeChild(textarea);
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
                
                // Update suggested config if available
                if (response.config && suggestedConfigElement) {
                    console.log('Config response content: ' + response.config.substring(0, 30) + '...');
                    
                    // Set the config content
                    suggestedConfigElement.textContent = response.config;
                    
                    // Enable buttons
                    if (applyChangesButton) {
                        applyChangesButton.disabled = false;
                    }
                    
                    if (copyChangesButton) {
                        copyChangesButton.disabled = false;
                    }
                    
                    // Switch to suggested tab
                    const suggestedTab = document.querySelector('.tab-button[data-tab="suggested"]');
                    if (suggestedTab) {
                        suggestedTab.click();
                    }
                    
                    // Add system message
                    addMessage('Configuration changes are available in the "Suggested Changes" tab', 'system');
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
                    
                    // Update suggested config if available
                    if (response.config && suggestedConfigElement) {
                        console.log("Received configuration from dedicated API call");
                        
                        // Log the first 100 chars of the config for debugging
                        console.log(`Config content (first 100 chars): "${response.config.substring(0, 100)}..."`);
                        
                        // Add the configuration to the suggested config element
                        suggestedConfigElement.textContent = response.config;
                        
                        // Enable buttons if we got a real config
                        if (response.config.includes("Site Configuration")) {
                            console.log("Config appears valid, enabling buttons");
                            
                            if (applyChangesButton) {
                                applyChangesButton.disabled = false;
                            }
                            
                            if (copyChangesButton) {
                                copyChangesButton.disabled = false;
                            }
                            
                            // Switch to suggested tab - find and click it
                            const suggestedTab = document.querySelector('.tab-button[data-tab="suggested"]');
                            if (suggestedTab) {
                                suggestedTab.click();
                            }
                            
                            // Add system message about configuration
                            addMessage('Configuration changes are available in the "Suggested Changes" tab', 'system');
                        } else {
                            console.log("Config appears invalid, not enabling buttons");
                            addMessage('Error: Unable to generate proper configuration changes', 'system');
                        }
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
                            '<em>[Configuration changes available in the "Suggested Changes" tab]</em>');
                        
                        console.log("Cleaned content for display:", cleanedContent.substring(0, 100) + "...");
                        
                        // Update the suggested config if we found a valid block
                        if (markdownBlock && suggestedConfigElement) {
                            console.log("Updating suggested config with extracted markdown");
                            suggestedConfigElement.textContent = markdownBlock;
                            
                            // Enable buttons
                            if (applyChangesButton) {
                                applyChangesButton.disabled = false;
                            }
                            
                            if (copyChangesButton) {
                                copyChangesButton.disabled = false;
                            }
                            
                            // Switch to suggested tab automatically
                            const suggestedTab = document.querySelector('.tab-button[data-tab="suggested"]');
                            if (suggestedTab) {
                                suggestedTab.click();
                            }
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
            // Create notification element
            const notification = document.createElement('div');
            notification.className = 'notification ' + type;
            notification.textContent = message;
            
            // Add to body
            document.body.appendChild(notification);
            
            // Remove after 3 seconds
            setTimeout(function() {
                notification.style.animation = 'notificationFadeOut 0.3s forwards';
                
                setTimeout(function() {
                    notification.remove();
                }, 300);
            }, 3000);
        }
    }
})();