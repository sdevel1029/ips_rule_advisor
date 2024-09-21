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
