// common-scripts.js must be loaded before this file

const documentTitle = 'Clock';

window.addEventListener('DOMContentLoaded', (event) => {
    getValues();

    const slider = document.getElementById('slider');

    slider.oninput = (event) => {
        debouncedSlider(event.target.value);
    }
});

const debouncedSlider = debounce((value) => {
    fetch(`/action/brightness?l=${value}`).then();
}, 500);

function getValues() {
    fetchWithTimeout('/settings/values', {
        timeout: 3000
    })
        .then(response => response.json())
        .then(response => {
            setTagValue('ip', response.ip);
            setTagValue('tag-net-id', response.netId);

            const slider = document.getElementById('slider');
            slider.value = response.brightness;

            document.title = `${documentTitle} ${response.netId}`;
        })
        .catch(() => setTimeout(getValues, 3000));
}