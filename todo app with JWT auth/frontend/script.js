// API URL - Change this to your API endpoint
const API_URL = 'http://localhost:8000';

// DOM Elements
// Auth elements
const authForms = document.getElementById('auth-forms');
const loginToggle = document.getElementById('login-toggle');
const registerToggle = document.getElementById('register-toggle');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const userName = document.getElementById('user-name');
const logoutBtn = document.getElementById('logout-btn');

// Task management elements
const taskManagement = document.getElementById('task-management');
const newTaskBtn = document.getElementById('new-task-btn');
const tasksContainer = document.getElementById('tasks-container');
const statusFilter = document.getElementById('status-filter');
const priorityFilter = document.getElementById('priority-filter');

// Task form modal elements
const taskFormModal = document.getElementById('task-form-modal');
const taskForm = document.getElementById('task-form');
const taskFormTitle = document.getElementById('task-form-title');
const taskIdInput = document.getElementById('task-id');
const taskTitleInput = document.getElementById('task-title');
const taskDescriptionInput = document.getElementById('task-description');
const taskDueDateInput = document.getElementById('task-due-date');
const taskPriorityInput = document.getElementById('task-priority');
const taskCompletedInput = document.getElementById('task-completed');
const completedGroup = document.getElementById('completed-group');
const cancelTaskBtn = document.getElementById('cancel-task');
const closeModalBtn = document.querySelector('.close');

// State
let token = localStorage.getItem('token');
let currentUser = null;
let tasks = [];

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Check auth status
    checkAuthStatus();
    
    // Auth form toggle
    loginToggle.addEventListener('click', () => {
        loginToggle.classList.add('active');
        registerToggle.classList.remove('active');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    });
    
    registerToggle.addEventListener('click', () => {
        registerToggle.classList.add('active');
        loginToggle.classList.remove('active');
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    });
    
    // Auth forms submission
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    logoutBtn.addEventListener('click', handleLogout);
    
    // Task management
    newTaskBtn.addEventListener('click', openNewTaskForm);
    statusFilter.addEventListener('change', filterTasks);
    priorityFilter.addEventListener('change', filterTasks);
    
    // Task form modal
    taskForm.addEventListener('submit', handleTaskFormSubmit);
    cancelTaskBtn.addEventListener('click', closeTaskForm);
    closeModalBtn.addEventListener('click', closeTaskForm);
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === taskFormModal) {
            closeTaskForm();
        }
    });
});

// Authentication Functions
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }
        
        // Save token and authenticate user
        localStorage.setItem('token', data.access_token);
        token = data.access_token;
        
        // Get user info
        await getUserInfo();
        
        // Show toast notification
        showToast('Login successful', 'success');
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch(`${API_URL}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                email,
                password
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Registration failed');
        }
        
        // Show success message and switch to login
        showToast('Registration successful. Please login.', 'success');
        loginToggle.click();
        
        // Auto-fill login form
        document.getElementById('login-email').value = email;
        document.getElementById('login-password').value = password;
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function getUserInfo() {
    try {
        const response = await fetch(`${API_URL}/users/me/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to get user info');
        }
        
        currentUser = await response.json();
        
        // Update UI
        userName.textContent = currentUser.name;
        showTaskManagement();
        
        // Load tasks
        await loadTasks();
        
    } catch (error) {
        handleLogout();
        showToast(error.message, 'error');
    }
}

function handleLogout() {
    localStorage.removeItem('token');
    token = null;
    currentUser = null;
    tasks = [];
    
    // Update UI
    showAuthForms();
    
    // Clear form values
    loginForm.reset();
    registerForm.reset();
}

function checkAuthStatus() {
    if (token) {
        getUserInfo();
    } else {
        showAuthForms();
    }
}

