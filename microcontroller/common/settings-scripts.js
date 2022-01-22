// common-scripts.js must be loaded before this file

window.addEventListener('DOMContentLoaded', (event) => {
    getValues();
    getSsids();
});

function getValues() {
    fetchWithTimeout('/settings/config', {
        timeout: 3000,
    })
        .then((response) => response.json())
        .then((response) => {
            setTagValue('ip', response.ip);
            setTagValue('net-id', response.netId);
        })
        .catch(() => setTimeout(getValues, 3000));
}

function toggle() {
    const action = document.getElementById('switch').checked ? 'on' : 'off';

    fetchWithTimeout(`/action/toggle?action=${action}`, {
        timeout: 3000,
    }).catch(() => setTimeout(toggle, 3000));
}

function setNetId() {
    const value = document.getElementById('net-id').value;
    fetch(`/settings/net-id?id=${value}`).then();
}

const debouncedSetNetId = debounce(setNetId, 1000);

function hideAll() {
    const settings = document.getElementById('settings'),
        password = document.getElementById('password'),
        connection = document.getElementById('connection'),
        connectionSuccess = document.getElementById('connection-success');

    settings.classList.add('display-none');
    password.classList.add('display-none');
    connection.classList.add('display-none');
    connectionSuccess.classList.add('display-none');
}

function displaySettings() {
    hideAll();

    const settings = document.getElementById('settings'),
        ssidsList = document.getElementById('ssids-list');

    settings.classList.remove('display-none');
    ssidsList.innerHTML = '';

    getSsids();
}

function displayPassword() {
    hideAll();

    const password = document.getElementById('password');
    password.classList.remove('display-none');
}

function displayConnection() {
    hideAll();

    const connection = document.getElementById('connection');
    connection.classList.remove('display-none');
}

function displayConnectionSuccess() {
    hideAll();

    const connectionSucces = document.getElementById('connection-succes');
    connectionSucces.classList.remove('display-none');
}

function getSsids() {
    fetchWithTimeout('/settings/ssids', {
        timeout: 15000,
    })
        .then((response) => response.json())
        .then((response) => response.ssids)
        .then((response) => {
            const ssidsList = document.getElementById('ssids-list');

            response.forEach((elem) => {
                const li = document.createElement('li'),
                    text = document.createTextNode(elem),
                    ssid = document.getElementById('ssid');

                li.classList.add('li');

                li.onclick = (_) => {
                    ssid.textContent = elem;
                    displayPassword();
                };

                li.appendChild(text);
                ssidsList.appendChild(li);
            });

            const appSpinner = document.getElementById('app-spinner');
            appSpinner.classList.add('display-none');

            const app = document.getElementById('app');
            app.classList.remove('display-none');
        })
        .catch((err) => setTimeout(getSsids, 3000));
}

function checkConnection() {
    fetchWithTimeout('/settings/config', {
        timeout: 3000,
    })
        .then((response) => response.json())
        .then((response) => {
            if (response.ip != '1.2.3.4' && response.ip != '0.0.0.0') {
                setTagValue('new-ip', response.ip);

                const connection = document.getElementById('connection'),
                    connectionSuccess =
                        document.getElementById('connection-success'),
                    newIp = document.getElementById('new-ip');

                connection.classList.add('display-none');
                connectionSuccess.classList.remove('display-none');
                newIp.href = `http://${response.ip}`;

                fetch(`/settings/router-ip-received`).then();
            } else {
                setTimeout(checkConnection, 3000);
            }
        })
        .catch((err) => setTimeout(checkConnection, 3000));
}

function connect() {
    const ssid = document.getElementById('ssid').textContent;
    const inputPasword = document.getElementById('input-password');

    fetch(`/connect?essid=${ssid}&password=${inputPasword.value}`).then();

    displayConnection();
    setTimeout(checkConnection, 3000);
}
