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
});
