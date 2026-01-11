# 검색엔진 등록 가이드 - stock-insight.app

## 📋 준비사항 확인

### ✅ 현재 설정 상태

#### 1. robots.txt
- ✅ 파일 위치: `static/robots.txt`
- ✅ 엔드포인트: `https://stock-insight.app/robots.txt`
- ✅ 주요 검색로봇 허용 설정 완료
- ✅ Sitemap 위치 명시 완료

#### 2. sitemap.xml
- ✅ 동적 생성: `main.py`의 `/sitemap.xml` 엔드포인트
- ✅ 엔드포인트: `https://stock-insight.app/sitemap.xml`
- ✅ 인기 주식 페이지 포함

#### 3. SEO 메타 태그
- ✅ `templates/base.html`에 메타 태그 설정 완료
- ✅ robots, description, keywords, Open Graph 태그 포함

---

## 🔍 사전 확인 (배포 후 필수!)

### 1. robots.txt 접근 확인

브라우저에서 직접 접속:
```
https://stock-insight.app/robots.txt
```

**예상 결과:**
```
User-agent: *
Allow: /
...
Sitemap: https://stock-insight.app/sitemap.xml
```

### 2. sitemap.xml 접근 확인

브라우저에서 직접 접속:
```
https://stock-insight.app/sitemap.xml
```

**예상 결과:**
- XML 형식의 사이트맵 표시
- 메인 페이지 및 인기 주식 페이지 URL 목록

### 3. 메타 태그 확인

브라우저 개발자 도구 (F12) → Elements → `<head>` 섹션 확인:
- `<meta name="description">`
- `<meta name="keywords">`
- `<meta property="og:title">`
- `<meta property="og:description">`
- `<link rel="canonical">`

---

## 🌐 구글 서치 콘솔 등록

### 1단계: 구글 서치 콘솔 접속

1. https://search.google.com/search-console 접속
2. Google 계정으로 로그인

### 2단계: 속성 추가

1. **"속성 추가"** 클릭
2. **"URL 접두어"** 선택
3. URL 입력: `https://stock-insight.app`
4. **"계속"** 클릭

### 3단계: 소유권 확인

**방법 1: HTML 파일 (권장)**
1. "HTML 파일" 선택
2. 제공된 HTML 파일 다운로드
3. `static/` 폴더에 업로드
4. FastAPI에서 해당 파일 서빙 설정
5. "확인" 클릭

**방법 2: HTML 태그**
1. "HTML 태그" 선택
2. 제공된 메타 태그 복사
3. `templates/base.html`의 `<head>` 섹션에 추가
4. 배포 후 "확인" 클릭

**방법 3: DNS 확인**
1. "도메인 이름 제공업체" 선택
2. 제공된 TXT 레코드를 DNS에 추가
3. DNS 전파 후 "확인" 클릭

### 4단계: Sitemap 제출

소유권 확인 후:
1. 좌측 메뉴에서 **"Sitemaps"** 클릭
2. **"새 사이트맵 추가"** 클릭
3. Sitemap URL 입력: `sitemap.xml`
4. **"제출"** 클릭

**예상 결과:**
- 상태: "성공" ✅
- 발견된 URL 수: 13개 (메인 1개 + 주식 12개)

### 5단계: URL 검사

1. 상단 검색창에 URL 입력: `https://stock-insight.app`
2. **"색인 생성 요청"** 클릭 (선택사항)
3. 구글이 크롤링할 때까지 대기 (보통 1-7일)

---

## 🇰🇷 네이버 서치어드바이저 등록

### 1단계: 네이버 서치어드바이저 접속

1. https://searchadvisor.naver.com 접속
2. 네이버 계정으로 로그인

### 2단계: 사이트 등록

1. **"웹마스터 도구"** → **"사이트 등록"**
2. 사이트 URL 입력: `https://stock-insight.app`
3. **"등록"** 클릭

### 3단계: 소유권 확인

**방법 1: HTML 파일 (권장)**
1. "HTML 파일" 선택
2. 제공된 HTML 파일 다운로드
3. `static/` 폴더에 업로드
4. FastAPI에서 해당 파일 서빙 설정
5. "확인" 클릭

**방법 2: 메타 태그**
1. "메타 태그" 선택
2. 제공된 메타 태그 복사
3. `templates/base.html`의 `<head>` 섹션에 추가
4. 배포 후 "확인" 클릭

### 4단계: robots.txt 확인

1. **"요청"** → **"robots.txt"** 클릭
2. `https://stock-insight.app/robots.txt` 확인
3. 네이버 로봇(Yeti, NaverBot) 허용 확인

### 5단계: Sitemap 제출

1. **"요청"** → **"사이트맵 제출"**
2. Sitemap URL 입력: `https://stock-insight.app/sitemap.xml`
3. **"확인"** 클릭

### 6단계: 크롤링 요청

1. **"요청"** → **"수집 요청"**
2. 사이트 URL 입력: `https://stock-insight.app`
3. **"요청"** 클릭

---

## 🔍 빙 웹마스터 도구 등록

### 1단계: 빙 웹마스터 도구 접속

1. https://www.bing.com/webmasters 접속
2. Microsoft 계정으로 로그인

### 2단계: 사이트 추가

