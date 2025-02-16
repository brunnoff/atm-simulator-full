document.addEventListener('DOMContentLoaded', function() {
    const socket = io();

    socket.on('connect', function() {
        console.log('Conectado ao servidor WebSocket');
    });

    socket.on('notification', function(message) {
        const notificationsDiv = document.getElementById('notifications');
        const newNotification = document.createElement('p');
        newNotification.textContent = message;
        notificationsDiv.appendChild(newNotification);
    });

    socket.on('disconnect', function() {
        console.log('Desconectado do servidor WebSocket');
    });
});