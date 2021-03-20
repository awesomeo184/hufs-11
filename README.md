# 종합설계 11조

## Quick-start

git clone 이후, 터미널에서 프로젝트로 이동 후
`pip install -r requirements.txt`를 입력해주세요. 프로젝트 의존 라이브러리를 자동으로 설치합니다.

만약 오류가 나면 cmake는 수동으로 설치하고 다시 명령어를 입력해주세요.

## 프로젝트 구조

```
hufs-11/
├── docs
├── resources (정적 파일)
        └── models (학습된 모델(*.h5))
├── src
    └── RabbitAndTurtle (메인 패키지, 각 파일의 용도는 파일 상단에 적어놨음)
            ├── __init__.py
            ├── controllers.py
            ├── images.py
            ├── models.py
            ├── statistics.py
            ├── user_settings.py
            └── views.py
├── tests
    └── __init__.py
├── README.md
├── requirements.txt (의존성)
└── setup.py (빌드 및 패키징 설정)
```