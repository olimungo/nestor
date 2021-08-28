import redis from './redis';

const MOSQUITTO_URL = process.env.MOSQUITTO_URL || 'mqtt://nestor.local';
const mqtt = require('mqtt').connect(MOSQUITTO_URL);

mqtt.on('connect', () => {
    console.log(`> MQTT server connected to ${MOSQUITTO_URL}`);
    mqtt.subscribe('#');
});

mqtt.on('message', async (topic, message) => {
    const split = topic.split('/');

    if (split.length) {
        if (split[0] === 'states') {
            // Remove "states/" from the topic and persist state
            persistState(topic.replace('states/', ''), message);
        } else if (split[0] === 'logs') {
            console.log('TBD: log to file');
        }
    }
});

async function persistState(key, value) {
    const persistedValue = await redis.getAsync(key);

    // Check if key exists and if value has changed
    if (!persistedValue || persistedValue !== value.toString()) {
        await redis.saddAsync('updated', key);
        await redis.setAsync(key, value.toString());
    }

    await redis.setAsync(`timestamp/${key}`, new Date().getTime());
}

setInterval(async () => {
    const commands: string[] = await redis.keysAsync('commands/*');

    commands.map(async (device: string) => {
        const command = await redis.getAsync(device);
        mqtt.publish(device, command);

        await redis.delAsync(device);
    });
}, 100);

// setInterval(async () => {
//     const now = new Date().getTime();
//     const timestamps: string[] = await redis.keysAsync('timestamp/*');

//     timestamps.map(async (timestamp: string) => {
//         const value = parseInt(await redis.getAsync(timestamp));

//         if (value + 1000 * 10 < now) {
//             await redis.delAsync(timestamp);

//             const device = timestamp.replace('timestamp/', '');
//             await redis.delAsync(device);
//             await redis.saddAsync('removed', device);
//         }
//     });
// }, 1000);

persistState(
    'states/shades/1',
    '{"ip": "192.168.0.177", "type": "MOTOR-H", "state": "TOP", "tags": ["garden","city2"] }'
);

persistState(
    'states/shades/2',
    '{"ip": "192.168.0.122", "type": "MOTOR-V", "state": "BOTTOM", "tags": ["entrance","city2", "door"] }'
);

// persistState(
//     'states/switch/1',
//     '{"ip": "192.168.0.199", "type": "SWITCH", "state": "OFF", "tags": ["living-room","disco", "light"] }'
// );

// persistState(
//     'states/shades/10',
//     '{"ip": "192.168.0.201", "type": "MOTOR-H", "state": "TOP", "tags": ["garden","city3"] }'
// );

// persistState(
//     'states/shades/11',
//     '{"ip": "192.168.0.202", "type": "MOTOR-V", "state": "BOTTOM", "tags": ["entrance","city3", "disco"] }'
// );

// persistState(
//     'states/shades/12',
//     '{"ip": "192.168.0.203", "type": "MOTOR-V", "state": "BOTTOM", "tags": ["entrance"] }'
// );

// persistState(
//     'states/shades/13',
//     '{"ip": "192.168.0.204", "type": "MOTOR-V", "state": "BOTTOM", "tags": ["entrance"] }'
// );

// persistState(
//     'states/switch/12',
//     '{"ip": "192.168.0.203", "type": "SWITCH", "state": "OFF", "tags": ["living-room","disco", "window", "door"] }'
// );
