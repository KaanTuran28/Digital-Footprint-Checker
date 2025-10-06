async function registerUser() {
  const username = document.getElementById('regUsername').value;
  const password = document.getElementById('regPassword').value;

  const res = await fetch('http://127.0.0.1:5000/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password})
  });

  const data = await res.json();
  alert(data.message || data.error);
}

async function loginUser() {
  const username = document.getElementById('loginUsername').value;
  const password = document.getElementById('loginPassword').value;

  const res = await fetch('http://127.0.0.1:5000/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password})
  });

  const data = await res.json();
  if (res.ok) {
    // Başarılı giriş → dashboard.html sayfasına yönlendir
    window.location.href = "dashboard.html";
  } else {
    alert(data.error);
  }
}
