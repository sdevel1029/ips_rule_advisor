document.addEventListener('pastCveListLoaded', (event) => {
    const { pastCveList, pastTestList } = event.detail;  

    // 정보 수집 목록 처리
    const infoSelection = document.getElementById('info_selection');
    pastCveList.forEach(cve => {
      const option = document.createElement('option');
      option.value = cve.cve;
      option.text = cve.cve;
      infoSelection.appendChild(option);
    });

    // 테스트 결과 목록 처리
    const testSelection = document.getElementById('test_results');
    pastTestList.forEach(test => {
      const option = document.createElement('option');
      option.value = test.cve;
      option.text = test.cve;
      testSelection.appendChild(option);
    });
});