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

            const states = response.state.split(',');
            setTagValue('switch-1', states[0]);
            
            if(response.type == "DOUBLE-SWITCH") {
                document.getElementById(`switch-container-2`).classList.remove('hidden');
                setTagValue('switch-2', states[1]);
            }

            document.title = `${documentTitle} ${response.netId}`;
        })
        .catch(() => setTimeout(getValues, 3000));
}

function toggle(id) {
    const action = document.getElementById(`switch-${id}`).checked ? 'on' : 'off';

    fetchWithTimeout(`/action/toggle-${id}?action=${action}`, {
        timeout: 3000
    })
    .catch(() => setTimeout(toggle, 3000));
}