const fs = require('fs');
const path = require('path');

const input = fs
    .readFileSync(
        '/Users/olimungo/Projects/DIY/nestor/stage/advent/input-15.txt'
    )
    .toString();

let lines = input.split(/\r?\n/);

const map = [];

lines.forEach((line) => map.push(line.split('').map((item) => parseInt(item))));

const print = (map) => {
    map.forEach((line) => console.log(line.join('')));
};

const memoize = {};

const findLowestRiskPath = (map, x, y) => {
    if (y === map.length - 1 && x === map[0].length - 1) {
        return [`${x}:${y}`, map[y][x]];
    }

    if (memoize[`${x}:${y}`]) {
        return memoize[`${x}:${y}`];
    }

    const localMap = [];
    map.forEach((line) => localMap.push([...line]));

    localMap[y][x] = -1;

    let leftCost, rightCost, upCost, downCost;
    leftCost = rightCost = upCost = downCost = Number.MAX_VALUE;
    let leftPath, rightPath, upPath, downPath;
    leftPath = rightPath = upPath = downPath = '';

    if (x < map[y].length - 1) {
        [rightPath, rightCost] = findLowestRiskPath(localMap, x + 1, y);
    }

    if (x > 0) {
        [leftPath, leftCost] = findLowestRiskPath(localMap, x - 1, y);
    }

    if (y < map.length - 1) {
        [downPath, downCost] = findLowestRiskPath(localMap, x, y + 1);
    }

    if (y > 0) {
        [upPath, upCost] = findLowestRiskPath(localMap, x, y - 1);
    }

    const min = Math.min(rightCost, leftCost, upCost, downCost);

    let pathResult = '';

    switch (min) {
        case rightCost:
            pathResult = `${x}:${y} - ${rightPath}`;
            break;
        case leftCost:
            pathResult = `${x}:${y} - ${leftPath}`;
            break;
        case upCost:
            pathResult = `${x}:${y} - ${upPath}`;
            break;
        case downCost:
            pathResult = `${x}:${y} - ${downPath}`;
            break;
    }

    if (x === 6 && y === 3) {
        console.log(map[y][x] + min);
    }

    memoize[`${x}:${y}`] = [pathResult, map[y][x] + min];

    return [pathResult, map[y][x] + min];
};

// print(map);

[pathResult, cost] = findLowestRiskPath(map, 0, 0, 0);

console.log({ pathResult, cost });
