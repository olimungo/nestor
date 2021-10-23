import { KeyValue } from './models';
import redis from './redis';

export const cleanDatabase = async () => {
    await redis.delAsync('updated');
};

export async function getDevices(): Promise<KeyValue[]> {
    const result: KeyValue[] = [];
    const states: string[] = await redis.keysAsync('states/*');

    await Promise.all(
        states.map(async (state: string) => {
            const value = await redis.getAsync(state);

            result.push({ key: state, value });
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

export async function getUpdated() {
    const updated = await redis.getAsync('updated');
    await redis.delAsync('updated');

    return updated === 'true';
}
