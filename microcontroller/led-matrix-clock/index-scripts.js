// common-scripts.js must be loaded before this file

const documentTitle = 'Clock';

window.addEventListener('DOMContentLoaded', (event) => {
    getValues();
});

function getValues() {
    fetchWithTimeout('/settings/config', {
        timeout: 3000,
    })
        .then((response) => response.json())
        .then((response) => {
            console.log(response);

            setTagValue('ip', response.ip);
            setTagValue('tag-net-id', response.netId);

            document.title = `${documentTitle}-${response.netId}`;

            const slider = document.getElementById('slider');
            slider.value = response.brightness;

            const appSpinner = document.getElementById('app-spinner');
            appSpinner.classList.add('display-none');

            const app = document.getElementById('app');
            app.classList.remove('display-none');
        })
        .catch(() => setTimeout(getValues, 3000));
}

const debouncedSlider = debounce((value) => {
    fetch(`/action/brightness?l=${value}`).then();
}, 500);
