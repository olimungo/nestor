import { Server } from 'socket.io';
import { cleanDatabase, getDevices, setKey, getUpdated } from './database';
import { toIotDevices } from './models';

const CORS_ORIGIN = process.env.CORS_ORIGIN.split(',') || 'http://localhost:3000';
const CHECK_DEVICE_UPDATES = 100; // milliseconds
const ROOM_ID = 'nestor';

(async () => {
    await cleanDatabase();
})();

const io = new Server(parseInt(process.env.PORT) || 9000, {
    cors: {
        origin: CORS_ORIGIN,
        methods: ['GET', 'POST'],
    },
});

console.log(`> Websockets server started on port ${process.env.PORT}`);
console.log(`> With CORS opened to ${CORS_ORIGIN}`);

io.on('connection', async (socket) => {
    socket.join(ROOM_ID);

    socket.on('mqtt-command', async (message) => {
        await setKey(`commands/${message.device}`, message.command);
    });

    socket.on('get-devices', () => {
        getDevices().then((devices) => {
            socket.emit('devices', toIotDevices(devices));
        });
    });
});

setInterval(async () => {
    const updated = await getUpdated();

    if (updated) {
        getDevices().then((devices) => {
            io.to(ROOM_ID).emit('devices', toIotDevices(devices));
        });
    }
}, CHECK_DEVICE_UPDATES);
