window.addEventListener('DOMContentLoaded', (event) => {
    getValues();
});

async function fetchWithTimeout(resource, options) {
    const { timeout = 8000 } = options,
        controller = new AbortController(),
        id = setTimeout(() => controller.abort(), timeout),
        response = await fetch(resource, {
            ...options,
            signal: controller.signal
        });

    clearTimeout(id);

    return response;
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

function getValues() {
    fetchWithTimeout('/settings/values', {
        timeout: 3000
    })
        .then(response => response.json())
        .then(response => {
            setTagValue('ip', response.ip);
            setTagValue('net-id', response.netId);
            setTagValue('tag-net-id', response.netId);
            setTagValue('switch', response.state);

            document.title = `Switch ${response.netId}`;
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

function setTagValue(tagId, value) {
    const tag = document.getElementById(tagId);
    tag.tagName == 'INPUT' ? tag.type == 'checkbox' ? (tag.checked = parseInt(value)) : (tag.value = value) : (tag.textContent = value);
}

function setNetId(value) {
    fetch(`/settings/net-id?id=${value}`).then();
    const tag = document.getElementById('tag-net-id');
    tag.textContent = value;
    document.title = `SWITCH ${value}`;
}

const debouncedSetNetId = debounce(setNetId, 500);

function hideAll() {
    const main = document.getElementById('main'),
        settings = document.getElementById('settings'),
        password = document.getElementById('password'),
        connection = document.getElementById('connection'),
        connectionSuccess = document.getElementById('connection-success');

    main.classList.add('hidden');
    settings.classList.add('hidden');
    password.classList.add('hidden');
    connection.classList.add('hidden');
    connectionSuccess.classList.add('hidden');
}

function displayMain() {
    hideAll();
    const main = document.getElementById('main');
    main.classList.remove('hidden');
}

function displaySettings() {
    hideAll();
    const settings = document.getElementById('settings'),
        ssidsList = document.getElementById('ssids-list');

    settings.classList.remove('hidden');
    ssidsList.innerHTML = '';

    getSsids();
}

function displayPassword() {
    hideAll();
    const password = document.getElementById('password');
    password.classList.remove('hidden');
}

function displayConnection() {
    hideAll();
    const connection = document.getElementById('connection');
    connection.classList.remove('hidden');
}

function displayConnectionSuccess() {
    hideAll();
    const connectionSucces = document.getElementById('connection-succes');
    connectionSucces.classList.remove('hidden');
}

function getSsids() {
    const spinnerWifi = document.getElementById('spinner-wifi');
    spinnerWifi.classList.remove('hidden');

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

            spinnerWifi.classList.add('hidden')
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

                connection.classList.add('hidden');
                connectionSuccess.classList.remove('hidden');
                newIp.href = `http://${response.ip}`;

                fetch(`/settings/shutdown-ap`).then();
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