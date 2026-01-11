# Stock Insight AI

AI 기반 실시간 주식 분석 및 투자 조언 플랫폼

## 로컬 개발 환경 설정

### 1. Python 가상환경 생성 (선택사항, 권장)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 서버 실행

#### 방법 1: uvicorn 직접 실행 (권장)
```bash
uvicorn main:app --reload
```

#### 방법 2: Python 스크립트 실행
```bash
python main.py
```

### 4. 브라우저에서 접속

서버 실행 후 다음 URL로 접속:
- **http://localhost:8000**

`--reload` 옵션을 사용하면 코드 변경 시 자동으로 서버가 재시작됩니다.

## 주요 기능

- 📊 실시간 글로벌 지수 (S&P 500, NASDAQ, Dow Jones, KOSPI, KOSDAQ)
- 📈 인터랙티브 주식 차트 (Plotly)
- 📰 뉴스 감성 분석
- 🤖 AI 기반 투자 조언
- 🇺🇸🇰🇷 미국/한국 인기 주식 빠른 검색

## 프로젝트 구조

```
├── main.py              # FastAPI 애플리케이션
├── utils.py             # 유틸리티 함수 (주식 데이터, 감성 분석 등)
├── templates/           # Jinja2 HTML 템플릿
│   ├── base.html       # 기본 레이아웃
│   └── index.html      # 메인 페이지
├── static/             # 정적 파일
│   ├── styles.css      # CSS 스타일
│   ├── robots.txt      # 검색엔진 설정
│   └── sitemap.xml     # 사이트맵
├── requirements.txt    # Python 패키지 의존성
└── Procfile           # 배포 설정
```

## 배포

### Heroku
```bash
git push heroku master
```

### 기타 플랫폼
- Railway, Render, AWS 등에서도 동일하게 작동합니다.

## 기술 스택

- **Backend**: FastAPI
- **Frontend**: Jinja2 Templates, HTML/CSS/JavaScript
- **Data**: yfinance, pandas
- **Visualization**: Plotly
- **Sentiment Analysis**: VADER
- **Translation**: deep-translator

