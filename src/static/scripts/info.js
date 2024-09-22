async function saveInfo() {

    const cveId = document.getElementById('cve-id').innerText.trim();
    const vulnType = document.getElementById('vuln-type').innerText.replace('취약점 유형 : ', '').trim();
    const description = document.getElementById('description').innerText.trim();
    const score = document.getElementById('score').innerText.trim();
    const exploitScore = document.getElementById('exploit_score').innerText.trim();
    const influenceScore = document.getElementById('influence_score').innerText.trim();
    const metrics = document.getElementById('metrics').innerText.replace('메트릭 : ', '').trim();
    const metricsSummary = document.getElementById('metrics_summary').innerText.trim();

    let cpeList = [];
    let index = 1;
    let cpeElement = document.getElementById(`cpe-${index}`);

    while (cpeElement) {
      const cpeValue = cpeElement.innerText.trim();
      const includedValue = document.getElementById(`included-${index}`).innerText.trim();
      const excludedValue = document.getElementById(`excluded-${index}`).innerText.trim();

      cpeList.push({
        CPE: cpeValue,
        포함: includedValue,
        비포함: excludedValue
      });

      index++;
      cpeElement = document.getElementById(`cpe-${index}`);
    }

    // cpe 데이터를 딕셔너리로 변환
    const cpeData = { CPE_List: cpeList };

    const pocElements = document.querySelectorAll('.card-poc .table-row .table__cell.text-link');
    const pocLinks = Array.from(pocElements).map(pocElement => pocElement.href.trim());
    const pocData = pocLinks.length > 0 ? { urls: pocLinks } : {};

    const refElements = document.querySelectorAll('.reference-row');
    const refDataArray = Array.from(refElements).map(row => {
        const urlElement = row.querySelector('.reference-url');
        const typeElement = row.querySelector('.reference-type');
        const url = urlElement ? urlElement.href.trim() : '정보 없음';
        const type = typeElement ? typeElement.innerText.trim() : '정보 없음';
        return { url: url, type: type };
    });
    const referenceData = refDataArray.length > 0 ? { references: refDataArray } : {};
    console.log(referenceData)

    const postingDateElement = document.getElementById('posting-date');
    const lastModifiedDateElement = document.getElementById('last-modified-date');

    const postingDateText = postingDateElement.textContent.trim();
    const lastModifiedDateText = lastModifiedDateElement.textContent.trim();

    const vulnerabilityData = {
      vuln_type: vulnType,
      description: description,
      cpe: cpeData,
      metric: metrics,
      score: score,
      influence_score: influenceScore,
      exploit_score: exploitScore,
      metrics_summary: metricsSummary,
      related_rules_type: { "example": "data" },
      related_rules_product: { "example": "data" },
      poc: pocData,
      reference: referenceData,
      cve: cveId,
      cve_posting_date: postingDateText,
      last_modified_date: lastModifiedDateText
    };

    try {
      const response = await fetch("/saveinfo", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(vulnerabilityData)
      });

      if (response.ok) {
        const result = await response.json();
        alert("저장 성공: " + result.message);
      } else {
        const error = await response.text();  // 응답을 JSON으로 파싱하기 전에 텍스트로 출력
        alert("저장 실패: " + error);
      }
    } catch (error) {
      console.error("Error:", error);
      alert("저장 중 오류 발생");
    }
  }

  function redirectToRuleTestWithCVE(cveCode) {
    window.location.href = `/ruletest?cve=${encodeURIComponent(cveCode)}`;
  }