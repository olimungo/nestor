// common-scripts.js must be loaded before this file

window.addEventListener('DOMContentLoaded', (event) => {
    const queryString = window.location.search;

    if (queryString !== '') {
        const urlParams = new URLSearchParams(queryString);

        if (urlParams.has('motor')) {
            const motor = document.getElementById('motor');
            motor.classList.remove('hidden-position-fixed');
        }
    }

    getValues();
    getSsids();
});

function getValues() {
    fetchWithTimeout('/settings/values', {
        timeout: 3000
    })
        .then(response => response.json())
        .then(response => {
            setTagValue('ip', response.ip);
            setTagValue('net-id', response.netId);
            // setTagValue('motor-reversed', response.motorReversed);
        })
        .catch(() => setTimeout(getValues, 3000));
}

function toggle() {
    const action = document.getElementById('switch').checked ? 'on' : 'off';

    fetchWithTimeout(`/action/toggle?action=${action}`, {
        timeout: 3000
    })
    .catch(() => setTimeout(toggle, 3000));
}

function setNetId(value) {
    fetch(`/settings/net-id?id=${value}`).then();
    const tag = document.getElementById('tag-net-id');
    tag.textContent = value;
    document.title = `SWITCH ${value}`;
}

const debouncedSetNetId = debounce(setNetId, 500);

function hideAll() {
    const settings = document.getElementById('settings'),
        password = document.getElementById('password'),
        connection = document.getElementById('connection'),
        connectionSuccess = document.getElementById('connection-success');

    settings.classList.add('hidden-position-fixed');
    password.classList.add('hidden-position-fixed');
    connection.classList.add('hidden-position-fixed');
    connectionSuccess.classList.add('hidden-position-fixed');
}

function displaySettings() {
    hideAll();

    const settings = document.getElementById('settings'),
        ssidsList = document.getElementById('ssids-list');

    settings.classList.remove('hidden-position-fixed');
    ssidsList.innerHTML = '';

    getSsids();
}

function displayPassword() {
    hideAll();

    const password = document.getElementById('password');
    password.classList.remove('hidden-position-fixed');
}

function displayConnection() {
    hideAll();

    const connection = document.getElementById('connection');
    connection.classList.remove('hidden-position-fixed');
}

function displayConnectionSuccess() {
    hideAll();

    const connectionSucces = document.getElementById('connection-succes');
    connectionSucces.classList.remove('hidden-position-fixed');
}

function getSsids() {
    const spinnerWifi = document.getElementById('spinner-wifi');
    spinnerWifi.classList.remove('hidden-position-fixed');

    fetchWithTimeout('/settings/ssids', {
        timeout: 15000
    })
        .then(response => response.json())
        .then(response => response.ssids)
        .then(response => {
            const ssidsList = document.getElementById('ssids-list');

            response.forEach(elem => {
                const li = document.createElement("li"),
                    text = document.createTextNode(elem),
                    ssid = document.getElementById('ssid');

                li.classList.add('li');

                li.onclick = _ => {
                    ssid.textContent = elem;
                    displayPassword();
                };

                li.appendChild(text);
                ssidsList.appendChild(li);

            });

            spinnerWifi.classList.add('hidden-position-fixed')
        })
        .catch((err) => setTimeout(getSsids, 3000));
}

function checkConnection() {
    fetchWithTimeout('/settings/values', {
        timeout: 3000
    })
        .then(response => response.json())
        .then(response => {
            if (response.ip != '1.2.3.4') {
                setTagValue('new-ip', response.ip);

                const connection = document.getElementById('connection'),
                    connectionSuccess = document.getElementById('connection-success'),
                    newIp = document.getElementById('new-ip');

                connection.classList.add('hidden-position-fixed');
                connectionSuccess.classList.remove('hidden-position-fixed');
                newIp.href = `http://${response.ip}`;

                fetch(`/settings/router-ip-received`).then();
            }
            else {
                setTimeout(checkConnection, 3000);
            }
        })
        .catch(err => setTimeout(checkConnection, 3000));
}

function connect() {
    const ssid = document.getElementById('ssid').textContent,
        pwd = document.getElementById('pwd'),
        password = document.getElementById('password'),
        connection = document.getElementById('connection');

    fetch(`/connect?essid=${ssid}&password=${pwd.value}`).then();

    displayConnection();
    setTimeout(checkConnection, 3000);
}