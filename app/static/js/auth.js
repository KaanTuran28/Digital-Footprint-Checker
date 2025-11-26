document.addEventListener('DOMContentLoaded', function() {
    const togglePasswordIcons = document.querySelectorAll('.toggle-password');
    togglePasswordIcons.forEach(icon => {
        icon.addEventListener('click', function() {
            const passwordField = this.previousElementSibling;
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            this.textContent = type === 'password' ? '👁️' : '🙈';
        });
    });

    const passwordInput = document.getElementById('password');
    const passwordRules = document.getElementById('password-rules');
    if (passwordInput && passwordRules) {
        const rules = {
            'length': document.getElementById('rule-length'),
            'uppercase': document.getElementById('rule-uppercase'),
            'lowercase': document.getElementById('rule-lowercase'),
            'number': document.getElementById('rule-number')
        };
        passwordInput.addEventListener('input', function() {
            const pass = this.value;
            rules.length.classList.toggle('valid', pass.length >= 8);
            rules.uppercase.classList.toggle('valid', /[A-Z]/.test(pass));
            rules.lowercase.classList.toggle('valid', /[a-z]/.test(pass));
            rules.number.classList.toggle('valid', /[0-9]/.test(pass));
        });
    }
});