// Task Management Functions
async function loadTasks() {
    try {
        const statusValue = statusFilter.value;
        const priorityValue = priorityFilter.value;
        
        let url = `${API_URL}/tasks/?skip=0&limit=100`;
        
        if (statusValue === 'active') {
            url += '&completed=false';
        } else if (statusValue === 'completed') {
            url += '&completed=true';
        }
        
        if (priorityValue !== 'all') {
            url += `&priority=${priorityValue}`;
        }
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load tasks');
        }
        
        tasks = await response.json();
        renderTasks();
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function renderTasks() {
    tasksContainer.innerHTML = '';
    
    if (tasks.length === 0) {
        tasksContainer.innerHTML = '<div class="no-tasks">No tasks found. Create a new task to get started!</div>';
        return;
    }
    
    tasks.forEach(task => {
        const taskCard = document.createElement('div');
        taskCard.className = `task-card priority-${task.priority}`;
        
        if (task.completed) {
            taskCard.classList.add('completed');
        }
        
        // Format due date
        let dueDateFormatted = 'No due date';
        if (task.due_date) {
            const dueDate = new Date(task.due_date);
            dueDateFormatted = dueDate.toLocaleString();
        }
        
        taskCard.innerHTML = `
            <div class="task-header">
                <h3 class="task-title">${task.title}</h3>
                <div class="task-actions">
                    <button class="edit-btn" data-id="${task.id}" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="delete-btn" data-id="${task.id}" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="task-info">
                <p class="task-description">${task.description || 'No description'}</p>
                <div class="task-meta">
                    <div class="task-due-date">
                        <i class="far fa-calendar-alt"></i>
                        <span>${dueDateFormatted}</span>
                    </div>
                    <div class="task-priority">
                        <i class="fas fa-flag"></i>
                        <span class="priority-badge priority-${task.priority}">${task.priority}</span>
                    </div>
                </div>
            </div>
            <label class="task-complete-toggle">
                <input type="checkbox" data-id="${task.id}" ${task.completed ? 'checked' : ''}>
                <span>Mark as ${task.completed ? 'incomplete' : 'complete'}</span>
            </label>
        `;
        
        // Add event listeners
        taskCard.querySelector('.edit-btn').addEventListener('click', () => openEditTaskForm(task));
        taskCard.querySelector('.delete-btn').addEventListener('click', () => deleteTask(task.id));
        
        const completeToggle = taskCard.querySelector('input[type="checkbox"]');
        completeToggle.addEventListener('change', () => toggleTaskCompletion(task.id, completeToggle.checked));
        
        tasksContainer.appendChild(taskCard);
    });
}

function filterTasks() {
    loadTasks();
}

async function handleTaskFormSubmit(e) {
    e.preventDefault();
    
    const taskId = taskIdInput.value;
    const isEdit = taskId !== '';
    
    const taskData = {
        title: taskTitleInput.value,
        description: taskDescriptionInput.value || null,
        priority: taskPriorityInput.value
    };
    
    if (taskDueDateInput.value) {
        taskData.due_date = new Date(taskDueDateInput.value).toISOString();
    }
    
    if (isEdit) {
        taskData.completed = taskCompletedInput.checked;
    }
    
    try {
        let url = `${API_URL}/tasks/`;
        let method = 'POST';
        
        if (isEdit) {
            url += taskId;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(taskData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to save task');
        }
        
        // Close form and reload tasks
        closeTaskForm();
        await loadTasks();
        
        // Show success message
        showToast(`Task ${isEdit ? 'updated' : 'created'} successfully`, 'success');
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function openNewTaskForm() {
    taskFormTitle.textContent = 'New Task';
    taskIdInput.value = '';
    taskForm.reset();
    
    // Hide completed checkbox for new tasks
    completedGroup.classList.add('hidden');
    
    // Set default due date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setMinutes(tomorrow.getMinutes() - tomorrow.getTimezoneOffset());
    taskDueDateInput.value = tomorrow.toISOString().slice(0, 16);
    
    taskFormModal.classList.remove('hidden');
}

function openEditTaskForm(task) {
    taskFormTitle.textContent = 'Edit Task';
    taskIdInput.value = task.id;
    taskTitleInput.value = task.title;
    taskDescriptionInput.value = task.description || '';
    taskPriorityInput.value = task.priority;
    taskCompletedInput.checked = task.completed;
    
    // Show completed checkbox for edit
    completedGroup.classList.remove('hidden');
    
    // Set due date if exists
    if (task.due_date) {
        const dueDate = new Date(task.due_date);
        dueDate.setMinutes(dueDate.getMinutes() - dueDate.getTimezoneOffset());
        taskDueDateInput.value = dueDate.toISOString().slice(0, 16);
    } else {
        taskDueDateInput.value = '';
    }
    
    taskFormModal.classList.remove('hidden');
}

function closeTaskForm() {
    taskFormModal.classList.add('hidden');
    taskForm.reset();
}

async function toggleTaskCompletion(taskId, completed) {
    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                completed: completed
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update task');
        }
        
        // Reload tasks
        await loadTasks();
        
        // Show success message
        showToast(`Task marked as ${completed ? 'completed' : 'active'}`, 'success');
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete task');
        }
        
        // Reload tasks
        await loadTasks();
        
        // Show success message
        showToast('Task deleted successfully', 'success');
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// UI Helper Functions
function showAuthForms() {
    authForms.classList.remove('hidden');
    taskManagement.classList.add('hidden');
}

function showTaskManagement() {
    authForms.classList.add('hidden');
    taskManagement.classList.remove('hidden');
}

function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <button class="toast-close">&times;</button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Add event listener to close button
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}