function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

const userCookie = getCookie('user');

if (userCookie) {
    const logoutButton = document.getElementById('logout-button');
    logoutButton.addEventListener('click', function () {
        fetch('/auth/sign_out', { method: 'GET' }) // 로그아웃 요청
            .then(response => {
                if (response.ok) {
                    // 로그아웃 성공 시 메인 페이지로 이동
                    window.location.href = '/';
                } else {
                    alert('로그아웃에 실패했습니다.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('로그아웃 중 문제가 발생했습니다.');
            });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('cve_code');
    const searchHistory = document.getElementById('search-history');
    const form = document.getElementById('cve-form');
    
    // 로컬 스토리지에서 검색 기록 가져오기
    function getSearchHistory() {
        return JSON.parse(localStorage.getItem('searchHistory')) || [];
    }

    // 검색 기록 저장하기
    function saveSearchHistory(keyword) {
        let history = getSearchHistory();
        // 중복 제거
        if (!history.includes(keyword)) {
            history.unshift(keyword); // 새로운 검색어를 맨 앞에 추가
            if (history.length > 10) history.pop(); // 최대 10개의 기록만 저장
            localStorage.setItem('searchHistory', JSON.stringify(history));
        }
    }

    // 검색 기록 표시하기
    function showSearchHistory() {
        let history = getSearchHistory();
        if (history.length > 0) {
            searchHistory.innerHTML = '';
            history.forEach(item => {
                let listItem = document.createElement('li');
                listItem.classList.add('list-group-item');
                listItem.style.display = 'flex'; // 아이콘과 텍스트가 나란히 보이도록 설정
                listItem.style.alignItems = 'center'; // 아이콘과 텍스트 수직 정렬

                // 시계 아이콘 추가
                let icon = document.createElement('i');
                icon.classList.add('bi', 'bi-clock', 'me-2'); // Bootstrap 아이콘 클래스 추가
                listItem.appendChild(icon);

                listItem.appendChild(document.createTextNode(item));
                listItem.style.cursor = 'pointer';
                listItem.addEventListener('click', function() {
                    searchInput.value = item;
                    searchHistory.style.display = 'none'; // 리스트 숨기기
                });
                searchHistory.appendChild(listItem);
            });
            updateSearchHistoryWidth(); // 너비 업데이트
            searchHistory.style.display = 'block';
        } else {
            searchHistory.style.display = 'none';
        }
    }

    // 검색 기록 너비를 검색창과 동일하게 설정
    function updateSearchHistoryWidth() {
        const searchInputWidth = searchInput.offsetWidth; // 검색창의 너비 가져오기
        searchHistory.style.width = searchInputWidth + 'px'; // 검색 기록 리스트의 너비 설정
    }

    // 검색창 클릭 시 검색 기록 표시
    searchInput.addEventListener('focus', function() {
        showSearchHistory();
    });

    // 검색창 입력 시 검색 기록 숨기기
    searchInput.addEventListener('input', function() {
        searchHistory.style.display = 'none';
    });

    // 검색 폼 제출 시 검색 기록 저장
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // 기본 제출 방지
        let keyword = searchInput.value.trim();
        if (keyword) {
            saveSearchHistory(keyword);
            form.submit(); // 폼 제출
        }
    });

    // 페이지 다른 곳 클릭 시 검색 기록 숨기기
    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target) && !searchHistory.contains(event.target)) {
            searchHistory.style.display = 'none';
        }
    });

    // 검색창의 크기 변경 감지하여 검색 기록 너비 업데이트
    window.addEventListener('resize', updateSearchHistoryWidth);

    // 검색 기록 클릭시 해당 검색 기록으로 인풋창 입력
    listItem.addEventListener('click', function() {
        searchInput.value = item;
        saveSearchHistory(item); // 클릭한 항목도 기록에 추가
        form.submit(); // 자동으로 폼 제출
        });
});

// 필터 옵션 클릭 시 hidden input 업데이트
document.querySelectorAll('input[name="filter_type_option"]').forEach(option => {
    option.addEventListener('change', function() {
        document.getElementById('filter_type').value = this.value;
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("cve-form");
    const spinnerContainer = document.querySelector(".spinner-container");
    const section = document.querySelector(".section");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // 기본 폼 제출 막기

        // 섹션 영역 숨기기
        section.style.display = "none";

        // 스피너와 메시지 표시
        spinnerContainer.classList.remove("d-none");

        // 서버로 데이터 전송 후 실제 폼 제출
        setTimeout(() => form.submit(), 100); // 시간 지연 후 폼 제출
    });
});