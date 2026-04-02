# 내비게이션 개편 계획

## 배경
`/tools` 허브처럼 관련 기능을 한 페이지로 묶는 방식을 분석/포트폴리오 영역에도 적용.
현재 12개인 내비게이션 항목을 9개로 줄여 UX 개선.

---

## 3번: 시장 분석 허브 (`/market-analysis`)

### 통합 대상 (현재 개별 내비 항목 4개)
| 현재 URL | 페이지명 |
|----------|---------|
| `/fear-greed-index` | 😨 공포/탐욕 지수 |
| `/sector-analysis` | 🏗️ 섹터 분석 |
| `/sentiment-analysis` | 📢 소셜 센티먼트 |
| `/economic-indicators` | 📈 경제지표 |

### 작업 목록
1. `templates/market_analysis.html` 신규 생성 (`tools.html` 구조 참고)
2. `main.py`에 `GET /market-analysis` 라우트 추가
3. `templates/base.html` 내비 수정
   - 4개 개별 항목 → `🔬 시장 분석` 단일 항목으로 교체
   - active 조건에 하위 URL 4개 포함
4. 4개 분석 페이지 상단에 브레드크럼 추가
   - `🔬 시장 분석 › [페이지명]`

### 내비 변경 전/후
```
전: 😨 공포/탐욕  🏗️ 섹터분석  📢 소셜센티먼트  📈 경제지표  (4개)
후: 🔬 시장 분석  (1개, 클릭하면 허브 페이지)
```

---

## 4번: 포트폴리오 허브 (`/portfolio`)

### 통합 대상 (현재 개별 내비 항목 2개)
| 현재 URL | 페이지명 |
|----------|---------|
| `/compare` | ⚖️ 종목비교 |
| `/portfolio-simulator` | 💼 포트폴리오 시뮬레이터 |

### 작업 목록
1. `templates/portfolio_hub.html` 신규 생성
2. `main.py`에 `GET /portfolio` 라우트 추가
3. `templates/base.html` 내비 수정
   - 2개 개별 항목 → `💼 포트폴리오` 단일 항목으로 교체
   - active 조건에 `/compare`, `/portfolio-simulator` 포함
4. 두 페이지 상단에 브레드크럼 추가
   - `💼 포트폴리오 › [페이지명]`

### 내비 변경 전/후
```
전: ⚖️ 종목비교  💼 포트폴리오 시뮬레이터  (2개)
후: 💼 포트폴리오  (1개, 클릭하면 허브 페이지)
```

---

## 최종 내비게이션 (12개 → 9개)

| # | 항목 | URL |
|---|------|-----|
| 1 | 📊 대시보드 | `/` |
| 2 | 🔍 종목 발굴 | `/stock-discovery` |
| 3 | 📋 일일리포트 | `/daily-report` |
| 4 | 🛠️ 도구/분석 | `/tools` |
| 5 | 🔬 시장 분석 *(신규 허브)* | `/market-analysis` |
| 6 | 🔭 ETF 탐험가 | `/etf-explorer` |
| 7 | 💼 포트폴리오 *(신규 허브)* | `/portfolio` |
| 8 | 📝 블로그 | `/blog` |

> ETF 탐험가는 성격상 단독 항목 유지가 적절.
