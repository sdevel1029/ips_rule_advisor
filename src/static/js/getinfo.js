document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('cve-form').addEventListener('submit', async function(event) {
      event.preventDefault();  
  
      const cveCode = document.getElementById('cve_code').value;
      try {
        const response = await fetch('/getinfo', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ cve_code: cveCode })
        });
  
        if (!response.ok) {
          throw new Error('서버 오류: ' + response.statusText);
        }
  
        const result = await response.json();
        console.log(result);  

      } catch (error) {
        console.error('문제 발생:', error);

      }
    });
  });
  