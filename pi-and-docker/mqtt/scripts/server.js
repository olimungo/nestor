
const express = require('express');
const mqtt = require('mqtt').connect(process.env.MOSQUITTO_URL || 'mqtt://nestor.local');
const redis = require('./redis');

mqtt.on('connect', () => mqtt.subscribe('#'));

mqtt.on('message', async (topic, message) => {
    const split = topic.split('/');

    if (split.length) {
        if (split[0] === 'states') {
            persistMessage(topic, message);
        } else if (split[0] === 'logs') {
            console.log('TBD: log to file');
        }
    }
});

const app = express();

app.get('/:key', async (req, res) => {
    const { key } = req.params;
    const rawData = await redis.getAsync(key);
    const rawData2 = await redis.keysAsync('*');
    console.log(rawData2);
    return res.send(rawData);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server listening on port ${PORT}`);
});

async function persistMessage(key, value) {
    const persistedValue = await redis.getAsync(key);

    // Check if key exists and if value has changed
    if (!persistedValue || persistedValue !== value.toString()) {
        await redis.setAsync('states/updated', 'states/updated');
        await redis.setAsync(key, value.toString());
    }
}