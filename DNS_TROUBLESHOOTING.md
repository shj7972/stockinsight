# DNS 연결 문제 해결 가이드

## 🔍 현재 상태 확인

### 1. DNS 전파 상태 확인

온라인 도구로 확인:
- https://www.whatsmydns.net/#CNAME/stock-insight.app
- https://dnschecker.org/#CNAME/stock-insight.app

**확인할 값:**
- `stock-insight.app` → `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`

**예상 결과:**
- ✅ **일부 지역에서 확인됨**: DNS 전파 중 (정상, 시간 필요)
- ✅ **모든 지역에서 확인됨**: DNS 전파 완료
- ❌ **확인 안 됨**: DNS 설정 오류 가능성

---

### 2. Heroku SSL 인증서 상태 확인

#### 방법 A: Heroku Dashboard

1. https://dashboard.heroku.com 접속
2. 배포된 앱 선택
3. **Settings** 탭 클릭
4. **SSL Certificate** 섹션 확인

**상태 확인:**
- ✅ **"Automatic Certificate Management (ACM)"** 활성화됨
- ✅ **"Cert Issued"** 또는 **"Cert Active"**: SSL 인증서 발급 완료
- ⏳ **"Pending"** 또는 **"Requesting"**: SSL 인증서 발급 중 (DNS 전파 필요)
- ❌ **"Error"**: 오류 발생

#### 방법 B: Heroku CLI

```bash
# SSL 인증서 상태 확인
heroku certs -a <your-app-name>

# 또는 ACM 상태 확인
heroku certs:auto -a <your-app-name>
```

---

## ⏰ 예상 소요 시간

### DNS 전파
- **빠른 경우**: 10분 ~ 1시간
- **일반적인 경우**: 1 ~ 6시간
- **느린 경우**: 24 ~ 48시간

### SSL 인증서 발급
- DNS 전파 완료 후: **1 ~ 10분**
- Heroku는 DNS가 전파되면 자동으로 SSL 인증서를 발급합니다

---

## 🚨 SSL 필수 도메인 문제

`.app` 도메인은 Google이 관리하는 **HTTPS 필수 도메인**입니다.

### .app 도메인의 특징:
- ✅ HTTPS 연결 필수
- ✅ SSL 인증서가 없으면 접속 불가
- ✅ Heroku는 자동으로 SSL 인증서 발급 (DNS 전파 후)

### 현재 상황:
1. DNS 설정은 완료했지만 **전파 중**일 수 있습니다
2. DNS 전파가 완료되어야 Heroku가 SSL 인증서를 발급할 수 있습니다
3. SSL 인증서 발급 후에야 `https://stock-insight.app` 접속 가능

---

## ✅ 해결 방법

### 1단계: DNS 전파 확인 (우선)

온라인 도구로 확인:
```
https://www.whatsmydns.net/#CNAME/stock-insight.app
```

**결과 해석:**
- 🟢 **여러 지역에서 확인됨**: DNS 전파 중 (정상)
  → 1~6시간 더 기다리세요
- 🔴 **전혀 확인 안 됨**: DNS 설정 오류 가능성
  → DNS 제공업체에서 설정 확인 필요

### 2단계: SSL 인증서 발급 대기

DNS 전파가 완료되면 (여러 지역에서 확인됨):
- Heroku가 자동으로 SSL 인증서를 발급합니다
- 발급까지 **1~10분** 소요
- Heroku Dashboard → Settings → SSL Certificate에서 확인

### 3단계: 로컬 DNS 캐시 삭제 (Windows)

DNS 캐시를 삭제하여 즉시 확인:

```powershell
# PowerShell (관리자 권한)
ipconfig /flushdns
```

또는:

```cmd
# 명령 프롬프트 (관리자 권한)
ipconfig /flushdns
```

**주의**: 관리자 권한이 필요합니다.

### 4단계: 브라우저 캐시 삭제 또는 시크릿 모드

- **시크릿/프라이빗 모드**로 접속 테스트
- 또는 브라우저 캐시 삭제 후 재시도

---

