function ping() {
    fetch('/api/v1/health')
        .then(res => res.json())
        .then(data => {
            document.getElementById('result').textContent =
                JSON.stringify(data, null, 2);
        });
}
