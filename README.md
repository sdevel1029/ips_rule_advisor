# 유의사항
localhost:8080/docs를 하시면 swagger에서 편하게 보실 수 있습니다.

# 주의사항
만약 clone 하셨을때 venv파일이 있으시면 삭제하시기 바랍니다.

# windows : 
`python -m venv venv`

`Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`

`.\venv\Scripts\activate`

`pip install -r requirements.txt`

`uvicorn src.main:app --reload`

# ubuntu :
가상환경 생성
`python -m venv venv` 

가상환경 경로
`source venv/bin/activate`

모듈 설치
`pip install -r requirements.txt`

서버 실행
`uvicorn src.main:app --reload`


# project_root
├── src
│   ├── auth
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   └── auth_service.py
│   ├── database
│   │   ├── __init__.py
│   │   └── supabase_client.py
│   ├── getinfo
│   │   ├── getinfo_routes.py
│   │   └── getinfo_service.py
│   ├── openai
│   │   ├── __init__.py
│   │   ├── openai_routes.py
│   │   └── openai_service.py
│   ├── root
│   │   └── root.py
│   ├── static
│   │   ├── css
│   │   │   └── getinfo.css
│   │   └── js
│   │       └── getinfo.js
│   ├── templates
│   │   └── getinfo.html
│   ├── __init__.py
│   ├── config.py
│   └── main.py
├── venv/
├── .gitignore
├── README.md
└── requirements.txt

