const fs = require('fs');

const input = fs
    .readFileSync(
        '/Users/olimungo/Projects/DIY/nestor/stage/advent/input-13.txt'
    )
    .toString();

const lines = input.split(/\r?\n/);

const foldingInstructionsLines = fs
    .readFileSync(
        '/Users/olimungo/Projects/DIY/nestor/stage/advent/input-13-folding-instructions.txt'
    )
    .toString();

const foldingInstructions = foldingInstructionsLines.split(/\r?\n/);

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

console.log({ maxX, maxY });

const foldY = (dots, foldingLine) => {
    let localDots = [...dots];
    const arr1 = localDots.filter((_, index) => index < foldingLine);
    const arr2 = localDots.filter((_, index) => index > foldingLine);

    if (arr1.length > arr2.length) {
        arr2.push(Array(arr1[0].length).fill(0));
    }

    const arr2Reversed = [];
    arr2.forEach((line) => arr2Reversed.unshift(line));

    localDots = arr1.map((line, indexLine) =>
        line.map((dot, indexDot) => dot || arr2Reversed[indexLine][indexDot])
    );

    return localDots;
};

const foldX = (dots, foldingLine) => {
    let localDots = [...dots];
    const arr1 = [];
    const arr2 = [];

    dots.forEach((line) => {
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

    localDots = arr1.map((line, indexLine) =>
        line.map((dot, indexDot) => dot || arr2Reversed[indexLine][indexDot])
    );

    return localDots;
};

const fold = (dots, direction, foldingLine) => {
    if (direction === 'x') {
        return foldX(dots, foldingLine);
    } else {
        return foldY(dots, foldingLine);
    }
};

let result = [...dots];

foldingInstructions.forEach((line) => {
    const instruction = line.replace('fold along ', '').split('=');
    result = fold(result, instruction[0], parseInt(instruction[1]));
});

result.forEach((line) => console.log(line.join('').replace(/0/g, ' ')));
