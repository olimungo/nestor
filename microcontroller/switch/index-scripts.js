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
                    .getElementById(`title-timer-switch-a`)
                    .classList.remove('display-none');

                document
                    .getElementById(`title-custom-timer-switch-a`)
                    .classList.remove('display-none');

                document
                    .getElementById(`switch-container-b`)
                    .classList.remove('display-none');

                setTagValue('switch-b', states[1] == 'ON' ? 1 : 0);
            }

            const timers = response.timer.split(',');

            if (timers[0] !== '0') {
                displayTimerMessage('a', timers[0]);
            }

            if (timers[1] !== '0') {
                displayTimerMessage('b', timers[1]);
            }

            document.title = `${documentTitle}-${response.netId}`;
            document
                .getElementById('app-spinner')
                .classList.add('display-none');
            document.getElementById('app').classList.remove('display-none');
        })
        .catch(() => setTimeout(getValues, 3000));
}

function updateTimerValue(id, value) {
    setTagValue(`slider-value-${id}`, value);
}

function setSliderTimer(id) {
    const sliderValue = document.getElementById(`slider-value-${id}`);
    setTimer(id, parseInt(sliderValue.textContent));
}

function setManualTimer(id) {
    const manualTimer = document.getElementById(`manual-timer-${id}`);
    setTimer(id, parseInt(manualTimer.value));
}

function setTimer(id, value) {
    fetch(`/action/timer-${id}?minutes=${value}`)
        .then((response) => response.json())
        .then((response) => {
            displayTimerMessage(id, response.timer);
        });
}

function toggle(id) {
    const action = document.getElementById(`switch-${id}`).checked
        ? 'on'
        : 'off';

    fetchWithTimeout(`/action/toggle-${id}?action=${action}`, {
        timeout: 3000,
    })
        .then(() => {
            if (action == 'off') {
                hideTimerMessage(id);
            }
        })
        .catch(() => setTimeout(() => toggle(id), 3000));
}

function displayTimerMessage(id, timer) {
    setTagValue(`switch-off-timer-${id}`, timer);
    setTagValue(`switch-${id}`, 1);

    document
        .getElementById(`switch-off-block-timer-${id}`)
        .classList.remove('visibility-hidden');
}

function hideTimerMessage(id) {
    document
        .getElementById(`switch-off-block-timer-${id}`)
        .classList.add('visibility-hidden');
}
