#src/openai/openai_service.py
import json
import os
from dotenv import load_dotenv
import httpx

# 환경변수를 불러오기
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def load_attack_types(filename: str):
    # 현재 스크립트 파일의 디렉토리 경로 가져오기
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # JSON 파일 경로 생성
    file_path = os.path.join(script_dir, filename)

    with open(file_path, 'r') as file:
        return json.load(file)

async def classify_attack(description: str) -> str:
    # 공격 유형을 JSON 파일에서 로드
    attack_types = load_attack_types("attack_types.json")
    
    # 공격 유형 셋을 문자열로 변환
    attack_types_str = "\n".join([f"{key}: {value}" for key, value in attack_types.items()])

    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {"role": "system", "content": "You are a helpful assistant for classifying types of security attacks."},
                    {"role": "user", "content": f"다음 설명을 읽고, 공격 유형 셋 중 어느 것에 해당하는지 선택해 주세요:\n\n설명: {description}\n\n{attack_types_str}\n\n위 공격 유형 중 설명에 가장 잘 맞는 것을 선택해 주세요."}
                ],
                'max_tokens': 200,
                'temperature': 0.2
            }
        )
        response_data = response.json()
        return response_data['choices'][0]['message']['content'].strip()
    
async def translate_to_korean(text: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {"role": "system", "content": "You are a helpful assistant for translating English to Korean."},
                    {"role": "user", "content": f"Translate the following English text to Korean:\n\n{text}"}
                ],
                'max_tokens': 200,
                'temperature': 0.3
            }
        )
        response_data = response.json()
        return response_data['choices'][0]['message']['content'].strip()

async def chat_with_gpt(chat_message: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": chat_message}
                ],
                'max_tokens': 300,
                'temperature': 0.3
            }
        )
        response_data = response.json()
        reply = response_data['choices'][0]['message']['content'].strip()
        return {"reply": reply}


async def summarize_vector(vector:str)->str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
             'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {"role": "system", "content": "You are a helpful assistant that explains CVSS vectors in Korean."},
                    {"role": "user", "content": f"다음 CVSS 벡터를 한글로 요약해줘:\n\n{vector}"}
                ],
                'max_tokens': 200,
                'temperature': 0.3
            }
        )
        response_data = response.json()
        return response_data['choices'][0]['message']['content'].strip()



def generate_text():
    pass
async def main():
    # 공격 유형 셋 로드
    attack_types = load_attack_types('attack_types.json')

    # 설명 예제
    description = "A method used to execute arbitrary SQL code on a database."

    # 공격 유형 분류
    result = await classify_attack(description, attack_types)
    print(f"Classification result: {result}")


async def test_translate_to_korean():
    # 번역할 영어 문구
    text = "This is a test to translate from English to Korean."
    
    # 번역 함수 호출
    translated_text = await translate_to_korean(text)
    
    # 결과 출력
    print(f"Original text: {text}")
    print(f"Translated text: {translated_text}")
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    asyncio.run(test_translate_to_korean())
