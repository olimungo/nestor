import { KeyValue } from './models';
import redis from './redis';

export const cleanDatabase = async () => {
    const keys = await redis.keysAsync('*');

    await Promise.all(
        keys.map(async (device) => {
            await redis.delAsync(device);
        })
    );
};

export async function saveState(key, value) {
    const savedStated = await redis.getAsync(key);

    // Check if key exists and if value has changed
    if (!savedStated || savedStated !== value) {
        await redis.setAsync(key, value);
        await redis.setAsync('updated', 'true');
    }

    await redis.setAsync(`timestamps/${key}`, new Date().getTime());
}

export async function getCommands(): Promise<KeyValue[]> {
    const result: KeyValue[] = [];
    const commands: string[] = await redis.keysAsync('commands/*');

    await Promise.all(
        commands.map(async (command: string) => {
            const value = await redis.getAsync(command);

            result.push({ key: command, value });

            await redis.delAsync(command);
        })
    );

    return result;
}

export async function getTimestamps(): Promise<KeyValue[]> {
    const result: KeyValue[] = [];
    const timestamps: string[] = await redis.keysAsync('timestamps/*');

    await Promise.all(
        timestamps.map(async (timestamp: string) => {
            const value = await redis.getAsync(timestamp);

            result.push({ key: timestamp, value });
        })
    );

    return result;
}

export async function deleteKey(key: string) {
    await redis.delAsync(key);
}

export async function setKey(key: string, value: string) {
    await redis.setAsync(key, value);
}
