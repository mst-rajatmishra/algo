function login() {
    const apiKey = document.getElementById('api-key').value;
    const apiSecret = document.getElementById('api-secret').value;
    const accessToken = document.getElementById('access-token').value;

    // Send login credentials to backend for validation
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            apiKey: apiKey,
            apiSecret: apiSecret,
            accessToken: accessToken
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('login-msg').textContent = 'Login successful.';
            document.getElementById('wishlist-container').style.display = 'block';
            // Load wishlist and stock management UI
        } else {
            document.getElementById('login-msg').textContent = 'Login failed. Please check your credentials.';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('login-msg').textContent = 'An error occurred. Please try again.';
    });
}
