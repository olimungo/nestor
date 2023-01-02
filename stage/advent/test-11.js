const fs = require('fs');

const input = fs
    .readFileSync(
        '/Users/olimungo/Projects/DIY/nestor/stage/advent/input-11.txt'
    )
    .toString();
const lines = input.split(/\r?\n/);
let map = [];

lines.forEach((line) => {
    map.push(line.split('').map((item) => parseInt(item)));
});

const addOne = (map) => map.map((line) => line.map((item) => item + 1));

const aboutToFlash = (map) =>
    map.some((line) => line.some((item) => item == 10));

const checkIncrementItem = (map, x, y) => {
    const item = map[y][x];

    if (item !== 0 && item !== 10) {
        map[y][x] += 1;
    }

    return map;
};

const flash = (map, x, y) => {
    map[y][x] = 0;

    if (y > 0) {
        map = checkIncrementItem(map, x, y - 1);

        if (x > 0) {
            map = checkIncrementItem(map, x - 1, y - 1);
        }

        if (x < map[y - 1].length - 1) {
            map = checkIncrementItem(map, x + 1, y - 1);
        }
    }

    if (y < map.length - 1) {
        map = checkIncrementItem(map, x, y + 1);

        if (x > 0) {
            const downLeft = map[y + 1][x - 1];
            map = checkIncrementItem(map, x - 1, y + 1);
        }

        if (x < map[y + 1].length - 1) {
            map = checkIncrementItem(map, x + 1, y + 1);
        }
    }

    if (x > 0) {
        map = checkIncrementItem(map, x - 1, y);
    }

    if (x < map[y].length - 1) {
        map = checkIncrementItem(map, x + 1, y);
    }

    return map;
};

const checkForFlash = (map) => {
    for (let y = 0; y < map.length; y++) {
        for (let x = 0; x < map[y].length; x++) {
            if (map[y][x] == 10) {
                return { x, y };
            }
        }
    }

    return null;
};

function printMap(map) {
    for (let index = 0; index < map.length; index++) {
        console.log(`${map[index]}`);
    }
    console.log('------------------');
}

let countFlash = 0;

for (let i = 0; i < 100; i++) {
    map = addOne(map);

    while (aboutToFlash(map)) {
        toBeFlashed = checkForFlash(map);

        if (toBeFlashed) {
            map = flash(map, toBeFlashed.x, toBeFlashed.y);
            countFlash += 1;
        }
    }
}

printMap(map);
console.log({ countFlash });
