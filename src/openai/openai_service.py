import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# 환경변수를 불러오기
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def load_attack_types(filename):
    # 현재 스크립트 파일의 디렉토리 경로 가져오기
    script_dir = os.path.dirname(os.path.abspath(__file__)) 

    # JSON 파일 경로 생성 (openai_service.py 파일과 같은 디렉토리에 있다고 가정)
    file_path = os.path.join(script_dir, filename)

    with open(file_path, 'r') as file:
        return json.load(file)

def classify_attack(description, attack_types):
    # 공격 유형 셋을 문자열로 변환
    attack_types_str = "\n".join([f"{key}: {value}" for key, value in attack_types.items()])
    
    # GPT API 요청
    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for classifying types of security attacks."
            },
            {
                "role": "user",
                "content": f"다음 설명을 읽고, 공격 유형 셋 중 어느 것에 해당하는지 선택해 주세요:\n\n설명: {description}\n\n{attack_types_str}\n\n위 공격 유형 중 설명에 가장 잘 맞는 것을 선택해 주세요."
            }
        ],
        max_tokens=200,
        temperature=0.2
    )
    
    # 응답에서 메시지 내용 가져오기
    return response.choices[0].message.content.strip()

def generate_text():
   pass

def main():
    # 공격 유형 셋 로드
    attack_types = load_attack_types('attack_types.json')
    
    # 설명 예제
    description = "A method used to execute arbitrary SQL code on a database."
    
    # 공격 유형 분류
    result = classify_attack(description, attack_types)
    print(f"Classification result: {result}")

if __name__ == "__main__":
    main()
