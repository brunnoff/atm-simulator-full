document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const loginArea = document.getElementById('login-area');
    const operationArea = document.getElementById('operation-area');

    loginForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loginArea.style.display = 'none';
                operationArea.style.display = 'block';
            } else {
                alert('Credenciais inválidas');
            }
        });
    });
});