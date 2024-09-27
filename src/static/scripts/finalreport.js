document.addEventListener("DOMContentLoaded", async () => {
  const infoSelection = document.getElementById('info_selection');
  const testResults = document.getElementById('test_results');
  const reportForm = document.getElementById("reportForm");

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

  // 폼 제출 시 보고서 요청
  reportForm.addEventListener("submit", async function (event) {
    event.preventDefault();  // 기본 폼 제출 동작을 방지

    const selectedInfoId = infoSelection.value;
    const selectedTestId = testResults.value;

    if (!selectedInfoId || !selectedTestId) {
      alert("정보 수집 결과와 테스트 결과를 선택해주세요.");
      return;
    }

    try {
      // 서버로 GET 요청 보내기
      const response = await fetch(`/finalshow?infoid=${selectedInfoId}&testid=${selectedTestId}`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error("Failed to generate report");
      }

      const reportContent = await response.text();

      // 보고서 내용 출력 (예: 별도의 div에 출력)
      displayReport(reportContent);

    } catch (error) {
      console.error("Error generating report:", error);
      alert("보고서 생성 중 오류가 발생했습니다.");
    }
  });

  // 보고서 내용을 화면에 표시하는 함수
  function displayReport(reportContent) {
    const reportSection = document.createElement("div");
    reportSection.innerHTML = reportContent;
    document.body.appendChild(reportSection);  // 원하는 위치에 추가 가능
  }
});
