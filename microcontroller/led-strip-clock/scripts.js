window.addEventListener('DOMContentLoaded', (event) => {
    var slider = document.getElementById("slider");

    slider.oninput = function () {
        debouncedSlider(this.value);
    }

    const xhr = send('/settings/values');

    xhr.onload = function () {
        if (xhr.status == 200) {
            const response = JSON.parse(xhr.response);

            console.log('111');
            console.log(response);

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