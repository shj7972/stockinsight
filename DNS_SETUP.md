# DNS 설정 가이드 - stock-insight.app

## 📋 개요

이 가이드는 Heroku에 배포된 애플리케이션에 `stock-insight.app` 도메인을 연결하는 방법을 설명합니다.

---

## 1️⃣ Heroku에서 DNS Target 값 확인하기 ⭐

**도메인을 이미 추가하셨다면, 이 단계에서 DNS Target 값을 확인하세요!**

### 방법 A: Heroku Dashboard에서 확인 (가장 간단) ⭐

1. https://dashboard.heroku.com 접속
2. 배포된 앱 선택 (예: `stock-insight-app`)
3. **Settings** 탭 클릭
4. **Domains** 섹션 스크롤
5. 다음과 같이 표시됩니다:

```
=== Custom Domains
Domain Name      DNS Record Type  DNS Target
stock-insight.app  CNAME            stock-insight-app-12345.herokudns.com
```

**⚠️ 중요: `DNS Target` 값이 바로 DNS 설정에 필요한 값입니다!**

예: `stock-insight-app-12345.herokudns.com` ← 이 값을 복사하세요!

### 방법 B: Heroku CLI로 확인

```bash
# 1. 앱 이름 확인
heroku apps

# 2. 도메인 정보 확인
heroku domains -a <your-app-name>
```

**출력 예시:**
```
=== stock-insight-app Custom Domains
Domain Name      DNS Record Type  DNS Target
stock-insight.app  CNAME            stock-insight-app-12345.herokudns.com
```

**DNS Target 값**: `stock-insight-app-12345.herokudns.com` ← 이 값!

---

## 1-1️⃣ Heroku에 커스텀 도메인 추가 (아직 안 하셨다면)

### Heroku CLI 사용:

```bash
# 1. Heroku에 로그인
heroku login

# 2. 앱 이름 확인 (예: stock-insight-app)
heroku apps

# 3. 도메인 추가
heroku domains:add stock-insight.app -a <your-app-name>

# 4. 확인 (DNS Target 값 확인!)
heroku domains -a <your-app-name>
```

### Heroku Dashboard 사용:

1. https://dashboard.heroku.com 접속
2. 배포된 앱 선택
3. **Settings** 탭 클릭
4. **Domains** 섹션에서 **Add domain** 클릭
5. `stock-insight.app` 입력 후 **Save changes**
6. **DNS Target 값 확인!** (위 표시된 값)

---

## 2️⃣ DNS 레코드 설정

도메인 등록업체(DNS 제공업체)에서 DNS 레코드를 설정해야 합니다.

### 🔍 DNS 제공업체 확인

다음 중 어디에서 도메인을 등록하셨나요?
- GoDaddy
- Namecheap
- AWS Route 53
- Cloudflare
- Google Domains
- 네이버 클라우드 플랫폼
- 기타

---

### 📝 DNS 레코드 설정 (공통)

**⚠️ 먼저 위 1️⃣ 단계에서 Heroku의 DNS Target 값을 확인하세요!**

**도메인 등록업체의 DNS 관리 페이지로 이동합니다.**

#### ✅ 방법 1: CNAME 레코드 (권장)

**예시:** Heroku에서 `stock-insight-app-12345.herokudns.com`를 제공했다면

| 타입 | 호스트/이름 | 값/Target | TTL |
|------|------------|-----------|-----|
| CNAME | @ | `stock-insight-app-12345.herokudns.com` | 3600 |
| CNAME | www | `stock-insight-app-12345.herokudns.com` | 3600 |

**실제 입력값 예시:**
- **타입**: `CNAME`
- **호스트/이름**: `@` (또는 비워두기, 루트 도메인용)
- **값/Target**: `stock-insight-app-12345.herokudns.com` ← **Heroku에서 확인한 DNS Target 값!**
- **TTL**: `3600` (또는 기본값)

