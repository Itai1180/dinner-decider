async function apiPost(path, body) {
    const response = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(body || {})
    });
    return response.json();
}

async function apiGet(path) {
    const response = await fetch(path, {
        credentials: 'same-origin'
    });
    return response.json();
}
