const fs = require('fs');

const input = fs
    .readFileSync(
        '/Users/olimungo/Projects/DIY/nestor/stage/advent/input-12.txt'
    )
    .toString();
const lines = input.split(/\r?\n/);
let map = [];

lines.forEach((line) => {
    map.push(line.split('-'));
});

let nodes = {};

map.forEach((line) => {
    if (!nodes[line[0]]) {
        nodes[line[0]] = [];
    }

    if (!nodes[line[1]]) {
        nodes[line[1]] = [];
    }

    nodes[line[0]].push(line[1]);
    nodes[line[1]].push(line[0]);
});

const checkSubNode = (subNode, path) => {
    // Start?
    if (subNode == 'start') {
        return false;
    }

    // Big cave?
    if (subNode !== subNode.toLowerCase()) {
        return true;
    }

    // Small cave but not already in the path?
    if (!path.some((item) => item === subNode)) {
        return true;
    }

    let localPath = path.filter(
        (item) => item !== 'start' && item === item.toLowerCase()
    );

    // Any node found twice in the path?
    for (let i = 0; i < localPath.length; i++) {
        const node = localPath[i];

        if (localPath.findIndex((item) => item === node) !== i) {
            return false;
        }
    }

    return true;
};

const checkPath = (paths, path, nodeName) => {
    const localPath = [...path, nodeName];

    if (nodeName == 'end') {
        paths.push(localPath);
        return paths;
    }

    nodes[nodeName].forEach((subNode) => {
        if (checkSubNode(subNode, localPath)) {
            paths = checkPath(paths, localPath, subNode);
        }
    });

    return paths;
};

const paths = checkPath([], [], 'start');
console.log(paths.length);
