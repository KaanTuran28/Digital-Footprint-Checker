document.addEventListener('DOMContentLoaded', function() {
    // Gerekli elementleri seç
    const scanButtons = document.querySelectorAll('.scan-button');
    const loader = document.getElementById('loader');
    const newResultsContainer = document.getElementById('new-results-container');

    // Her bir "Tara" butonuna tıklama olayı ekle
    scanButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Data attribute'larından platform bilgisini al
            const platform = this.dataset.platform;
            
            // İlgili input ve checkbox elementlerini bul
            const usernameInput = document.getElementById(`${platform}-username`);
            const deepScanCheckbox = document.getElementById(`${platform}-deep-scan`);
            
            const username = usernameInput.value;
            const deepScan = deepScanCheckbox ? deepScanCheckbox.checked : false;

            // Kullanıcı adı boşsa uyarı ver
            if (!username) {
                alert('Lütfen analiz için bir kullanıcı adı girin.');
                return;
            }

            // Backend'e gidecek veriyi hazırla
            const data = {};
            data[`${platform}_username`] = username;
            data['deep_scan'] = deepScan;

            // Butonun durumunu "Taranıyor" yap
            const originalButtonText = this.innerHTML;
            this.disabled = true;
            this.innerHTML = '<span aria-busy="true">Taranıyor...</span>';
            
            // Önceki sonuçları temizle ve loader'ı göster
            if (newResultsContainer) newResultsContainer.innerHTML = '';
            if (loader) loader.style.display = 'block';

            // API İsteği Gönder
            fetch('/start-analysis', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                // Loader'ı gizle
                if (loader) loader.style.display = 'none';

                if (data.success) {
                    renderResults(data.results);
                } else {
                    alert('Hata: ' + data.error);
                }
            })
            .catch(error => {
                if (loader) loader.style.display = 'none';
                console.error('Hata:', error);
                alert('Sunucuyla iletişim kurulamadı.');
            })
            .finally(() => {
                // İşlem bitince butonu eski haline getir
                this.disabled = false;
                this.innerHTML = originalButtonText;
            });
        });
    });

    // Sonuçları HTML olarak oluşturup ekrana basan fonksiyon
    function renderResults(results) {
        let html = '<h2>Son Analiz Sonuçları</h2>';
        
        results.forEach(result => {
            let detailsHtml = '<p>Riskli bir bilgi bulunamadı.</p>';
            
            // Eğer detaylı veri varsa listeye çevir
            if (result.details && Object.keys(result.details).length > 0) {
                detailsHtml = '<ul>';
                for (const [key, value] of Object.entries(result.details)) {
                    detailsHtml += `<li><strong>${key.toUpperCase()}:</strong> ${value}</li>`;
                }
                detailsHtml += '</ul>';
            }

            // Platform baş harfini büyüt
            const platformName = result.platform.charAt(0).toUpperCase() + result.platform.slice(1);

            // HTML Kartını Oluştur (CSS sınıflarını kullanarak)
            html += `
            <article>
                <details open>
                    <summary>
                        <b>${platformName}:</b> ${result.username} - 
                        <span class="risk-${result.level}">${result.level} Risk (${result.score}/100)</span>
                    </summary>
                    ${detailsHtml}
                </details>
            </article>`;
        });

        if (newResultsContainer) {
            newResultsContainer.innerHTML = html;
            newResultsContainer.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Silme işlemi için Event Delegation (Geçmiş analizler için)
    document.body.addEventListener('click', function(event) {
        // Tıklanan element silme butonu mu?
        if (event.target.classList.contains('delete-analysis-btn')) {
            const button = event.target;
            const analysisId = button.dataset.analysisId;

            if (confirm('Bu analiz kaydını kalıcı olarak silmek istediğinizden emin misiniz?')) {
                fetch(`/analysis/delete/${analysisId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Başarılıysa kartı ekrandan kaldır
                        button.closest('.past-analysis-card').remove();
                    } else {
                        alert('Hata: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Silme hatası:', error);
                    alert('Bir hata oluştu, silme işlemi gerçekleştirilemedi.');
                });
            }
        }
    });
});