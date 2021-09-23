// common-scripts.js must be loaded before this file

const documentTitle = 'Shade';

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

            document.title = `${documentTitle} ${response.netId}`;
        })
        .catch(() => setTimeout(getValues, 3000));
}
