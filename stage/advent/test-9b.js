const sample = [
    '2199943210',
    '3987894921',
    '9856789892',
    '8767896789',
    '9899965678',
];

const formatSample = (sample) => {
    return sample.map((line, indexLine) =>
        line.split('').map((point, indexPoint) => ({
            depth: parseInt(point),
            indexLine,
            indexPoint,
            alreadyProcessed: false,
            toBeProcessed: false,
            bassin: null,
        }))
    );
};

const getNeighbours = (sample, indexLine, indexPoint) => {
    let pointUp = { depth: 99 };
    let pointDown = { depth: 99 };
    let pointRight = { depth: 99 };
    let pointLeft = { depth: 99 };

    if (indexLine > 0 && !sample[indexLine - 1][indexPoint].alreadyProcessed) {
        pointUp = sample[indexLine - 1][indexPoint];
    }

    if (
        indexLine < sample.length - 1 &&
        !sample[indexLine + 1][indexPoint].alreadyProcessed
    ) {
        pointDown = sample[indexLine + 1][indexPoint];
    }

    if (indexPoint > 0 && !sample[indexLine][indexPoint - 1].alreadyProcessed) {
        pointRight = sample[indexLine][indexPoint - 1];
    }

    if (
        indexPoint < sample[indexLine].length - 1 &&
        !sample[indexLine][indexPoint + 1].alreadyProcessed
    ) {
        pointLeft = sample[indexLine][indexPoint + 1];
    }

    return { pointUp, pointDown, pointRight, pointLeft };
};

const findLowestPoints = (sample) => {
    const lowestPoints = [];

    sample.forEach((line, indexLine) => {
        line.forEach((point, indexPoint) => {
            ({ pointUp, pointDown, pointRight, pointLeft } = getNeighbours(
                sample,
                indexLine,
                indexPoint
            ));

            if (
                point.depth < pointUp.depth &&
                point.depth < pointDown.depth &&
                point.depth < pointRight.depth &&
                point.depth < pointLeft.depth
            ) {
                lowestPoints.push(point);
                point.bassin = {
                    indexLine,
                    indexPoint,
                    point: point.depth,
                    pointIndexLine: point.indexLine,
                    pointIndexPoint: point.indexPoint,
                };

                if (pointUp.depth < 9) {
                    pointUp.bassin = point.bassin;
                    pointUp.toBeProcessed = true;
                }

                if (pointDown.depth < 9) {
                    pointDown.bassin = point.bassin;
                    pointDown.toBeProcessed = true;
                }

                if (pointRight.depth < 9) {
                    pointRight.bassin = point.bassin;
                    pointRight.toBeProcessed = true;
                }

                if (pointLeft.depth < 9) {
                    pointLeft.bassin = point.bassin;
                    pointLeft.toBeProcessed = true;
                }
            }
        });
    });

    lowestPoints.forEach((point) => (point.alreadyProcessed = true));

    return lowestPoints;
};

const getToBeProcessed = (sample) => {
    const toBeProcessed = [];

    sample.forEach((line) => {
        line.forEach((point) => {
            if (point.toBeProcessed && !point.alreadyProcessed) {
                toBeProcessed.push(point);
            }
        });
    });

    return toBeProcessed;
};

const display = (sample) => {
    sample.forEach((line) => {
        let output = '';

        line.forEach((point) => {
            if (point.bassin !== null) {
                output += 'X';
            } else {
                output += point.depth;
            }
        });

        console.log(output);
    });
};

const sampleFormatted = formatSample(sample);
const lowestPoints = findLowestPoints(sampleFormatted);

console.log(lowestPoints.reduce((acc, item) => acc + item.depth + 1, 0));

let toBeProcessed = getToBeProcessed(sampleFormatted);

while (toBeProcessed.length > 0) {
    const point = toBeProcessed.pop();

    ({ pointUp, pointDown, pointRight, pointLeft } = getNeighbours(
        sampleFormatted,
        point.indexLine,
        point.indexPoint
    ));

    point.alreadyProcessed = true;

    if (pointUp.depth < 9) {
        pointUp.bassin = point.bassin;
        pointUp.toBeProcessed = true;
    }

    if (pointDown.depth < 9) {
        pointDown.bassin = point.bassin;
        pointDown.toBeProcessed = true;
    }

    if (pointRight.depth < 9) {
        pointRight.bassin = point.bassin;
        pointRight.toBeProcessed = true;
    }

    if (pointLeft.depth < 9) {
        pointLeft.bassin = point.bassin;
        pointLeft.toBeProcessed = true;
    }

    toBeProcessed = getToBeProcessed(sampleFormatted);
}

// display(sampleFormatted);

const bassins = [];
sampleFormatted.forEach((line) => {
    line.forEach((point) => {
        if (point.bassin != null) {
            bassins.push(point.bassin);
        }
    });
});

results = {};
bassins.forEach((bassin) => {
    if (results[bassin.indexLine + ';' + bassin.indexPoint]) {
        results[bassin.indexLine + ';' + bassin.indexPoint] += 1;
    } else {
        results[bassin.indexLine + ';' + bassin.indexPoint] = 1;
    }
});

const total = Object.values(results)
    .sort((a, b) => (a > b ? -1 : 1))
    .slice(0, 3)
    .reduce((acc, elem) => (acc *= elem), 1);

console.log(total);
