window.addEventListener('DOMContentLoaded', (event) => {
    const slider = document.getElementById("slider");
    const canvas = document.getElementById('canvas');

    slider.oninput = function () {
        debouncedSlider(this.value);
    }

    // canvas.onclick = colorWheelMouse;
    // window.onresize = setCanvasSize;

    // setCanvasSize()

    const p = document.body.appendChild(document.createElement("p"));

    const xhr = send('/settings/values');

    xhr.onload = function () {
        if (xhr.status == 200) {
            const response = JSON.parse(xhr.response);

            setTagValue('ip', response.ip);
            setTagValue('net-id', response.netId);
            setTagValue('tag-net-id', response.netId);
            setTagValue('group', response.group);
            setTagValue('essid', response.essid);

            const slider = document.getElementById('slider');
            slider.value = response.brightness;

            document.title += ` ${response.netId}`;
        }
    };
});

const debouncedSlider = debounce((value) => {
    send(`/action/brightness?l=${value}`);
}, 500);

function setTagValue(tagId, value) {
    const tag = document.getElementById(tagId);
    tag.tagName == 'INPUT' ? (tag.value = value) : (tag.textContent = value);
}

function debounce(fn, wait = 100) {
    let timeout;

    return function (...args) {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            fn.apply(this, args);
        }, wait);
    };
}

function send(action) {
    const http = new XMLHttpRequest();
    http.open('GET', action);
    http.send();

    return http;
}

function setColor(hex) {
    const xhr = send(`/action/color?hex=${hex}`);

    xhr.onload = function () {
        if (xhr.status == 200) {
            const response = JSON.parse(xhr.response);
            const slider = document.getElementById('slider');
            slider.value = response.brightness;
        }
    }
}

function setNetId(value) {
    send(`/settings/net?id=${value}`);
    const tag = document.getElementById('tag-net-id');
    tag.textContent = value;
}

const debouncedSetNetId = debounce(setNetId, 500);

function setGroup(value) {
    send(`/settings/group?name=${value}`);
}

const debouncedSetGroup = debounce(setGroup, 500);

function displayMain() {
    const main = document.getElementById('main'),
        settings = document.getElementById('settings');
    main.classList.remove('hidden');
    settings.classList.add('hidden');
}

function displaySettings() {
    const main = document.getElementById('main'),
        settings = document.getElementById('settings');
    main.classList.add('hidden');
    settings.classList.remove('hidden');
}

function displayConnectionInProgress() {
    const settings = document.getElementById('settings'),
        connection = document.getElementById('connection');
    settings.classList.add('hidden');
    connection.classList.remove('hidden');

    setTimeout(checkConnection, 3000);
}

function checkConnection() {
    const xhr = send('/settings/values');

    xhr.onload = function () {
        let tryAgain = false;

        if (xhr.status == 200) {
            const response = JSON.parse(xhr.response);

            if (response.ip != "192.168.4.1") {
                setTagValue('new-ip', response.ip);

                const spinner = document.getElementById('spinner'),
                    newIp = document.getElementById('new-ip');

                spinner.classList.add('hidden');
                newIp.classList.remove('hidden');
            } else {
                tryAgain = true;
            }
        } else {
            tryAgain = true;
        }

        if (tryAgain) {
            setTimeout(checkConnection, 3000)
        }
    };
}

function connect() {
    const essid = document.getElementById('essid');
    const pwd = document.getElementById('pwd');

    send(`/connect?essid=${essid.value}&password=${pwd.value}`);

    displayConnectionInProgress();
}

function degreesToRadians(degrees) {
    return degrees * (Math.PI / 180);
}

function drawColorWheel(canvas) {
    const context = canvas.getContext('2d');
    const centerColor = 'white';

    // Initiate variables
    let angle = 0;
    const hexCode = [0, 0, 255];
    let pivotPointer = 0;
    const colorOffsetByDegree = 4.322;
    const radius = canvas.width / 2;

    // For each degree in circle, perform operation
    while (angle < 360) {
        // find index immediately before and after our pivot
        const pivotPointerbefore = (pivotPointer + 3 - 1) % 3;

        // Modify colors
        if (hexCode[pivotPointer] < 255) {
            // If main points isn't full, add to main pointer
            hexCode[pivotPointer] =
                hexCode[pivotPointer] + colorOffsetByDegree > 255 ?
                    255 :
                    hexCode[pivotPointer] + colorOffsetByDegree;
        } else if (hexCode[pivotPointerbefore] > 0) {
            // If color before main isn't zero, subtract
            hexCode[pivotPointerbefore] =
                hexCode[pivotPointerbefore] > colorOffsetByDegree ?
                    hexCode[pivotPointerbefore] - colorOffsetByDegree :
                    0;
        } else if (hexCode[pivotPointer] >= 255) {
            // If main color is full, move pivot
            hexCode[pivotPointer] = 255;
            pivotPointer = (pivotPointer + 1) % 3;
        }

        const rgb = `rgb(${hexCode.map(h => Math.floor(h)).join(',')})`;
        const grad = context.createRadialGradient(
            radius,
            radius,
            0,
            radius,
            radius,
            radius
        );
        grad.addColorStop(0, centerColor);
        grad.addColorStop(1, rgb);
        context.fillStyle = grad;

        // draw circle portion
        context.globalCompositeOperation = 'source-over';
        context.beginPath();
        context.moveTo(radius, radius);
        context.arc(
            radius,
            radius,
            radius,
            degreesToRadians(angle),
            degreesToRadians(360)
        );
        context.closePath();
        context.fill();
        angle++;
    }
}

function colorWheelMouse(evt) {
    const ctx = canvas.getContext("2d");
    const data = ctx.getImageData(evt.offsetX, evt.offsetY, 1, 1);

    rgb = data.data.slice(0, 3)
    r = rgb[0]; g = rgb[1]; b = rgb[2]

    if (r !== 0 && g !== 0 && b !== 0) {
        console.log(`RGB: ${data.data.slice(0, 3).join(',')}`);
    }
}

function setCanvasSize(event) {
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    const width = canvas.clientWidth;
    const height = canvas.clientHeight;

    canvas.width = width;
    canvas.height = height;

    context.clearRect(0, 0, canvas.width, canvas.height);
    drawColorWheel(canvas);
}