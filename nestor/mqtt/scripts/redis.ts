import * as redis from 'redis';
const { promisify } = require('util');

const redisClient = redis.createClient(
    process.env.REDIS_URL || 'redis://localhost'
);

redisClient.on('error', (error) => {
    if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
        console.log('Redis container not yet available...');
    }
});

redisClient.on('connect', () => console.log('connected...'));

export default {
    ...redisClient,
    getAsync: promisify(redisClient.get).bind(redisClient),
    setAsync: promisify(redisClient.set).bind(redisClient),
    keysAsync: promisify(redisClient.keys).bind(redisClient),
    delAsync: promisify(redisClient.del).bind(redisClient),
    saddAsync: promisify(redisClient.sadd).bind(redisClient),
    smembersAsync: promisify(redisClient.smembers).bind(redisClient),
    sremAsync: promisify(redisClient.srem).bind(redisClient),
};