## 🔧 즉시 확인할 수 있는 방법

### 1. 터미널에서 DNS 확인 (Windows)

```powershell
# PowerShell
Resolve-DnsName stock-insight.app -Type CNAME
```

또는:

```cmd
nslookup stock-insight.app
```

**예상 결과 (정상):**
```
Name: stock-insight.app
CanonicalName: transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com
```

### 2. curl로 직접 확인

```powershell
# PowerShell
curl https://stock-insight.app
```

또는:

```bash
curl -I https://stock-insight.app
```

**응답 코드:**
- `200 OK`: 정상 작동 ✅
- `SSL certificate problem`: SSL 인증서 발급 중 ⏳
- `Could not resolve host`: DNS 전파 안 됨 ❌

---

## 📋 체크리스트

현재 상태를 확인하세요:

- [ ] DNS 전파 확인 (whatsmydns.net)
  - [ ] 일부 지역에서 확인됨 → 대기 중 (정상)
  - [ ] 전혀 확인 안 됨 → DNS 설정 오류 확인 필요

- [ ] Heroku SSL 인증서 상태
  - [ ] Heroku Dashboard → Settings → SSL Certificate 확인
  - [ ] "Pending" 또는 "Requesting" → DNS 전파 대기 중
  - [ ] "Cert Issued" 또는 "Cert Active" → 정상

- [ ] 로컬 DNS 캐시 삭제 (선택사항)
  - [ ] `ipconfig /flushdns` 실행

- [ ] 브라우저에서 접속 테스트
  - [ ] 시크릿 모드로 접속
  - [ ] `https://stock-insight.app` 접속
  - [ ] `https://www.stock-insight.app` 접속

---

## 🎯 예상 타임라인

### 시나리오 1: 방금 DNS 설정 완료
```
현재: DNS 설정 완료
0-1시간: DNS 전파 시작
1-6시간: 대부분의 지역에서 DNS 전파 완료
6-7시간: Heroku SSL 인증서 자동 발급
7시간 후: https://stock-insight.app 접속 가능
```

### 시나리오 2: DNS 설정이 1시간 이상 전에 완료
```
1. DNS 전파 확인: https://www.whatsmydns.net
2. 전파가 완료되었는데도 접속 안 되면:
   - Heroku Dashboard에서 SSL 인증서 상태 확인
   - DNS 레코드 설정 재확인 (오타 확인)
```

---

## ⚠️ 자주 발생하는 문제

### 문제 1: "ERR_SSL_VERSION_OR_CIPHER_MISMATCH" 오류

**원인**: SSL 인증서가 아직 발급되지 않음

**해결**:
- DNS 전파 완료 대기
- Heroku Dashboard에서 SSL 인증서 발급 상태 확인

### 문제 2: "DNS_PROBE_FINISHED_NXDOMAIN" 오류

**원인**: DNS가 전파되지 않음 또는 DNS 설정 오류

**해결**:
- DNS 설정 재확인 (DNS 제공업체에서)
- DNS 전파 확인 (whatsmydns.net)
- 24시간 더 대기

### 문제 3: ".herokuapp.com"로만 접속됨

**원인**: DNS 전파 미완료

**해결**:
- DNS 전파 대기
- 로컬 DNS 캐시 삭제 (`ipconfig /flushdns`)

---

## 💡 빠른 확인 방법 요약

1. **DNS 전파 확인** (가장 중요):
   ```
   https://www.whatsmydns.net/#CNAME/stock-insight.app
   ```

2. **Heroku SSL 상태 확인**:
   ```
   Heroku Dashboard → Settings → SSL Certificate
   ```

3. **로컬 확인**:
   ```powershell
   Resolve-DnsName stock-insight.app -Type CNAME
   ```

4. **접속 테스트**:
   ```
   https://stock-insight.app
   ```

---

**결론: `.app` 도메인은 HTTPS 필수이므로, DNS 전파가 완료되어 Heroku가 SSL 인증서를 발급할 때까지 기다려야 합니다. 보통 1-6시간 소요됩니다.**

