import {
    cleanDatabase,
    saveState,
    getCommands,
    getTimestamps,
    deleteKey,
    setKey,
} from './database';
import { log } from './logger';
import { mockData } from './mocks';

const DEBUG_MOCK_DATA = true;
const DEBUG_KEEP_DEVICE = true;
const LIMIT_TO_BE_REMOVED = 4000; // milliseconds
const CHECK_LAST_STATUS_FREQUENCY = 250; // milliseconds
const CHECK_COMMANDS_FREQUENCY = 100; // milliseconds
const MOSQUITTO_URL = process.env.MOSQUITTO_URL || 'mqtt://nestor.local';
const mqtt = require('mqtt').connect(MOSQUITTO_URL);

mqtt.on('connect', async () => {
    console.log(`> MQTT server connected to ${MOSQUITTO_URL}`);

    await cleanDatabase();

    mqtt.subscribe('#');

    if (DEBUG_MOCK_DATA) {
        mockData();
    }
});

mqtt.on('message', (topic, message) => {
    const split = topic.split('/');

    if (split.length) {
        if (split[0] === 'states') {
            saveState(topic, message.toString());
        } else if (split[0] === 'logs') {
            log(message.toString());
        }
    }
});

setInterval(() => {
    getCommands().then((commands) =>
        commands.map((command) => {
            mqtt.publish(command.key, command.value);
        })
    );
}, CHECK_COMMANDS_FREQUENCY);

if (!DEBUG_KEEP_DEVICE) {
    setInterval(() => {
        const now = new Date().getTime();

        getTimestamps().then((timestamps) => {
            timestamps.map(async (timestamp) => {
                if (parseInt(timestamp.value) + LIMIT_TO_BE_REMOVED < now) {
                    const device = timestamp.key.replace('timestamps/', '');

                    await deleteKey(timestamp.key);
                    await deleteKey(device);
                    await setKey('updated', 'true');
                }
            });
        });
    }, CHECK_LAST_STATUS_FREQUENCY);
}
