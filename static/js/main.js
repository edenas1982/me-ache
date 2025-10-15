// Me Ache - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Like/Dislike functionality
    const likeButtons = document.querySelectorAll('.btn-like, .btn-dislike, .btn-super-like');
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            const action = this.dataset.action;
            
            if (postId && action) {
                handlePostAction(postId, action, this);
            }
        });
    });

    // Chat functionality
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });
    }

    // Auto-scroll chat to bottom
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Image preview functionality
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            previewImage(this);
        });
    });

    // Location services
    if (navigator.geolocation) {
        const locationButtons = document.querySelectorAll('.btn-location');
        locationButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                getCurrentLocation();
            });
        });
    }
});

// Handle post actions (like, dislike, super like)
function handlePostAction(postId, action, button) {
    const url = `/feed/${postId}/${action}/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update button appearance
            updateActionButton(button, action, data.liked);
            
            // Update like count if element exists
            const likeCount = document.querySelector(`[data-post-id="${postId}"] .like-count`);
            if (likeCount) {
                likeCount.textContent = data.total_likes;
            }
        } else {
            showAlert('Erro ao processar ação', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Erro de conexão', 'danger');
    });
}

// Update action button appearance
function updateActionButton(button, action, isActive) {
    const icon = button.querySelector('i');
    
    if (isActive) {
        button.classList.add('active');
        if (action === 'like') {
            icon.className = 'bi bi-heart-fill';
        } else if (action === 'dislike') {
            icon.className = 'bi bi-x-circle-fill';
        } else if (action === 'super-like') {
            icon.className = 'bi bi-star-fill';
        }
    } else {
        button.classList.remove('active');
        if (action === 'like') {
            icon.className = 'bi bi-heart';
        } else if (action === 'dislike') {
            icon.className = 'bi bi-x-circle';
        } else if (action === 'super-like') {
            icon.className = 'bi bi-star';
        }
    }
}

// Send chat message
function sendMessage() {
    const form = document.getElementById('chat-form');
    const messageInput = form.querySelector('input[name="message"]');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    const chatMessages = document.querySelector('.chat-messages');
    const conversationId = form.dataset.conversationId;
    
    // Add message to UI immediately
    addMessageToUI(message, true);
    messageInput.value = '';
    
    // Send to server
    fetch(`/chat/${conversationId}/send/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            showAlert('Erro ao enviar mensagem', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Erro de conexão', 'danger');
    });
}

// Add message to chat UI
function addMessageToUI(message, isSent = false) {
    const chatMessages = document.querySelector('.chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isSent ? 'sent' : 'received'}`;
    
    const now = new Date();
    const timeString = now.toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <img src="/static/images/default-avatar.png" alt="Avatar" class="message-avatar">
        <div class="message-content">
            <div>${message}</div>
            <div class="message-time">${timeString}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Preview uploaded image
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('image-preview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Get current location
function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                // Update location fields
                const latInput = document.getElementById('id_latitude');
                const lngInput = document.getElementById('id_longitude');
                
                if (latInput) latInput.value = lat;
                if (lngInput) lngInput.value = lng;
                
                showAlert('Localização atualizada com sucesso!', 'success');
            },
            function(error) {
                showAlert('Erro ao obter localização: ' + error.message, 'danger');
            }
        );
    } else {
        showAlert('Geolocalização não suportada pelo navegador', 'warning');
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Format date to relative time
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'agora mesmo';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} min atrás`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours}h atrás`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days}d atrás`;
    }
}

// Initialize relative time formatting
document.addEventListener('DOMContentLoaded', function() {
    const timeElements = document.querySelectorAll('[data-time]');
    timeElements.forEach(element => {
        const timeString = element.dataset.time;
        element.textContent = formatRelativeTime(timeString);
    });
});
