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

            setTagValue('switch', response.state == 'ON' ? 1 : 0);

            if (response.timer !== '0') {
                displayTimerMessage(response.timer);
            }

            document.title = `${documentTitle}-${response.netId}`;
            document
                .getElementById('app-spinner')
                .classList.add('display-none');
            document.getElementById('app').classList.remove('display-none');
        })
        .catch(() => setTimeout(getValues, 3000));
}

function updateTimerValue(value) {
    setTagValue('slider-value', value);
}

function setSliderTimer() {
    const sliderValue = document.getElementById('slider-value');
    setTimer(parseInt(sliderValue.textContent));
}

function setManualTimer() {
    const manualTimer = document.getElementById('manual-timer');
    setTimer(parseInt(manualTimer.value));
}

function setTimer(value) {
    fetch(`/action/timer?minutes=${value}`)
        .then((response) => response.json())
        .then((response) => {
            displayTimerMessage(response.timer);
        });
}

function toggle() {
    const action = document.getElementById('switch').checked ? 'on' : 'off';

    fetchWithTimeout(`/action/toggle?action=${action}`, {
        timeout: 3000,
    })
        .then(() => {
            if (action == 'off') {
                hideTimerMessage();
            }
        })
        .catch(() => setTimeout(() => toggle(), 3000));
}

function displayTimerMessage(timer) {
    setTagValue('switch-off-timer', timer);
    setTagValue('switch', 1);

    document
        .getElementById('switch-off-block-timer')
        .classList.remove('visibility-hidden');
}

function hideTimerMessage() {
    document
        .getElementById('switch-off-block-timer')
        .classList.add('visibility-hidden');
}
