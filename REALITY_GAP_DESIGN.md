# Reality Gap Score — 구현 설계서 (v1)

**승인**: 2026-10-07 16:10 현종님 ("Reality Gap 우선 하시죠")
**대상**: stock-insight.app (stockinsight 디렉토리, FastAPI + GitHub Actions)
**목표**: 주가 모멘텀과 펀더멘털·산업 데이터의 괴리를 점수화해 저평가/과열 종목 발굴

---

## 1. 지표 정의 (v1)

Reality Gap Score = 정규화(주가 모멘텀) − 정규화(펀더멘털 모멘텀)

- **가격 모멘텀 (P)**: 20일 수익률 60%, 60일 수익률 40% — 섹터 내 Z-score 정규화
- **펀더멘털 모멘텀 (F)**:
  - 매출 YoY (최근 분기 vs 4분기 전) — 40%
  - 영업이익 YoY — 30% (음→양 전환 시 +보정)
  - Gross Margin 전분기 대비 변화 — 15%
  - FCF/순이익 트렌드 — 15%
- **Score**: −100 ~ +100
  - **+50 이상 (Positive Gap)**: 주가↓ + 펀더멘털↑ → **저평가 후보**
  - **−50 이하 (Negative Gap)**: 주가↑ + 펀더멘털↓ → **과열 경계**
  - ±20 이내: 일치(gap 없음), 노이즈 구간

**유니버스**: stock_discovery_manager의 US_UNIVERSE(42) + KR_UNIVERSE(26) 재사용

## 2. 데이터 소스 (전부 무료·이미 검증)

| 계층 | 소스 | 방식 | 실측 |
|---|---|---|---|
| 개별 펀더멘털 | yfinance info + quarterly_income_stmt | `revenueGrowth`, `earningsGrowth`, `grossMargins`, `FreeCashflow` + Total Revenue/Operating Income YoY | ✅ 종목당 ~0.9~1.8초 |
| 주가 | yhistory 70d | close.iloc[-1]/[-21]/[-61] | ✅ 0.5초 |
| 섹터 산업 | 기존 `utils.get_sector_performance()` 11 ETF RS | 내부 재사용 | ✅ 이미 사이트에 있음 |
| 거시 산업 | FRED INDPRO/DGORDER (CSV 이미 있음) | `update_economic_indicators.py` 확장 | ✅ GHA 돌고 있음 |

**국내 종목 보강(v2)**: DART API(공시) 연동 검토 — 1차는 yfinance로 충분
**US 규제 리스크**: JOBY처럼 초기 기업은 YoY 왜곡 큼 → **YoY 사용 시 절대 분모가 너무 작은 케이스(4분기 전 값 < 일정 규모)는 `N/A` 처리** 필수

## 3. 파일 구성 (신규 3개 + 수정 3개)

```
stockinsight/
├── reality_gap.py               # 엔진 (계산 + static/reality_gap.json 저장)
├── templates/reality_gap.html   # 페이지 (Plotly 산점도 + 표)
├── static/reality_gap.json      # 결과 스냅샷 (GHA가 생성, 웹에서 읽음)
├── main.py                      # 수정: /reality-gap 라우트 + sitemap 항목
├── tools/... (nav)              # 수정: 네비에 "현실 괴리 탐지" 추가
└── .github/workflows/
    └── reality_gap.yml          # 신규: 매일 08:20 KST(=23:20 UTC) 계산+커밋
```

**구현 순서 (총 3~5일 실작업 기준)**
1. [ 오늘 ] reality_gap.py 엔진 코어 (68종 × 펀더멘털+가격 계산, 스냅샷 저장)
2. [ 오늘/내일 ] Z-score 정규화 + 분모 작은 케이스 N/A 처리 + 산점도 산출
3. [ 내일 ] /reality-gap 라우트 + reality_gap.html (산점도: X=가격모멘텀, Y=펀더멘털모멘텀, 색=Gap)
4. [ +1일 ] 네비/사이트맵/OG 이미지, GHA 워크플로우
5. [ +2일 ] 트위터/스레드 콘텐츠 1건 + 티스토리(stock-insight-lab) 홍보글 1건 — 검색 유입용

## 4. 페이지 UI (1개 화면)

- **산점도 (핵심)**: X축=가격모멘텀 Z, Y축=펀더멘털모멘텀 Z, 점=종목(국내=파랑,미국=초록)
  - 우상단=둘다 강세, **우하단=가격↑+펀더멘털↓=Negative Gap(과열)**, **좌상단=가격↓+펀더멘털↑=Positive Gap(저평가)**
- **Top 5 저평가 / Top 5 과열 표**: 티커·이름·섹터·가격모멘텀·펀더멘털모멘텀·Score
- **산업 배경 서머리**: FRED 제조생산지수 + 섹터 RS 상위 — 표 위에 2줄 문맥
- **FAQ/설명 블록**: 점수 산식·한계(분기 기준, 초기기업 N/A), SEO 문구 포함
- **OG 이미지**: 산점도 캡처 자동화 (기존 og_generator 재사용)

## 5. 검증·안전장치

- **팩트체크**: 삼성전자(+130% 매출 YoY) 같은 급등 기업 Score 과대 방지 — Z-score로 상대 평가
- **결측**: 펀더멘털 누락 종목은 Gap 계산에서 제외 + `N/A` 표기 (투자 판단 왜곡 방지)
- **주장 수위**: "투자 권유" 아닌 "데이터 기반 괴리 정보" 문구 명시, 면책조항 페이지 링크
- **한자 금지** + 현종님 보고는 3줄 이내
- **성능**: 68종 × ~1.5초 = 2분 이내 계산 (GHA에서 문제없음, 페이지는 스냅샷 JSON만 읽음 — 실시간 API 호출 안 함)

## 6. 배포 직후 성공 기준

1. /reality-gap 페이지 200 + 산점도 렌더 (라이브 실측)
2. static/reality_gap.json 커밋 확인 (GHA 첫 런 성공)
3. SCon 색인 요청 1건 (새 페이지)
4. 7일간 페이지뷰 추적 — stockinsight.app 부진 해소 척도
5. 티스토리 홍보글 유입 확인

---

*작성: 플링크 (2026-10-07 16:20) — 현종님 승인 아래 Reality Gap 우선.*