1. **"사이트 추가"** 클릭
2. 사이트 URL 입력: `https://stock-insight.app`
3. **"추가"** 클릭

### 3단계: 소유권 확인

**방법 1: XML 파일**
1. "XML 파일" 선택
2. 제공된 XML 파일 다운로드
3. `static/` 폴더에 업로드
4. FastAPI에서 해당 파일 서빙 설정
5. "확인" 클릭

**방법 2: 메타 태그**
1. "메타 태그" 선택
2. 제공된 메타 태그 복사
3. `templates/base.html`의 `<head>` 섹션에 추가
4. 배포 후 "확인" 클릭

### 4단계: Sitemap 제출

1. **"Sitemaps"** 클릭
2. Sitemap URL 입력: `https://stock-insight.app/sitemap.xml`
3. **"제출"** 클릭

---

## ✅ 등록 체크리스트

### 사전 준비
- [ ] `https://stock-insight.app/robots.txt` 접속 가능 확인
- [ ] `https://stock-insight.app/sitemap.xml` 접속 가능 확인
- [ ] 메타 태그 확인 (브라우저 개발자 도구)
- [ ] HTTPS 연결 확인 (자물쇠 🔒 아이콘)

### 구글 서치 콘솔
- [ ] 속성 추가 (`https://stock-insight.app`)
- [ ] 소유권 확인 완료
- [ ] Sitemap 제출 완료
- [ ] URL 검사 및 색인 생성 요청

### 네이버 서치어드바이저
- [ ] 사이트 등록 (`https://stock-insight.app`)
- [ ] 소유권 확인 완료
- [ ] robots.txt 확인 완료
- [ ] Sitemap 제출 완료
- [ ] 수집 요청 완료

### 빙 웹마스터 도구
- [ ] 사이트 추가 (`https://stock-insight.app`)
- [ ] 소유권 확인 완료
- [ ] Sitemap 제출 완료

---

## 📊 등록 후 모니터링

### 구글 서치 콘솔

1. **성능 보고서**
   - 노출수, 클릭수, CTR 확인
   - 확인 주기: 주 1회

2. **색인 범위**
   - 색인 생성된 페이지 수 확인
   - 오류 확인 및 해결

3. **Sitemaps**
   - 제출된 URL 수 확인
   - 오류 확인

### 네이버 서치어드바이저

1. **요약 정보**
   - 수집된 페이지 수 확인
   - 확인 주기: 주 1회

2. **수집 현황**
   - 수집 성공/실패 확인
   - 오류 분석 및 해결

3. **사이트맵**
   - 제출된 URL 수 확인
   - 상태 확인

---

## 🚨 문제 해결

### 문제 1: "robots.txt를 찾을 수 없습니다"

**원인**: FastAPI 엔드포인트 설정 오류

**해결**:
1. `main.py`에서 `/robots.txt` 엔드포인트 확인
2. 배포 상태 확인
3. 브라우저에서 직접 접속 테스트

### 문제 2: "sitemap.xml을 찾을 수 없습니다"

**원인**: sitemap.xml 엔드포인트 오류

**해결**:
1. `main.py`에서 `/sitemap.xml` 엔드포인트 확인
2. 브라우저에서 직접 접속 테스트
3. XML 형식 오류 확인

### 문제 3: "소유권 확인 실패"

**원인**: 
- HTML 파일/메타 태그가 올바른 위치에 없음
- DNS TXT 레코드 전파 미완료

**해결**:
1. 제공된 파일/태그가 올바른 위치에 있는지 확인
2. 브라우저에서 직접 접속하여 확인
3. DNS TXT 레코드 전파 확인 (24-48시간 소요 가능)

### 문제 4: "Sitemap 제출 실패"

**원인**: 
- Sitemap URL 오류
- XML 형식 오류
- 접근 불가

**해결**:
1. Sitemap URL 정확성 확인 (`https://stock-insight.app/sitemap.xml`)
2. 브라우저에서 직접 접속하여 XML 형식 확인
3. XML 유효성 검사 도구 사용

---

## 💡 추가 최적화 팁

### 1. 구조화된 데이터 (Schema.org)

추후 추가 권장:
- `Organization` 스키마
- `WebSite` 스키마
- `Article` 스키마 (뉴스 섹션용)

### 2. Open Graph 이미지

- `static/og-image.png` 파일 생성 권장
- 크기: 1200x630px
- 사이트 로고 및 설명 포함

### 3. Favicon

- `static/favicon.png` 파일 생성 권장
- 크기: 32x32px 또는 16x16px

### 4. 정기적인 Sitemap 업데이트

- 새로운 인기 주식 추가 시 sitemap.xml 업데이트
- `lastmod` 날짜 정기 업데이트

---

## 📞 참고 링크

- **구글 서치 콘솔**: https://search.google.com/search-console
- **네이버 서치어드바이저**: https://searchadvisor.naver.com
- **빙 웹마스터 도구**: https://www.bing.com/webmasters
- **Sitemap 프로토콜**: https://www.sitemaps.org/protocol.html
- **robots.txt 규칙**: https://www.robotstxt.org/

---

**등록 완료 후 1-2주 후부터 검색 결과에 나타나기 시작합니다!**

