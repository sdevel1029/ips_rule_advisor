document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('cve-form').addEventListener('submit', async function(event) {
      event.preventDefault();

      const cveCode = document.getElementById('cve_code').value;

      try {
          const response = await fetch('/getinfo', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'  // JSON 요청
              },
              body: JSON.stringify({ cve_code: cveCode })  // JSON 형식으로 데이터 전송
          });

          if (!response.ok) {
              throw new Error('서버 오류: ' + response.statusText);
          }

          const result = await response.json();
          console.log(result);

          // 결과 페이지로 이동 코드 또는 데이터 처리
          window.location.href = `getinfo_result.html?cve_code=${encodeURIComponent(result.cve_code)}&info=${encodeURIComponent(result.info)}`;
      } catch (error) {
          console.error('문제 발생:', error);
      }
  });
});
