
const redis = require('./redis');
const socketIo = require('socket.io');

io = socketIo(3001);

io.on('connection', (socket) => {
    socket.on('hello', () => console.log('hello'));
});

// io.on('connection', (socket) => {
//     socket.on('mqtt-command', (message) => {
//         command = JSON.parse(message);

//         command.netIds.forEach((netId) => {
//             callbackCommandReceived(
//                 `${command.topic}/${netId}`,
//                 command.message
//             );
//         });
//     });

//     socket.on('get-states', (_) => {
//         callbackGetStatesReveived();
//     });
// });

// function sendMessage(states) {
//     io.emit('update', {
//         shades: states,
//     });
// };