import redis from './redis';
import { Server } from 'socket.io';

const CORS_ORIGIN =
    process.env.CORS_ORIGIN.split(',') || 'http://localhost:3000';

const states = {};

const cleanDatabase = async () => {
    const updated = await redis.smembersAsync('updated');

    await Promise.all(updated.map(async(device)=>{
        await redis.sremAsync('updated', device);
    }));

    const removed = await redis.smembersAsync('removed');

    await Promise.all(removed.map(async(device)=>{
        await redis.sremAsync('removed', device);
    }));

    const keys = await redis.keysAsync('*');

    await Promise.all(keys.map(async(device)=>{
        await redis.delAsync(device);
    }));
}

const io = new Server(parseInt(process.env.PORT) || 9000, {
    cors: {
        origin: CORS_ORIGIN,
        methods: ['GET', 'POST'],
    },
});

console.log(`> Websockets server started on port ${process.env.PORT}`);
console.log(`> With CORS opened to ${CORS_ORIGIN}`);

io.on('connection', async (socket) => {
    await cleanDatabase();

    socket.on(
        'mqtt-command',
        async (message) => {
            console.log(message);
            await redis.setAsync(`commands/${message.device}`, message.command)
        }
    );

    socket.on('get-states', () => {
        const statesRemapped = Object.entries(states).map((state) => {
            console.log(state);
            const value = Object.assign({}, state[1]);
            const key = state[0].split('/');
            key.shift();
            // const key = state[0];

            return { id: key.join(''), name: key.join('/'), ...value };
            // return { id: key, name: key, ...value };
        });

        socket.emit('states', statesRemapped);
    });
});

setInterval(async () => {
    const updated: string[] = await redis.smembersAsync('updated');

    await Promise.all(
        updated.map(async (device) => {
            const state = await redis.getAsync(device);
            states[device] = JSON.parse(state);
            await redis.sremAsync('updated', device);
            io.emit('update-device', { device, state: JSON.parse(state) });
        })
    );

    const removed: string[] = await redis.smembersAsync('removed');

    await Promise.all(
        removed.map(async (device) => {
            delete states[device];
            await redis.sremAsync('removed', device);
            io.emit('remove-device', { device });
        })
    );
}, 100);

// setInterval(() => {
//     console.log(states)
// }, 3000);