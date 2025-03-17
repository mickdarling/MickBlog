/* AI Editor JavaScript */
(function($) {
    $(document).ready(function() {
        // DOM elements
        const chatMessages = $('#chatMessages');
        const userInput = $('#userInput');
        const sendButton = $('#sendButton');
        const applyChangesButton = $('#applyChangesButton');
        const copyChangesButton = $('#copyChangesButton');
        const loadingSpinner = $('#loadingSpinner');
        const currentConfigElement = $('#currentConfig');
        const suggestedConfigElement = $('#suggestedConfig');
        
        // Chat history for context management
        let messageHistory = [];
        
        // Tab switching functionality
        $('.tab-button').click(function() {
            $('.tab-button').removeClass('active');
            $(this).addClass('active');
            
            const tabId = $(this).data('tab');
            $('.tab-content').removeClass('active');
            $('#' + tabId + 'Tab').addClass('active');
        });
        
        // Send message when button is clicked
        sendButton.click(sendMessage);
        
        // Send message when Enter is pressed (but allow Shift+Enter for new lines)
        userInput.keydown(function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Apply changes button
        applyChangesButton.click(function() {
            const suggestedConfig = suggestedConfigElement.text();
            
            if (!suggestedConfig || suggestedConfig === 'No suggested changes yet') {
                showNotification('No changes to apply', 'error');
                return;
            }
            
            // Show loading spinner
            loadingSpinner.show();
            
            // Call the apply changes endpoint
            $.ajax({
                url: '../apply_changes/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    config: suggestedConfig
                }),
                success: function(response) {
                    loadingSpinner.hide();
                    
                    if (response.success) {
                        showNotification('Configuration updated successfully', 'success');
                        
                        // Update current config display
                        currentConfigElement.text(suggestedConfig);
                        
                        // Add system message
                        addMessage('Changes applied successfully! The site configuration has been updated.', 'system');
                    } else {
                        showNotification(response.error || 'Error applying changes', 'error');
                    }
                },
                error: function(xhr) {
                    loadingSpinner.hide();
                    const errorMsg = xhr.responseJSON?.error || 'Error applying changes';
                    showNotification(errorMsg, 'error');
                }
            });
        });
        
        // Copy to clipboard button
        copyChangesButton.click(function() {
            const suggestedConfig = suggestedConfigElement.text();
            
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
        
        // Function to send message to AI
        function sendMessage() {
            const message = userInput.val().trim();
            
            if (!message) {
                return;
            }
            
            // Add user message to chat
            addMessage(message, 'user');
            
            // Clear input
            userInput.val('');
            
            // Show loading spinner
            loadingSpinner.show();
            
            // Add to message history
            messageHistory.push({
                role: 'user',
                content: message
            });
            
            // Send to AI
            $.ajax({
                url: '../ai_message/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    message: message,
                    history: messageHistory
                }),
                success: function(response) {
                    loadingSpinner.hide();
                    
                    // Add AI response to chat
                    addMessage(response.reply, 'assistant');
                    
                    // Add to message history
                    messageHistory.push({
                        role: 'assistant',
                        content: response.reply
                    });
                    
                    // If there's a suggested config, update the editor
                    if (response.has_suggested_config && response.suggested_config) {
                        suggestedConfigElement.text(response.suggested_config);
                        applyChangesButton.prop('disabled', false);
                        copyChangesButton.prop('disabled', false);
                        
                        // Switch to suggested tab
                        $('.tab-button[data-tab="suggested"]').click();
                    }
                    
                    // Scroll to bottom of chat
                    chatMessages.scrollTop(chatMessages[0].scrollHeight);
                },
                error: function(xhr) {
                    loadingSpinner.hide();
                    const errorMsg = xhr.responseJSON?.error || 'Error communicating with AI';
                    addMessage('Error: ' + errorMsg, 'system');
                    showNotification(errorMsg, 'error');
                }
            });
        }
        
        // Function to add message to chat
        function addMessage(content, role) {
            const messageElement = $('<div class="message"></div>').addClass(role);
            
            // Process markdown-like formatting
            // This is a simple version - consider using a markdown library for better rendering
            let formattedContent = content
                .replace(/```([\s\S]*?)```/g, '<pre>$1</pre>')  // Code blocks
                .replace(/`([^`]+)`/g, '<code>$1</code>')  // Inline code
                .replace(/\n/g, '<br>');  // Line breaks
            
            messageElement.html('<p>' + formattedContent + '</p>');
            chatMessages.append(messageElement);
            
            // Scroll to bottom
            chatMessages.scrollTop(chatMessages[0].scrollHeight);
        }
        
        // Function to show notification
        function showNotification(message, type) {
            // Create notification element
            const notification = $('<div class="notification"></div>').addClass(type);
            notification.text(message);
            
            // Add to body
            $('body').append(notification);
            
            // Remove after 3 seconds
            setTimeout(function() {
                notification.css('animation', 'notificationFadeOut 0.3s forwards');
                
                setTimeout(function() {
                    notification.remove();
                }, 300);
            }, 3000);
        }
    });
})(django.jQuery);