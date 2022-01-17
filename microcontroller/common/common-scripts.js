async function fetchWithTimeout(resource, options) {
    const { timeout = 8000 } = options,
        controller = new AbortController(),
        id = setTimeout(() => controller.abort(), timeout),
        response = await fetch(resource, {
            ...options,
            signal: controller.signal,
        });

    clearTimeout(id);

    return response;
}

function debounce(fn, wait = 100) {
    let timeout;

    return function (...args) {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            fn.apply(this, args);
        }, wait);
    };
}

function setTagValue(tagId, value) {
    const tag = document.getElementById(tagId);
    tag.tagName == 'INPUT'
        ? tag.type == 'checkbox'
            ? (tag.checked = parseInt(value))
            : (tag.value = value)
        : (tag.textContent = value);
}
