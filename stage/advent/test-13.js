const fs = require('fs');

const input = fs
    .readFileSync(
        '/Users/olimungo/Projects/DIY/nestor/stage/advent/input-13.txt'
    )
    .toString();

const lines = input.split(/\r?\n/);

let map = [];
let maxX = 0;
let maxY = 0;

lines.forEach((line) => {
    const split = line.split(',');
    x = parseInt(split[0]);
    y = parseInt(split[1]);

    if (x > maxX) {
        maxX = x;
    }

    if (y > maxY) {
        maxY = y;
    }

    map.push([x, y]);
});

let dots = Array(maxY + 1).fill(0);
dots = dots.map((line) => Array(maxX + 1).fill(0));

map.forEach((dotCoord) => {
    x = dotCoord[0];
    y = dotCoord[1];

    dots[y][x] = 1;
});

const foldX = (dots, foldingLine) => {
    const arr1 = [];
    const arr2 = [];

    dots.forEach((line, indexLine) => {
        const arr1Line = [];
        const arr2Line = [];

        line.forEach((dot, indexDot) => {
            if (indexDot < foldingLine) {
                arr1Line.push(dot);
            } else if (indexDot > foldingLine) {
                arr2Line.push(dot);
            }
        });

        arr1.push(arr1Line);
        arr2.push(arr2Line);
    });

    const arr2Reversed = [];
    arr2.forEach((line) => {
        const reversedLine = [];

        line.forEach((dot) => reversedLine.unshift(dot));

        arr2Reversed.push(reversedLine);
    });

    let result = arr1.map((line, indexLine) =>
        line.map((dot, indexDot) => dot || arr2Reversed[indexLine][indexDot])
    );

    return result;
};

const resultFoldX = foldX(dots, 655);

const countDotsFoldX = resultFoldX.reduce(
    (acc, line) => acc + line.reduce((acc, dot) => acc + dot),
    0
);

console.log(countDotsFoldX);
