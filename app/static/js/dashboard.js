document.addEventListener('DOMContentLoaded', function() {
    const scanButtons = document.querySelectorAll('.scan-button');
    const loader = document.getElementById('loader');
    const newResultsContainer = document.getElementById('new-results-container');

    scanButtons.forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.dataset.platform;
            const usernameInput = document.getElementById(`${platform}-username`);
            const username = usernameInput.value;
            const deepScanCheckbox = document.getElementById(`${platform}-deep-scan`);
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
            this.innerHTML = '<span aria-busy="true">Taranıyor...</span>';
            newResultsContainer.innerHTML = '';

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
                    alert('Hata: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Hata:', error);
                alert('Sunucuyla iletişim kurulamadı.');
            })
            .finally(() => {
                this.disabled = false;
                this.innerHTML = originalButtonText;
            });
        });
    });

    function renderResults(results) {
        let html = '<h2>Son Analiz Sonuçları</h2>';
        results.forEach(result => {
            let detailsHtml = '<p>Riskli bir bilgi bulunamadı.</p>';
            if (result.details && Object.keys(result.details).length > 0) {
                detailsHtml = '<ul>';
                for (const [key, value] of Object.entries(result.details)) {
                    detailsHtml += `<li><strong>${key.toUpperCase()}:</strong> ${value}</li>`;
                }
                detailsHtml += '</ul>';
            }
            html += `<article><details open><summary><b>${result.platform.charAt(0).toUpperCase() + result.platform.slice(1)}:</b> ${result.username} - <span><b>${result.level} Risk (${result.score}/100)</b></span></summary>${detailsHtml}</details></article>`;
        });
        newResultsContainer.innerHTML = html;
        newResultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    document.body.addEventListener('click', function(event) {
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
