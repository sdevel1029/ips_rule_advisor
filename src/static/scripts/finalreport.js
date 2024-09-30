document.addEventListener("DOMContentLoaded", async () => {
  const infoSelection = document.getElementById('info_selection');
  const testResults = document.getElementById('test_results');

  try {
    const response = await fetch('/past_info');
    const data = await response.json();

    const pastInfoList = data.past_info_list;
    const pastTestList = data.past_test_list;

    console.log(pastInfoList, pastTestList);

    // 정보 수집 목록 옵션 추가
    if (Array.isArray(pastInfoList)) {
      pastInfoList.forEach(info => {
        const option = document.createElement('option');
        option.value = info.id;  // 고유 ID를 value로 설정
        option.textContent = info.cve;  // 표시할 텍스트
        infoSelection.appendChild(option);
      });
    }

    // 테스트 결과 목록 옵션 추가
    if (Array.isArray(pastTestList)) {
      pastTestList.forEach(test => {
        const option = document.createElement('option');
        option.value = test.id;  // 고유 ID를 value로 설정
        option.textContent = test.cve;  // 표시할 텍스트
        testResults.appendChild(option);
      });
    }
  } catch (error) {
    console.error("Error fetching past data:", error);
  }

  const form = document.getElementById('reportForm');
  const spinnerContainer = document.querySelector('.spinner-container');
  const section = document.querySelector('.section');

  form.addEventListener('submit', function(event) {
      event.preventDefault(); // 기본 폼 제출 막기

      // 섹션 영역 숨기기 (옵션)
      section.style.display = "none";

      // 스피너와 메시지 표시
      spinnerContainer.classList.remove('d-none');

      // 실제 폼 제출을 지연하여 스피너 표시
      setTimeout(() => form.submit(), 100); // 시간 지연 후 폼 제출
  });
});

