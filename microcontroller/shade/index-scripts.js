// common-scripts.js must be loaded before this file

const documentTitle = 'Shade';

window.addEventListener('DOMContentLoaded', (event) => {
    getValues();
});

function getValues() {
    fetchWithTimeout('/settings/values', {
        timeout: 3000,
    })
        .then((response) => response.json())
        .then((response) => {
            setTagValue('ip', response.ip);
            setTagValue('tag-net-id', response.netId);
            setTagValue('reverse-motor', response.motorReversed);

            document.title = `${documentTitle} ${response.netId}`;

            const appSpinner = document.getElementById('app-spinner');
            appSpinner.classList.add('display-none');

            const app = document.getElementById('app');
            app.classList.remove('display-none');
        })
        .catch(() => setTimeout(getValues, 3000));
}
