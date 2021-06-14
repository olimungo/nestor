import redis from './redis';
import { Server } from 'socket.io';

const CORS_ORIGIN =
    process.env.CORS_ORIGIN.split(',') || 'http://localhost:3000';

const states = {};

const io = new Server(parseInt(process.env.PORT) || 9000, {
    cors: {
        origin: CORS_ORIGIN,
        methods: ['GET', 'POST'],
    },
});

console.log(`> Websockets server started on port ${process.env.PORT}`);
console.log(`> With CORS opened to ${CORS_ORIGIN}`);

io.on('connection', (socket) => {
    socket.on(
        'mqtt-command',
        async (message) =>
            await redis.setAsync(`commands/${message.device}`, message.command)
    );

    socket.on('get-states', () => {
        const statesRemapped = Object.entries(states).map((state) => {
            const value = Object.assign({}, state[1]);
            const key = state[0].split('/');
            key.shift();

            return { id: key.join(''), name: key.join('/'), ...value };
        });

        socket.emit('states', statesRemapped);
    });
});

setInterval(async () => {
    const updated: string[] = await redis.smembersAsync('states/updated');

    await Promise.all(
        updated.map(async (device) => {
            const state = await redis.getAsync(device);
            states[device] = JSON.parse(state);
            await redis.sremAsync('states/updated', device);
            io.emit('update-device', { device, state });
        })
    );

    const removed: string[] = await redis.smembersAsync('states/removed');

    await Promise.all(
        removed.map(async (device) => {
            delete states[device];
            await redis.sremAsync('states/removed', device);
            io.emit('remove-device', { device });
        })
    );
}, 100);
