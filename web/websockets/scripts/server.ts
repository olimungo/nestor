import redis from './redis';
import { Server } from 'socket.io';

const CORS_ORIGIN = process.env.CORS_ORIGIN.split(',') || 'http://localhost:3000';
const CHECK_DEVICE_UPDATES = 100; // milliseconds
const ROOM_ID = 'nestor';
let devices = [];

(async () => {
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
    socket.join(ROOM_ID);

    socket.on('mqtt-command', async (message) => {
        await redis.setAsync(`commands/${message.device}`, message.command);
    });

    socket.on('get-devices', () => socket.emit('devices', devices));
});

setInterval(async () => {
    const updatedDevicesId: string[] = await redis.smembersAsync('updated');

    await Promise.all(
        updatedDevicesId.map(async (updatedDeviceId) => {
            const device = await addDevice(updatedDeviceId);
            await redis.sremAsync('updated', updatedDeviceId);
            io.to(ROOM_ID).emit('update-device', device);
        })
    );

    const removedDevicesId: string[] = await redis.smembersAsync('removed');

    await Promise.all(
        removedDevicesId.map(async (removedDeviceId) => {
            devices = devices.filter((device) => device.id !== removedDeviceId);
            await redis.sremAsync('removed', removedDeviceId);
            io.to(ROOM_ID).emit('remove-device', removedDeviceId);
        })
    );
}, CHECK_DEVICE_UPDATES);

async function addDevice(id: string) {
    const value = await redis.getAsync(id);
    const parsedValue = JSON.parse(value);
    const netId = id.split('/')[1];
    const urlId = id.replace('/', '-');
    const device = { id, urlId, netId, ...parsedValue };

    // Remove device if it's already in the list
    devices = devices.filter((device) => device.id !== id);

    // Add new or updated device
    devices = [...devices, device];

    return device;
}
