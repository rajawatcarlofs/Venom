// Utility functions for all pages
function formatDate(isoDate) {
    return new Date(isoDate).toLocaleString();
}

function showSpinner() {
    return '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>';
}

function getStatusBadge(status) {
    const colors = {
        'online': 'success',
        'offline': 'danger',
        'running': 'warning',
        'paused': 'secondary',
        'completed': 'info',
        'stopped': 'danger',
        'draft': 'light',
        'error': 'danger'
    };
    return `<span class="badge bg-${colors[status] || 'secondary'}">${status.toUpperCase()}</span>`;
}

function showNotification(message, type = 'success') {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const icon = type === 'success' ? 'check-circle' : 'exclamation-triangle';
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass} alert-dismissible fade show`;
    alert.innerHTML = `<i class="fas fa-${icon}"></i> ${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertAdjacentElement('afterbegin', alert);
    }
    
    setTimeout(() => alert.remove(), 5000);
}

console.log('Utilities loaded');
