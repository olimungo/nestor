import redis from './redis';
import { Server } from 'socket.io';

const CORS_ORIGIN = process.env.CORS_ORIGIN.split(',') || 'http://localhost:3000';

const roomdId = 'nestor';
let devices = [];

(async() => {
    // When starting, load devices identified in "list"
    const listDevicesId: string[] = await redis.smembersAsync('list');

    await Promise.all(
        listDevicesId.map(async (listDeviceId) => {
            await addDevice(listDeviceId);
        })
    );

    // And remove everything in "updated" and "removed"
    const updatedDevicesId: string[] = await redis.smembersAsync('updated');

    await Promise.all(
        updatedDevicesId.map(async (updatedDeviceId) => {
            await redis.sremAsync('updated', updatedDeviceId);
        })
    );

    const removedDevicesId: string[] = await redis.smembersAsync('removed');

    await Promise.all(
        removedDevicesId.map(async (removedDeviceId) => {
            await redis.sremAsync('updated', removedDeviceId);
        })
    );
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
    socket.join(roomdId);

    socket.on(
        'mqtt-command',
        async (message) => {
            await redis.setAsync(`commands/${message.device}`, message.command)
        }
    );

    socket.on('get-devices', () => socket.emit('devices', devices));
});

setInterval(async () => {
    const updatedDevicesId: string[] = await redis.smembersAsync('updated');

    await Promise.all(
        updatedDevicesId.map(async (updatedDeviceId) => {
            const device = await addDevice(updatedDeviceId);
            await redis.sremAsync('updated', updatedDeviceId);
            io.to(roomdId).emit('update-device', device);
        })
    );

    const removedDevicesId: string[] = await redis.smembersAsync('removed');

    await Promise.all(
        removedDevicesId.map(async (removedDeviceId) => {
            devices = devices.filter(device => device.id !== removedDeviceId);
            await redis.sremAsync('removed', removedDeviceId);
            io.to(roomdId).emit('remove-device', removedDeviceId);
        })
    );
}, 1000);

async function addDevice(id: string) {
    const value = await redis.getAsync(id);
    const parsedValue = JSON.parse(value);
    const netId = id.split('/')[1];
    const device = { id, netId, ...parsedValue };

    devices = [ ...devices, device];

    return device;
}