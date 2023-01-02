const fs = require('fs');

const input = fs
    .readFileSync(
        '/Users/olimungo/Projects/DIY/nestor/stage/advent/input-14.txt'
    )
    .toString();

let lines = input.split(/\r?\n/);
const rules = lines.map((line) => line.split(' -> '));

const nextStep = (template, rules) => {
    console.log(`template length: ${template.length}`);
    let result = '';

    for (let i = 0; i < template.length - 1; i++) {
        const token = template[i] + template[i + 1];

        let toInject = rules
            .filter((rule) => rule[0] === token)
            .map((rule) => rule[1]);
        toInject = toInject.length > 0 ? toInject[0] : '';

        result += `${template[i]}${toInject}`;
    }

    return `${result}${template[template.length - 1]}`;
};

// let result = 'OOVSKSPKPPPNNFFBCNOV';
let result = 'NNCB';

for (let i = 0; i < 40; i++) {
    console.log(`step ${i}`);
    result = nextStep(result, rules);
}

const counts = {};

for (const char of result) {
    if (counts[char]) {
        counts[char] += 1;
    } else {
        counts[char] = 1;
    }
}

let most = 0;
let least = Number.MAX_SAFE_INTEGER;

for (const count in counts) {
    most = counts[count] > most ? counts[count] : most;
    least = counts[count] < least ? counts[count] : least;
}

console.log({ counts, most, least, total: most - least });
