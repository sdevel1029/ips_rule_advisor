document.getElementById('feedbackForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // 기본 폼 제출 방지

    const feedback = document.getElementById('userFeedback').value;

    // 의견이 입력되었는지 확인
    if (!feedback) {
        alert("의견을 입력하세요.");
        return;
    }

    try {
        // 서버로 의견 전송
        const response = await fetch('/comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                comment: feedback 
            })
        });

        if (!response.ok) {
            throw new Error("서버 오류: 의견을 전송할 수 없습니다.");
        }

        const result = await response.json();
        console.log("의견이 성공적으로 추가되었습니다:", result);

        // 입력 필드 초기화
        document.getElementById('userFeedback').value = '';

        // 성공 메시지 표시 또는 의견 목록 다시 불러오기
        alert("의견이 성공적으로 추가되었습니다!");
    } catch (error) {
        console.error("의견 제출 중 오류가 발생했습니다:", error);
        alert("의견을 제출하는 동안 오류가 발생했습니다.");
    }
});