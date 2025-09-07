const form = document.getElementById('form');
const result = document.getElementById('result');

form.addEventListener('submit', async function(e) {
  e.preventDefault();
  result.innerHTML = 'שולח...';

  const formData = new FormData(form);
  const response = await fetch('/generate-link', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  if (data.link) {
    result.innerHTML = `<a href="${data.link}" target="_blank">מעבר לאתר miluimnik</a>`;
    document.getElementById('counter').innerText = ` מספר הקישורים שנוצרו עד כה: ${data.counter}`;    
  } else if (data.error) {
    result.innerHTML = `<p style="color:red;">שגיאה: ${data.error}</p>`;
  } else {
    result.innerHTML = `<p style="color:red;">שגיאה כללית: לא התקבל קישור</p>`;
  }
});