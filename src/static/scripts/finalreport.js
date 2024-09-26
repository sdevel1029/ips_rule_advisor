document.addEventListener('pastCveListLoaded', (event) => {
    const pastCveList = event.detail;
    const infoSelection = document.getElementById('info_selection');
  
    pastCveList.forEach(cve => {
      const option = document.createElement('option');
      option.value = cve.cve;
      option.text = cve.cve;
      infoSelection.appendChild(option);
    });
  });