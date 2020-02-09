const mqtt = require('mqtt');
const log = require('./logger').log;

const BROKER = `mqtt://${process.env.MQTT_BROKER}`;
let client;
let callbackMessageReceived;

let states = [];

exports.connect = callback => {
    callbackMessageReceived = callback;

    client = mqtt.connect(BROKER);

    client.on('connect', postConnect);
    client.on('message', gotMessage);
};

exports.getStates = () =>
    states.map(item => ({
        netId: item.netId,
        group: item.group,
        state: item.state
    }));

exports.sendMessage = (topic, message) => {
    client.publish(topic, message);
};

function postConnect() {
    client.subscribe('shades/states/#');
    client.subscribe('logs/#');

    // Remove devices which aren't alive (the ones that didn't send a message since 35 seconds)
    setInterval(_ => {
        const now = new Date().getTime();

        states = states.filter(item => now - item.date.getTime() < 35000);
    }, 1000);
}

function gotMessage(topic, message) {
    if (topic.indexOf('logs/') > -1) {
        callbackMessageReceived('logs', topic, message);
    }

    if (topic.indexOf('shades/states/') > -1) {
        netId = parseInt(topic.split('shades/states/')[1]);

        try {
            jsonMessage = JSON.parse(message.toString());

            states = states.filter(item => item.netId != netId);
            states.push({
                netId,
                group: jsonMessage.group,
                state: jsonMessage.state,
                date: new Date()
            });

            states = states.sort((a, b) => (a.netId < b.netId ? -1 : 1));

            callbackMessageReceived(
                'states',
                topic,
                message,
                states.map(item => ({
                    netId: item.netId,
                    group: item.group,
                    state: item.state
                }))
            );
        } catch (error) {
            log(`ERROR in mqtt.gotMessage: ${error}|${message.toString()}`);
        }
    }
}
