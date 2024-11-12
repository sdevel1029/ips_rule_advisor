# windows : 
`python -m venv venv`

`Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`

`.\venv\Scripts\activate`

`pip install -r requirements.txt`

`uvicorn src.main:app --reload`

# ubuntu :
가상환경 생성
`python3 -m venv venv` 

가상환경 경로
`source venv/bin/activate`

모듈 설치
`pip install -r requirements.txt`

서버 실행
`uvicorn src.main:app --reload`

