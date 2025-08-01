document.addEventListener('DOMContentLoaded', function() {
    // Add smooth fade-out animation before delete
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const todoItem = this.closest('.todo-item');
            todoItem.style.opacity = '0';
            todoItem.style.transform = 'translateX(20px)';
            todoItem.style.transition = 'all 0.3s ease';
            
            setTimeout(() => {
                window.location.href = this.href;
            }, 300);
        });
    });

    // Add smooth transition for completion toggle
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const todoItem = this.closest('.todo-item');
            todoItem.classList.toggle('completed');
            
            setTimeout(() => {
                window.location.href = this.href;
            }, 300);
        });
    });
});