**참고:**
- `@` = 루트 도메인 (stock-insight.app)
- `www` = 서브도메인 (www.stock-insight.app) - 선택사항
- **DNS Target 값** = Heroku Dashboard의 **Domains** 섹션에 표시된 값 (예: `xxx-xxxxx.herokudns.com`)

#### ✅ 방법 2: ALIAS/ANAME 레코드 (가능한 경우)

일부 DNS 제공업체는 ALIAS/ANAME 레코드를 지원합니다.

| 타입 | 호스트/이름 | 값/Target | TTL |
|------|------------|-----------|-----|
| ALIAS | @ | `<your-app-name>.herokudns.com` | 3600 |
| CNAME | www | `<your-app-name>.herokudns.com` | 3600 |

---

### 🎯 주요 DNS 제공업체별 설정 방법

#### **GoDaddy**

1. https://godaddy.com 로그인
2. **My Products** → 도메인 클릭
3. **DNS** 탭 클릭
4. **Records** 섹션에서:
   - 기존 `@` 레코드가 있다면 삭제 또는 수정
   - **Add** 클릭
   - **Type**: `CNAME`
   - **Name**: `@` (또는 비워두기)
   - **Value**: `<your-app-name>.herokudns.com`
   - **TTL**: `600 seconds` (또는 기본값)
   - **Save**

#### **Namecheap**

1. https://namecheap.com 로그인
2. **Domain List** → **Manage** 클릭
3. **Advanced DNS** 탭
4. **Host Records** 섹션:
   - 기존 `@` A 레코드가 있다면 삭제
   - **Add New Record**
   - **Type**: `CNAME Record`
   - **Host**: `@`
   - **Value**: `<your-app-name>.herokudns.com`
   - **TTL**: `Automatic`
   - **Save All Changes**

#### **AWS Route 53**

1. AWS Console → Route 53
2. **Hosted zones** → `stock-insight.app` 선택
3. **Create record**:
   - **Record name**: 비워두기 (루트 도메인용)
   - **Record type**: `CNAME`
   - **Value**: `<your-app-name>.herokudns.com`
   - **TTL**: `300`
   - **Create records**

#### **Cloudflare**

1. Cloudflare Dashboard 로그인
2. `stock-insight.app` 도메인 선택
3. **DNS** 탭
4. **Records**:
   - 기존 `@` 레코드가 있다면 클릭하여 수정
   - **Type**: `CNAME`
   - **Name**: `@`
   - **Target**: `<your-app-name>.herokudns.com`
   - **Proxy status**: 🟠 **DNS only** (Gray cloud) - **중요!**
   - **TTL**: `Auto`
   - **Save**

⚠️ **Cloudflare 사용 시 주의사항:**
- Heroku와 함께 사용하려면 Proxy를 **비활성화**해야 합니다 (Gray cloud)
- Orange cloud (Proxy 활성화) 상태에서는 CNAME이 작동하지 않을 수 있습니다

#### **네이버 클라우드 플랫폼**

1. 네이버 클라우드 콘솔 로그인
2. **DNS Plus** → 도메인 선택
3. **레코드 관리**
4. **레코드 추가**:
   - **레코드 유형**: `CNAME`
   - **호스트**: `@` (또는 비워두기)
   - **값**: `<your-app-name>.herokudns.com`
   - **TTL**: `3600`
   - **저장**

---

## 3️⃣ SSL 인증서 자동 발급

Heroku는 자동으로 SSL 인증서를 발급합니다.

### 확인 방법:

```bash
# CLI로 확인
heroku certs -a <your-app-name>
```

또는 Heroku Dashboard:
- **Settings** → **SSL Certificate**
- **Automatic Certificate Management (ACM)** 활성화 확인

**SSL 인증서 발급까지 보통 1-10분 소요됩니다.**

---

## 4️⃣ DNS 전파 확인

