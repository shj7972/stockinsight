# 배포 가이드

## 옵션 1: Streamlit Cloud (추천 - 가장 간단)

### 단계:
1. GitHub에 코드 푸시
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. Streamlit Cloud 접속
   - https://streamlit.io/cloud 접속
   - GitHub 계정으로 로그인
   - "New app" 클릭
   - 저장소 선택
   - Main file path: `app.py`
   - Deploy!

## 옵션 2: Heroku 배포

### 사전 준비:
1. Heroku CLI 설치 확인
2. Heroku 계정 생성

### 배포 명령:
```bash
# Heroku 로그인
heroku login

# Heroku 앱 생성
heroku create stock-insight-app

# 배포
git init
git add .
git commit -m "Initial commit"
git push heroku main

# 또는 이미 Git 저장소가 있다면
git push heroku main
```

### 환경 변수 설정 (필요시):
```bash
heroku config:set VARIABLE_NAME=value
```

## 옵션 3: Railway 배포

1. https://railway.app 접속
2. GitHub 저장소 연결
3. 자동 배포

## 옵션 4: Render 배포

1. https://render.com 접속
2. New Web Service
3. GitHub 저장소 연결
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `streamlit run app.py --server.port $PORT`

## 배포 후 확인사항

- [ ] https://stock-insight.app/robots.txt 접근 가능 확인
- [ ] 네이버 서치어드바이저에 사이트 등록
- [ ] 도메인 연결 (stock-insight.app)
- [ ] HTTPS 설정 확인

