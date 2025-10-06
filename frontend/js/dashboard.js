let chart;

async function uploadCSV() {
  const fileInput = document.getElementById('csvFile');
  if (!fileInput.files.length) {
    alert("Lütfen bir CSV dosyası seçin");
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const response = await fetch('http://127.0.0.1:5000/upload_csv', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const data = await response.json();
    displayDashboard(data.reports);
  } catch (err) {
    console.error(err);
    alert("CSV yüklenirken hata oluştu: " + err.message);
  }
}

function displayDashboard(reports) {
  const riskCounts = { Low:0, Medium:0, High:0 };
  reports.forEach(r => { riskCounts[r.risk_level] += 1; });

  const ctx = document.getElementById('riskChart').getContext('2d');
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Low', 'Medium', 'High'],
      datasets: [{
        label: 'Risk Dağılımı',
        data: [riskCounts.Low, riskCounts.Medium, riskCounts.High],
        backgroundColor: ['#4caf50','#ff9800','#f44336']
      }]
    }
  });

  const table = document.getElementById('highRiskTable');
  table.querySelectorAll("tr:not(:first-child)").forEach(tr => tr.remove());
  const sorted = reports.sort((a,b) => b.risk_score - a.risk_score).slice(0,5);
  sorted.forEach(r => {
    const row = table.insertRow();
    row.insertCell(0).textContent = r.name;
    row.insertCell(1).textContent = r.role;
    row.insertCell(2).textContent = r.risk_score;
    row.insertCell(3).textContent = r.risk_level;
  });
}
