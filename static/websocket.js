const socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', () => {
    console.log('Conectado ao servidor WebSocket');
});
socket.on('update_balance', (data) => {
    alert('Novo saldo: R$ ' + data.balance);
});
socket.on('response', (data) => {
    console.log(data.data);
});