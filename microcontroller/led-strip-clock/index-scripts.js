// common-scripts.js must be loaded before this file

const documentTitle = 'Clock';

window.addEventListener('DOMContentLoaded', (event) => {
    getValues();
});

const debouncedSlider = debounce((value) => {
    fetch(`/action/brightness?l=${value}`).then();
}, 500);

function getValues() {
    fetchWithTimeout('/settings/config', {
        timeout: 3000,
    })
        .then((response) => response.json())
        .then((response) => {
            setTagValue('ip', response.ip);
            setTagValue('tag-net-id', response.netId);
            setTagValue('hex', response.color);

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

function setColor(hex) {
    fetch(`/action/color?hex=${hex}`)
        .then((response) => response.json())
        .then((response) => {
            setTagValue('slider', response.brightness);
            setTagValue('hex', hex);
        });
}

function setManualColor() {
    const hex = document.getElementById('hex');

    if (hex.value.match(/\b[0-9A-F]{6}\b/gi)) {
        fetch(`/action/color?hex=${hex.value}`)
            .then((response) => response.json())
            .then((response) => {
                setTagValue('slider', response.brightness);
            });
    }
}
