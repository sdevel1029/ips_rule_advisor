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

    const pocElements = document.querySelectorAll('#flush-poc_list a'); 
    const pocLinks = Array.from(pocElements).map(pocElement => {
        return { url: pocElement.href.trim() }; 
    });
    const pocData = pocLinks.length > 0 ? { pocs: pocLinks } : {};

    const refElements = document.querySelectorAll('.reference-row');
    const refDataArray = Array.from(refElements).map(row => {
        const urlElement = row.querySelector('.reference-url');
        const typeElement = row.querySelector('.reference-type');
        const url = urlElement ? urlElement.href.trim() : '정보 없음';
        const type = typeElement ? typeElement.innerText.trim() : '정보 없음';
        return { url: url, type: type };
    });
    const referenceData = refDataArray.length > 0 ? { references: refDataArray } : {};

    const postingDateElement = document.getElementById('posting-date');
    const lastModifiedDateElement = document.getElementById('last-modified-date');

    const postingDateText = postingDateElement.textContent.trim();
    const lastModifiedDateText = lastModifiedDateElement.textContent.trim();

    // Snort Community Rule 데이터를 객체 배열로 변환하여 저장
    const snortRuleElements = document.querySelectorAll('#flush-snortRules .list-group-item');
    const snortDataArray = Array.from(snortRuleElements).map(ruleElement => {
        return {Rule: ruleElement.innerText.trim() }; 
    });
    const snortData = snortDataArray.length > 0 ? { snortCommunityRules: snortDataArray } : {};

    // Emerging Rule 데이터를 객체 배열로 변환하여 저장
    const emergingRuleElements = document.querySelectorAll('#flush-emergingRule .list-group-item');
    const emergingDataArray = Array.from(emergingRuleElements).map(ruleElement => {
        return { Rule: ruleElement.innerText.trim() }; 
    });
    const emergingData = emergingDataArray.length > 0 ? { emergingRules: emergingDataArray } : {};

    //메트릭 세부 관련 데이터 저장 함수
    function getNextActiveTd(thText) {
      const thElements = document.querySelectorAll('th');
      for (const th of thElements) {
          if (th.innerText.includes(thText)) {
              // th 다음에 나오는 모든 td를 찾음
              const tdElements = th.parentElement.querySelectorAll('td');
              for (const td of tdElements) {
                  // table-active 클래스가 있는지 확인
                  if (td.classList.contains('table-active')) {
                      return td.innerText.trim(); // 활성화된 td 태그 반환
                  }
              }
          }
      }
      return '정보 없음'; // 활성화된 td가 없으면 '정보 없음' 반환
    }
  

    //메트릭 세부와 관련된 데이터들

    // 각 메트릭 데이터를 가져옴 (활성화된 td 값을 찾아서 저장)
    const attackVector = getNextActiveTd('Attack Vector');
    const attackComplexity = getNextActiveTd('Attack Complexity');
    const privilegesRequired = getNextActiveTd('Privileges Required');
    const userInteraction = getNextActiveTd('User Interaction');
    const scope = getNextActiveTd('Scope');
    const confidentialityImpact = getNextActiveTd('Confidentiality Impact');
    const integrityImpact = getNextActiveTd('Integrity Impact');
    const availabilityImpact = getNextActiveTd('Availability Impact');

    const vulnerabilityData = {
      vuln_type: vulnType,
      description: description,
      cpe: cpeData,
      metric: metrics,
      score: score,
      influence_score: influenceScore,
      exploit_score: exploitScore,
      metrics_summary: metricsSummary,
      snort_community_rule: snortData,
      emerging_rule: emergingData,
      poc: pocData,
      reference: referenceData,
      cve: cveId,
      cve_posting_date: postingDateText,
      last_modified_date: lastModifiedDateText,

      // 메트릭세부 데이터 추가
      attack_vector: attackVector,
      attack_complexity: attackComplexity,
      privileges_required: privilegesRequired,
      user_interaction: userInteraction,
      scope: scope,
      confidentiality_impact: confidentialityImpact,
      integrity_impact: integrityImpact,
      availability_impact: availabilityImpact
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