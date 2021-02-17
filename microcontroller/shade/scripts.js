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
    const settings = document.getElementById('settings'),
        ssidsList = document.getElementById('ssids-list');

    settings.classList.remove('hidden');
    ssidsList.innerHTML = '';

    fetch('/settings/ssids')
        .then(response => response.json())
        .then(response => response.ssids)
        .then(response => {

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
        })
        .catch(err => console.log(err));
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

function checkConnection() {
    fetchWithTimeout('/settings/values', {
        timeout: 3000
    })
        .then(response => response.json())
        .then(response => {
            if (response.ip != '192.168.4.1') {
                setTagValue('new-ip', response.ip);

                const connection = document.getElementById('connection'),
                    connectionSuccess = document.getElementById('connection-success');

                connection.classList.add('hidden');
                connectionSuccess.classList.remove('hidden');
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
        
    password.classList.add('hidden');
    connection.classList.remove('hidden');

    fetch(`/connect?essid=${ssid}&password=${pwd.value}`).then();

    setTimeout(checkConnection, 3000);
}