DNS 변경 사항이 전 세계에 전파되는 데 **24-48시간**이 걸릴 수 있습니다.

### 즉시 확인 방법:

#### A. 온라인 DNS 체커 사용
- https://www.whatsmydns.net
- https://dnschecker.org
- 도메인: `stock-insight.app`
- 레코드 타입: `CNAME`

#### B. 터미널에서 확인 (Windows)

```powershell
# PowerShell에서
Resolve-DnsName stock-insight.app -Type CNAME
```

또는:

```cmd
nslookup stock-insight.app
```

#### C. 브라우저에서 직접 접속 테스트

```
https://stock-insight.app
```

**정상 작동 시:**
- HTTPS로 리다이렉트됨
- 브라우저 주소창에 자물쇠 아이콘 표시
- 사이트가 정상적으로 로드됨

---

## 5️⃣ www 서브도메인 설정 (선택사항)

`www.stock-insight.app`도 작동하게 하려면:

### Heroku에서:
```bash
heroku domains:add www.stock-insight.app -a <your-app-name>
```

### DNS에서:
| 타입 | 호스트/이름 | 값/Target | TTL |
|------|------------|-----------|-----|
| CNAME | www | `<your-app-name>.herokudns.com` | 3600 |

---

## 6️⃣ 코드에서 도메인 확인

배포 전에 코드의 모든 도메인 참조를 확인하세요:

```bash
# 프로젝트에서 stock-insight.app 검색
grep -r "stock-insight.app" .
```

**확인해야 할 파일:**
- `main.py` (sitemap.xml 생성 부분)
- `static/robots.txt`
- `templates/base.html` (canonical URL, OG tags)

---

## 🚨 문제 해결

### 문제 1: "DNS_PROBE_FINISHED_NXDOMAIN" 오류

**원인:** DNS 레코드가 아직 전파되지 않음

**해결:**
- DNS 설정이 올바른지 확인
- 24-48시간 대기
- 다른 DNS 체커로 확인

### 문제 2: SSL 인증서 오류

**원인:** SSL 인증서가 아직 발급되지 않음

**해결:**
```bash
# Heroku에서 SSL 인증서 강제 갱신 (필요시)
heroku certs:auto:refresh -a <your-app-name>
```

### 문제 3: "Too many redirects" 오류

**원인:** DNS 설정 오류 또는 Cloudflare Proxy 활성화

**해결:**
- Cloudflare 사용 시 Proxy 비활성화 (Gray cloud)
- DNS 레코드 타입 확인 (CNAME이어야 함)

### 문제 4: 여전히 .herokuapp.com으로 접속됨

**원인:** DNS 전파가 완료되지 않음

**해결:**
- 로컬 DNS 캐시 삭제:
  ```powershell
  # Windows PowerShell (관리자 권한)
  ipconfig /flushdns
  ```
- 브라우저 캐시 삭제 또는 시크릿 모드로 테스트

---

## ✅ 최종 확인 체크리스트

- [ ] Heroku에 `stock-insight.app` 도메인 추가 완료
- [ ] DNS 제공업체에서 CNAME 레코드 설정 완료
- [ ] DNS 전파 확인 (whatsmydns.net 사용)
- [ ] `https://stock-insight.app` 접속 가능
- [ ] SSL 인증서 정상 작동 (자물쇠 아이콘 표시)
- [ ] `https://stock-insight.app/robots.txt` 접속 가능
- [ ] `https://stock-insight.app/sitemap.xml` 접속 가능
- [ ] 코드 내 도메인 참조 확인 완료

---

## 📞 추가 도움말

- **Heroku 공식 문서**: https://devcenter.heroku.com/articles/custom-domains
- **DNS 제공업체 지원팀**: DNS 설정 문제는 도메인 등록업체에 문의

---

**배포 날짜**: 2025-01-06  
**도메인**: stock-insight.app  
**배포 플랫폼**: Heroku

