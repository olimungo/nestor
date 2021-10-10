import redis from './redis';

const DEBUG_MOCK_DATA = false;
const DEBUG_KEEP_DEVICE = false;
const LIMIT_TO_BE_REMOVED = 4000; // milliseconds
const CHECK_LAST_STATUS_FREQUENCY = 200; // milliseconds
const CHECK_COMMANDS_FREQUENCY = 200; // milliseconds
const MOSQUITTO_URL = process.env.MOSQUITTO_URL || 'mqtt://nestor.local';
const mqtt = require('mqtt').connect(MOSQUITTO_URL);

mqtt.on('connect', async () => {
    console.log(`> MQTT server connected to ${MOSQUITTO_URL}`);

    await cleanDatabase();

    if (DEBUG_MOCK_DATA) {
        mockData();
    }

    mqtt.subscribe('#');
});

mqtt.on('message', async (topic, message) => {
    const split = topic.split('/');

    if (split.length) {
        if (split[0] === 'states') {
            // Remove "states/" from the topic and persist state
            persistState(topic.replace('states/', ''), message.toString());
        } else if (split[0] === 'logs') {
            console.log('TBD: log to file');
        }
    }
});

setInterval(async () => {
    const commandsId: string[] = await redis.keysAsync('commands/*');

    await Promise.all(
        commandsId.map(async (commandId: string) => {
            const command = await redis.getAsync(commandId);
            mqtt.publish(commandId, command);

            await redis.delAsync(commandId);
        })
    );
}, CHECK_COMMANDS_FREQUENCY);

if (!DEBUG_KEEP_DEVICE) {
    setInterval(async () => {
        const now = new Date().getTime();
        const timestamps: string[] = await redis.keysAsync('timestamp/*');

        timestamps.map(async (timestamp: string) => {
            const value = parseInt(await redis.getAsync(timestamp));

            if (value + LIMIT_TO_BE_REMOVED < now) {
                await redis.delAsync(timestamp);

                const device = timestamp.replace('timestamp/', '');
                await redis.delAsync(device);
                await redis.sremAsync('list', device);
                await redis.saddAsync('removed', device);
            }
        });
    }, CHECK_LAST_STATUS_FREQUENCY);
}

const cleanDatabase = async () => {
    const updated = await redis.smembersAsync('updated');

    await Promise.all(
        updated.map(async (device) => {
            await redis.sremAsync('updated', device);
        })
    );

    const removed = await redis.smembersAsync('removed');

    await Promise.all(
        removed.map(async (device) => {
            await redis.sremAsync('removed', device);
        })
    );

    const list = await redis.smembersAsync('list');

    await Promise.all(
        list.map(async (device) => {
            await redis.sremAsync('list', device);
        })
    );

    const keys = await redis.keysAsync('*');

    await Promise.all(
        keys.map(async (device) => {
            await redis.delAsync(device);
        })
    );
};

async function persistState(key, value) {
    const persistedValue = await redis.getAsync(key);

    // Check if key exists and if value has changed
    if (!persistedValue || persistedValue !== value) {
        await redis.saddAsync('updated', key);
        await redis.saddAsync('list', key);
        await redis.setAsync(key, value);
    }

    await redis.setAsync(`timestamp/${key}`, new Date().getTime());
}

function mockData() {
    persistState(
        'shades/1',
        '{"ip": "192.168.0.177", "type": "SHADE", "state": "TOP", "tags": ["garden","city2"] }'
    );

    persistState(
        'shades/2',
        '{"ip": "192.168.0.122", "type": "SHADE", "state": "BOTTOM", "tags": ["entrance","city2", "door"] }'
    );

    // persistState(
    //     'switches/11',
    //     '{"ip": "192.168.0.199", "type": "SWITCH", "state": "OFF", "tags": ["living-room","disco", "light"] }'
    // );

    // persistState(
    //     'clocks/10',
    //     '{"ip": "192.168.0.201", "type": "CLOCK", "state": "ON", "tags": ["garden","city3"] }'
    // );
}
