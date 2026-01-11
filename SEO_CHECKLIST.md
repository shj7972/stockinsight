# SEO 설정 확인 체크리스트 - stock-insight.app

## ✅ 현재 설정 상태

### 1. robots.txt ✅

**파일 위치**: `static/robots.txt`  
**엔드포인트**: `https://stock-insight.app/robots.txt`  
**상태**: 정상 설정됨

**내용 확인:**
- ✅ 모든 검색로봇 허용 (`User-agent: *`)
- ✅ 네이버 로봇 명시적 허용 (Yeti, NaverBot)
- ✅ 구글 로봇 허용 (Googlebot, Googlebot-Image)
- ✅ 빙, 다음 로봇 허용
- ✅ Sitemap 위치 명시

**확인 방법:**
```
브라우저에서 https://stock-insight.app/robots.txt 접속 확인
```

---

### 2. sitemap.xml ✅

**생성 방식**: 동적 생성 (`main.py`의 `/sitemap.xml` 엔드포인트)  
**엔드포인트**: `https://stock-insight.app/sitemap.xml`  
**상태**: 정상 설정됨

**포함된 URL:**
- ✅ 메인 페이지 (`/`)
- ✅ 주요 기능 페이지 (yield-calculator, fear-greed-index, exchange-rate, etf-explorer)
- ✅ 미국 인기 주식 8개 (`?ticker=AAPL` 등)
- ✅ 한국 인기 주식 4개 (`?ticker=005930.KS` 등)

**특징:**
- ✅ 날짜 자동 업데이트 (`lastmod`)
- ✅ 우선순위 설정 (`priority`)
- ✅ 변경 빈도 설정 (`changefreq`)

**확인 방법:**
```
브라우저에서 https://stock-insight.app/sitemap.xml 접속 확인
```

---

### 3. 메타 태그 ✅

**파일 위치**: `templates/base.html`  
**상태**: 정상 설정됨

**포함된 메타 태그:**
- ✅ `<meta charset="UTF-8">`
- ✅ `<meta name="viewport">`
- ✅ `<meta name="robots">` - index, follow
- ✅ `<meta name="googlebot">` - index, follow
- ✅ `<meta name="Yeti">` - 네이버 로봇
- ✅ `<meta name="NaverBot">` - 네이버 로봇
- ✅ `<meta name="description">` - 사이트 설명
- ✅ `<meta name="keywords">` - 키워드
- ✅ `<meta property="og:title">` - Open Graph 제목
- ✅ `<meta property="og:description">` - Open Graph 설명
- ✅ `<meta property="og:type">` - website
- ✅ `<meta property="og:url">` - 사이트 URL
- ✅ `<meta property="og:image">` - OG 이미지
- ✅ `<link rel="canonical">` - 정규 URL

**확인 방법:**
```
브라우저 개발자 도구 (F12) → Elements → <head> 섹션 확인
또는
브라우저에서 페이지 소스 보기 (Ctrl+U)
```

---

## 🔍 배포 후 확인 사항

### 필수 확인 항목

1. **robots.txt 접근 확인**
   - [ ] `https://stock-insight.app/robots.txt` 접속 가능
   - [ ] 내용이 정상적으로 표시됨
   - [ ] Sitemap 위치가 올바르게 표시됨

2. **sitemap.xml 접근 확인**
   - [ ] `https://stock-insight.app/sitemap.xml` 접속 가능
   - [ ] XML 형식이 올바르게 표시됨
   - [ ] 모든 URL이 포함되어 있음
   - [ ] 날짜가 최신으로 업데이트됨

3. **메타 태그 확인**
   - [ ] 페이지 소스에서 메타 태그 확인
   - [ ] 모든 필수 메타 태그가 포함되어 있음
   - [ ] Open Graph 태그가 올바르게 설정됨

4. **HTTPS 확인**
   - [ ] HTTPS로 접속 가능
   - [ ] 브라우저 주소창에 자물쇠 🔒 아이콘 표시
   - [ ] SSL 인증서 오류 없음

---

## 🌐 검색엔진 등록 준비

### 등록 전 확인 체크리스트

- [ ] `https://stock-insight.app/robots.txt` 접속 가능
- [ ] `https://stock-insight.app/sitemap.xml` 접속 가능
- [ ] 메타 태그 확인 완료
- [ ] HTTPS 연결 확인 완료
- [ ] 사이트가 정상적으로 작동함

### 등록할 검색엔진

1. **구글 서치 콘솔** (필수)
   - URL: https://search.google.com/search-console
   - 등록 방법: `SEARCH_ENGINE_REGISTRATION.md` 참고

2. **네이버 서치어드바이저** (한국 필수)
   - URL: https://searchadvisor.naver.com
   - 등록 방법: `SEARCH_ENGINE_REGISTRATION.md` 참고

3. **빙 웹마스터 도구** (선택)
   - URL: https://www.bing.com/webmasters
   - 등록 방법: `SEARCH_ENGINE_REGISTRATION.md` 참고

---

## 📝 개선 권장 사항

### 1. Open Graph 이미지 추가 (선택)

현재 설정: `https://stock-insight.app/static/og-image.png`

**권장 사항:**
- `static/og-image.png` 파일 생성
- 크기: 1200x630px
- 사이트 로고 및 설명 포함

### 2. Favicon 추가 (선택)

현재 설정: `/static/favicon.png`

**권장 사항:**
- `static/favicon.png` 파일 생성
- 크기: 32x32px 또는 16x16px

### 3. 구조화된 데이터 (Schema.org) 추가 (추후)

**권장 스키마:**
- `Organization` - 사이트 정보
- `WebSite` - 웹사이트 정보
- `Article` - 뉴스 섹션용

---

## ✅ 최종 확인

### 배포 후 즉시 확인:

1. **브라우저에서 직접 확인**
   ```
   https://stock-insight.app/robots.txt
   https://stock-insight.app/sitemap.xml
   https://stock-insight.app/
   ```

2. **온라인 도구로 확인**
   - Sitemap 검증: https://www.xml-sitemaps.com/validate-xml-sitemap.html
   - Robots.txt 검증: https://www.google.com/webmasters/tools/robots-testing-tool

3. **검색엔진 등록**
   - 구글 서치 콘솔 등록
   - 네이버 서치어드바이저 등록

---

## 📞 문제 해결

### 문제 1: robots.txt 접근 불가

**확인 사항:**
- FastAPI에서 `/robots.txt` 엔드포인트 확인
- `static/robots.txt` 파일 존재 확인
- 배포 상태 확인

### 문제 2: sitemap.xml 접근 불가

**확인 사항:**
- FastAPI에서 `/sitemap.xml` 엔드포인트 확인
- XML 형식 오류 확인
- 배포 상태 확인

### 문제 3: 메타 태그가 표시되지 않음

**확인 사항:**
- `templates/base.html` 파일 확인
- Jinja2 템플릿 렌더링 확인
- 브라우저 캐시 삭제 후 재확인

---

**모든 확인이 완료되면 `SEARCH_ENGINE_REGISTRATION.md` 파일의 가이드를 따라 검색엔진에 등록하세요!**

