// Form validation and loading states
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.recommendation-form');
    const submitBtn = document.querySelector('.submit-btn');
    
    if (form && submitBtn) {
        form.addEventListener('submit', function(e) {
            const selects = form.querySelectorAll('select');
            let allFilled = true;
            
            selects.forEach(select => {
                if (!select.value) {
                    allFilled = false;
                    select.style.borderColor = '#ef4444';
                } else {
                    select.style.borderColor = '#10b981';
                }
            });
            
            if (!allFilled) {
                e.preventDefault();
                alert('Please fill in all fields before submitting.');
            } else {
                submitBtn.textContent = 'Analyzing...';
                submitBtn.disabled = true;
            }
        });
        
        // Real-time validation
        const selects = form.querySelectorAll('select');
        selects.forEach(select => {
            select.addEventListener('change', function() {
                if (this.value) {
                    this.style.borderColor = '#10b981';
                }
            });
        });
    }
});

// Simple notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        background: ${type === 'error' ? '#ef4444' : '#10b981'};
        color: white;
        border-radius: 5px;
        z-index: 1000;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}