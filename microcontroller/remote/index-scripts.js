// common-scripts.js must be loaded before this file

const documentTitle = 'Remote';

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
            setTagValue('command-a', response.commandA);
            setTagValue('command-b', response.commandB);

            document.title = `${documentTitle}-${response.netId}`;
            document
                .getElementById('app-spinner')
                .classList.add('display-none');
            document.getElementById('app').classList.remove('display-none');
        })
        .catch((err) => {
            console.log(err);
            setTimeout(getValues, 3000);
        });
}

function sendCommand(button) {
    const command = document.getElementById(`command-${button}`);
    fetch(`/action/command?button=${button}&command=${command.value}`).then(
        () => {}
    );
}
