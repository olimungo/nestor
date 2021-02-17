window.addEventListener('DOMContentLoaded', (event) => {
    fetch('/settings/values')
        .then(response => response.json())
        .then(response => {
            setTagValue('ip', response.ip);
            setTagValue('net-id', response.netId);
            setTagValue('tag-net-id', response.netId);
            setTagValue('motor-reversed', response.motorReversed);

            document.title = `Shade ${response.netId}`;
        });
});


function setTagValue(tagId, value) {
    const tag = document.getElementById(tagId);
    tag.tagName == 'INPUT' ? tag.type == 'checkbox' ? (tag.checked = parseInt(value)) : (tag.value = value) : (tag.textContent = value);
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

function setNetId(value) {
    fetch(`/settings/net?id=${value}`).then();
    const tag = document.getElementById('tag-net-id');
    tag.textContent = value;
    document.title = `Shade ${value}`;
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
    const settings = document.getElementById('settings');
    settings.classList.remove('hidden');

    console.log('000');

    fetch('/settings/ssids')
        .then(response => response.json())
        .then(response => response.ssids)
        .then(response => {
            const ssidsList = document.getElementById('ssids-list');

            response.forEach(element => {
                const li = document.createElement("li");
                const text = document.createTextNode(element);

                li.onclick(displayPassword)

                li.appendChild(text);
                ssidsList.appendChild(li);
            });
        })
}

function displayPassword(event) {
    console.log(event);
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

async function fetchWithTimeout(resource, options) {
    const { timeout = 8000 } = options;

    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(resource, {
        ...options,
        signal: controller.signal
    });

    clearTimeout(id);

    return response;
}

function checkConnection() {
    try {
        return fetchWithTimeout('/settings/values', {
            timeout: 3000
        })
            .then(response => response.json())
            .then(response => {
                if (response.ip != '192.168.4.1') {
                    setTagValue('new-ip', response.ip);

                    const connection = document.getElementById('connection');
                    const connectionSuccess = document.getElementById('connection-success');

                    connection.classList.add('hidden');
                    connectionSuccess.classList.remove('hidden');
                }
                else {
                    setTimeout(checkConnection, 3000);
                }
            });
    } catch (error) {
        setTimeout(checkConnection, 3000);
    }
}

function connect() {
    const essid = document.getElementById('essid'),
        pwd = document.getElementById('pwd'),
        settings = document.getElementById('settings'),
        connection = document.getElementById('connection');

    fetch(`/connect?essid=${essid.value}&password=${pwd.value}`).then();

    settings.classList.add('hidden');
    connection.classList.remove('hidden');

    setTimeout(checkConnection, 3000);
}