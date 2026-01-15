# 접속 문제 해결 가이드

## 현재 상태 확인

✅ **Heroku 도메인 등록**: 완료
✅ **SSL 인증서**: 발급 완료 (ACM)
✅ **DNS CNAME**: 정상 확인됨

⚠️ **로컬 DNS 해석**: 실패 (캐시 문제 가능성)

---

## 해결 방법

### 1. DNS 캐시 삭제 (가장 중요!)

**Windows PowerShell (관리자 권한 필요):**

```powershell
# DNS 캐시 삭제
ipconfig /flushdns

# 확인
Resolve-DnsName stock-insight.app -Type CNAME
```

**명령 프롬프트 (관리자 권한 필요):**

```cmd
ipconfig /flushdns
```

### 2. 브라우저 캐시 삭제

1. **Chrome/Edge**:
   - `Ctrl + Shift + Delete`
   - "캐시된 이미지 및 파일" 선택
   - "데이터 삭제" 클릭

2. **시크릿/프라이빗 모드로 접속**
   - Chrome: `Ctrl + Shift + N`
   - Edge: `Ctrl + Shift + P`

### 3. 다른 DNS 서버 사용 (선택)

**Google DNS 사용:**
1. 제어판 → 네트워크 및 공유 센터
2. 어댑터 설정 변경
3. 네트워크 어댑터 우클릭 → 속성
4. IPv4 속성 → 다음 DNS 서버 주소 사용:
   - 기본 DNS: `8.8.8.8`
   - 보조 DNS: `8.8.4.4`

### 4. 다른 브라우저로 접속 테스트

- Chrome
- Edge
- Firefox

### 5. 다른 네트워크에서 접속 테스트

- 모바일 데이터 사용
- 다른 Wi-Fi 네트워크
- 핫스팟 사용

---

## 온라인 도구로 확인

### 1. DNS 전파 확인
- https://www.whatsmydns.net/#CNAME/stock-insight.app
- 여러 지역에서 확인됨 = 정상

### 2. 사이트 상태 확인
- https://downforeveryoneorjustme.com/stock-insight.app
- "It's just you" = 정상 (로컬 문제)

### 3. SSL 인증서 확인
- https://www.ssllabs.com/ssltest/analyze.html?d=stock-insight.app

---

## 빠른 확인 방법

### 방법 1: 시크릿 모드로 접속

1. 브라우저 시크릿 모드 열기
2. `https://stock-insight.app` 접속
3. 정상 접속되면 → 브라우저 캐시 문제

### 방법 2: 다른 디바이스로 접속

- 스마트폰 브라우저로 접속
- 정상 접속되면 → PC 로컬 문제

### 방법 3: Heroku URL로 접속

```
https://stock-insight-ai-9ef2fcc96a08.herokuapp.com/
```

이 URL로 접속되면 → 도메인 연결 문제

---

## 단계별 해결 절차

### 1단계: DNS 캐시 삭제 (필수)

```powershell
# PowerShell을 관리자 권한으로 실행
ipconfig /flushdns
```

### 2단계: 브라우저 캐시 삭제

- 시크릿 모드로 접속 또는
- 브라우저 캐시 삭제

### 3단계: 5-10분 대기

DNS 변경사항이 전파되는 데 시간이 걸릴 수 있습니다.

### 4단계: 다시 접속 시도

```
https://stock-insight.app
```

---

## 여전히 접속이 안 되면

### 확인 사항

1. **다른 디바이스에서 접속 확인**
   - 모바일 브라우저
   - 다른 PC

2. **온라인 도구로 확인**
   - https://www.whatsmydns.net/#CNAME/stock-insight.app
   - 여러 지역에서 확인되는지 확인

3. **Heroku Dashboard 확인**
   - https://dashboard.heroku.com
   - 앱 상태 확인
   - Metrics 탭에서 트래픽 확인

4. **에러 메시지 확인**
   - 브라우저에서 정확한 에러 메시지 확인
   - 개발자 도구 (F12) → Console 탭 확인

---

## 일반적인 에러 메시지와 해결책

### "ERR_NAME_NOT_RESOLVED"
- **원인**: DNS 문제
- **해결**: DNS 캐시 삭제, 다른 DNS 서버 사용

### "ERR_CONNECTION_REFUSED"
- **원인**: 서버 문제 또는 방화벽
- **해결**: Heroku Dashboard에서 앱 상태 확인

### "ERR_SSL_PROTOCOL_ERROR"
- **원인**: SSL 인증서 문제
- **해결**: SSL 인증서는 이미 발급됨, 브라우저 캐시 삭제

### "사이트에 연결할 수 없음"
- **원인**: 네트워크 또는 DNS 문제
- **해결**: DNS 캐시 삭제, 다른 네트워크 사용

---

## 즉시 시도할 방법

1. **시크릿 모드로 접속** (가장 빠름)
2. **DNS 캐시 삭제** (`ipconfig /flushdns`)
3. **다른 브라우저로 접속**
4. **모바일에서 접속 확인**

---

**대부분의 경우 DNS 캐시 삭제와 브라우저 캐시 삭제로 해결됩니다!**

