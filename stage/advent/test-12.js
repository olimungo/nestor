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

const checkPath = (paths, path, nodeName) => {
    const localPath = [...path, nodeName];

    if (nodeName == 'end') {
        paths.push(localPath);
        return paths;
    }

    nodes[nodeName].forEach((subnode) => {
        if (subnode !== 'start') {
            if (
                subnode !== subnode.toLowerCase() ||
                !path.some((item) => item === subnode)
            ) {
                paths = checkPath(paths, localPath, subnode);
            }
        }
    });

    return paths;
};

const paths = checkPath([], [], 'start');
console.log(paths.length);
