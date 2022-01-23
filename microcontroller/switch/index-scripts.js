// common-scripts.js must be loaded before this file

const documentTitle = 'Switch';

window.addEventListener('DOMContentLoaded', (event) => {
    getValues();
});

function getValues() {
    fetchWithTimeout('/settings/config', {
        timeout: 3000,
    })
        .then((response) => response.json())
        .then((response) => {
            setTagValue('ip', response.ip);
            setTagValue('tag-net-id', response.netId);

            const states = response.state.split(',');
            setTagValue('switch-a', states[0] == 'ON' ? 1 : 0);

            if (response.type == 'DOUBLE-SWITCH') {
                document
                    .getElementById(`title-switch-a`)
                    .classList.remove('display-none');

                document
                    .getElementById(`switch-container-2`)
                    .classList.remove('display-none');
                setTagValue('switch-b', states[1] == 'ON' ? 1 : 0);
            }

            document.title = `${documentTitle}-${response.netId}`;
            document
                .getElementById('app-spinner')
                .classList.add('display-none');
            document.getElementById('app').classList.remove('display-none');
        })
        .catch(() => setTimeout(getValues, 3000));
}

function toggle(id) {
    const action = document.getElementById(`switch-${id}`).checked
        ? 'on'
        : 'off';

    fetchWithTimeout(`/action/toggle-${id}?action=${action}`, {
        timeout: 3000,
    }).catch(() => setTimeout(toggle, 3000));
}
