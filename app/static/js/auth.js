document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================
    // 1. ŞİFRE GÖSTER/GİZLE (Tüm Sayfalar İçin)
    // ==========================================
    const togglePasswordIcons = document.querySelectorAll('.toggle-password');

    togglePasswordIcons.forEach(icon => {
        icon.addEventListener('click', function() {
            // İkonun bulunduğu satırdaki inputu bul
            const passwordField = this.previousElementSibling;
            
            // Tipini değiştir (text <-> password)
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            
            // İkonu değiştir
            this.textContent = type === 'password' ? '👁️' : '🙈';
        });
    });

    // ==========================================
    // 2. ŞİFRE GÜVENLİK KURALLARI (Sadece Kayıt)
    // ==========================================
    const passwordInput = document.getElementById('password');
    const passwordRules = document.getElementById('password-rules');

    // Eğer sayfada şifre kuralları listesi varsa (yani Register sayfasıysa) çalışır
    if (passwordInput && passwordRules) {
        const rules = {
            'length': document.getElementById('rule-length'),
            'uppercase': document.getElementById('rule-uppercase'),
            'lowercase': document.getElementById('rule-lowercase'),
            'number': document.getElementById('rule-number')
        };

        passwordInput.addEventListener('input', function() {
            const pass = this.value;

            // Kural 1: En az 8 karakter
            rules.length.classList.toggle('valid', pass.length >= 8);
            
            // Kural 2: Büyük Harf
            rules.uppercase.classList.toggle('valid', /[A-Z]/.test(pass));
            
            // Kural 3: Küçük Harf
            rules.lowercase.classList.toggle('valid', /[a-z]/.test(pass));
            
            // Kural 4: Rakam
            rules.number.classList.toggle('valid', /[0-9]/.test(pass));
        });
    }

    // ==========================================
    // 3. ŞİFRE EŞLEŞME KONTROLÜ (Sadece Kayıt)
    // ==========================================
    const confirmPasswordInput = document.getElementById('password2');

    if (passwordInput && confirmPasswordInput) {
        function checkMatch() {
            const pass1 = passwordInput.value;
            const pass2 = confirmPasswordInput.value;

            // İkinci kutu boşsa renk verme
            if (pass2 === '') {
                confirmPasswordInput.style.borderColor = '';
                confirmPasswordInput.style.boxShadow = 'none';
            } 
            // Eşleşiyorsa Yeşil Çerçeve
            else if (pass1 === pass2) {
                confirmPasswordInput.style.borderColor = '#388e3c';
                confirmPasswordInput.style.boxShadow = '0 0 0 2px rgba(56, 142, 60, 0.2)';
            } 
            // Eşleşmiyorsa Kırmızı Çerçeve
            else {
                confirmPasswordInput.style.borderColor = '#d32f2f';
                confirmPasswordInput.style.boxShadow = '0 0 0 2px rgba(211, 47, 47, 0.2)';
            }
        }

        // Her iki kutuya da yazıldığında kontrol et
        passwordInput.addEventListener('input', checkMatch);
        confirmPasswordInput.addEventListener('input', checkMatch);
    }
});