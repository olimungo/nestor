// common-scripts.js must be loaded before this file

const documentTitle = 'Switch';

window.addEventListener('DOMContentLoaded', (event) => {
    getValues();
});

function getValues() {
    fetchWithTimeout('/settings/values', {
        timeout: 3000
    })
        .then(response => response.json())
        .then(response => {
            setTagValue('ip', response.ip);
            setTagValue('tag-net-id', response.netId);
            setTagValue('switch', response.state);

            document.title = `${documentTitle} ${response.netId}`;
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