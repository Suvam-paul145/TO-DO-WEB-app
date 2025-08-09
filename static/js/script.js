document.addEventListener('DOMContentLoaded', function() {
    const todoList = document.getElementById('todo-list');
    const addTodoForm = document.getElementById('add-todo-form');
    const todoTitleInput = document.getElementById('todo-title-input');

    // Function to render a single todo item
    const renderTodo = (todo) => {
        const todoItem = document.createElement('div');
        todoItem.className = `todo-item ${todo.complete ? 'completed' : ''}`;
        todoItem.dataset.id = todo.id;

        todoItem.innerHTML = `
            <span class="todo-title">${todo.title}</span>
            <div class="todo-actions">
                <button class="toggle-btn">
                    <i class="fas ${todo.complete ? 'fa-check-circle' : 'fa-circle'}"></i>
                </button>
                <button class="delete-btn">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        return todoItem;
    };

    // Function to fetch and display all todos
    const fetchTodos = async () => {
        try {
            const response = await fetch('/api/todos');
            if (!response.ok) throw new Error('Failed to fetch todos');
            const todos = await response.json();
            todoList.innerHTML = ''; // Clear existing list
            todos.forEach(todo => {
                todoList.appendChild(renderTodo(todo));
            });
        } catch (error) {
            console.error('Error fetching todos:', error);
        }
    };

    // Event listener for adding a new todo
    addTodoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = todoTitleInput.value.trim();
        if (!title) return;

        try {
            const response = await fetch('/api/add_todo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: title })
            });
            if (!response.ok) throw new Error('Failed to add todo');
            const newTodo = await response.json();
            todoList.appendChild(renderTodo(newTodo));
            todoTitleInput.value = ''; // Clear input
        } catch (error) {
            console.error('Error adding todo:', error);
        }
    });

    // Event listener for toggle and delete actions (using event delegation)
    todoList.addEventListener('click', async (e) => {
        const target = e.target;
        const todoItem = target.closest('.todo-item');
        if (!todoItem) return;

        const id = todoItem.dataset.id;

        // Handle toggle
        if (target.closest('.toggle-btn')) {
            try {
                const response = await fetch(`/api/toggle_todo/${id}`, { method: 'POST' });
                if (!response.ok) throw new Error('Failed to toggle todo');
                const updatedTodo = await response.json();
                
                // Update UI
                const localItem = document.querySelector(`.todo-item[data-id='${id}']`);
                if (localItem) {
                    localItem.className = `todo-item ${updatedTodo.complete ? 'completed' : ''}`;
                    const icon = localItem.querySelector('.toggle-btn i');
                    icon.className = `fas ${updatedTodo.complete ? 'fa-check-circle' : 'fa-circle'}`;
                }
            } catch (error) {
                console.error('Error toggling todo:', error);
            }
        }

        // Handle delete
        if (target.closest('.delete-btn')) {
            try {
                const response = await fetch(`/api/delete_todo/${id}`, { method: 'DELETE' });
                if (!response.ok) throw new Error('Failed to delete todo');
                
                // Update UI
                const localItem = document.querySelector(`.todo-item[data-id='${id}']`);
                if (localItem) {
                    localItem.style.opacity = '0';
                    localItem.style.transform = 'translateX(20px)';
                    setTimeout(() => localItem.remove(), 300);
                }
            } catch (error) {
                console.error('Error deleting todo:', error);
            }
        }
    });

    // Initial fetch of todos when the page loads
    fetchTodos();
});
