import { appendFile } from 'fs';

export function log(message) {
    const data = getDateAndTime() + '|' + message;
    const dataArray = new Uint8Array(Buffer.from(data + '\n'));

    appendFile('messages.log', dataArray, (err) => {
        if (err) throw err;
    });
}

function getDateAndTime() {
    const now = new Date();

    const dayNum = now.getDate();
    const monthNum = now.getMonth() + 1;
    const year = now.getFullYear();
    const hoursNum = now.getHours();
    const minutesNum = now.getMinutes();
    const secondsNum = now.getSeconds();

    const day = ('0' + dayNum).slice(-2);
    const hours = ('0' + hoursNum).slice(-2);
    const month = ('0' + monthNum).slice(-2);
    const minutes = ('0' + minutesNum).slice(-2);
    const seconds = ('0' + secondsNum).slice(-2);

    return `${day}/${month}/${year}|${hours}:${minutes}:${seconds}`;
}
