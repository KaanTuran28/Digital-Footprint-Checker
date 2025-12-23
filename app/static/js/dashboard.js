document.addEventListener('DOMContentLoaded', function() {
    const scanButtons = document.querySelectorAll('.scan-button');
    const loader = document.getElementById('loader');
    const newResultsContainer = document.getElementById('new-results-container');

    scanButtons.forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.dataset.platform;
            const usernameInput = document.getElementById(`${platform}-username`);
            const deepScanCheckbox = document.getElementById(`${platform}-deep-scan`);
            
            const username = usernameInput.value;
            const deepScan = deepScanCheckbox ? deepScanCheckbox.checked : false;

            if (!username) {
                alert('Lütfen analiz için bir kullanıcı adı girin.');
                return;
            }

            const data = {};
            data[`${platform}_username`] = username;
            data['deep_scan'] = deepScan;

            const originalButtonText = this.innerHTML;
            this.disabled = true;
            
            // YENİ: Dinamik Yükleniyor Mesajı
            let dots = 0;
            const loadingInterval = setInterval(() => {
                dots = (dots + 1) % 4;
                const loadingText = 'Analiz Ediliyor' + '.'.repeat(dots);
                this.innerHTML = `<span aria-busy="true">${loadingText}</span>`;
            }, 500);
            
            if (newResultsContainer) newResultsContainer.innerHTML = '';
            // Loader'ı göster ve mesajını güncelle
            if (loader) {
                loader.style.display = 'block';
                loader.querySelector('small').textContent = deepScan ? 
                    "Derin tarama yapılıyor, bu işlem 30 saniye kadar sürebilir, lütfen bekleyin..." : 
                    "Profil taranıyor, lütfen bekleyin...";
            }

            fetch('/start-analysis', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderResults(data.results);
                } else {
                    // Hata mesajını daha şık göster
                    if (newResultsContainer) {
                        newResultsContainer.innerHTML = `
                            <article style="background-color: #ffe6e6; border-color: #ffcccc; color: #cc0000;">
                                <header>❌ Analiz Başarısız</header>
                                ${data.error}
                                <footer>Lütfen kullanıcı adını kontrol edip tekrar deneyin.</footer>
                            </article>
                        `;
                    }
                }
            })
            .catch(error => {
                console.error('Hata:', error);
                alert('Sunucuyla iletişim kurulamadı. Lütfen internet bağlantınızı kontrol edin.');
            })
            .finally(() => {
                // Yükleme animasyonunu durdur
                clearInterval(loadingInterval);
                if (loader) loader.style.display = 'none';
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
                    // Anahtarları daha okunaklı hale getir (LOCATION_HOLIDAY -> Location Holiday)
                    const readableKey = key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                    detailsHtml += `<li><strong>${readableKey}:</strong> ${value}</li>`;
                }
                detailsHtml += '</ul>';
            }

            const platformName = result.platform.charAt(0).toUpperCase() + result.platform.slice(1);

            html += `
            <article>
                <details open>
                    <summary>
                        <b>${platformName}:</b> ${result.username} - 
                        <span class="risk-${result.level}">${result.level} Risk (${result.score}/100)</span>
                    </summary>
                    <div style="margin-top: 1rem;">
                        ${detailsHtml}
                    </div>
                </details>
            </article>`;
        });

        if (newResultsContainer) {
            newResultsContainer.innerHTML = html;
            newResultsContainer.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Silme işlemi (Aynı kalıyor)
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-analysis-btn')) {
            const button = event.target;
            const analysisId = button.dataset.analysisId;

            if (confirm('Bu analizi silmek istediğinizden emin misiniz?')) {
                fetch(`/analysis/delete/${analysisId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        button.closest('.past-analysis-card').remove();
                        // Eğer liste boşaldıysa "Henüz analiz yok" mesajını geri getir
                        const list = document.getElementById('past-analyses-list');
                        if (list && list.children.length === 0) {
                             list.innerHTML = `
                                <div style="text-align: center; padding: 2rem; border: 1px dashed var(--muted-border-color); border-radius: var(--border-radius);">
                                    <p><strong>Henüz bir analiz yapmadınız.</strong></p>
                                    <small>Not: Sunucu kapanınca bu liste sıfırlanır.</small>
                                </div>`;
                        }
                    } else {
                        alert('Hata: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Silme hatası:', error);
                });
            }
        }
    });
});