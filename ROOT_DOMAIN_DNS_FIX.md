# 루트 도메인 접속 문제 해결 - stock-insight.app

## 문제 상황

- ✅ `https://www.stock-insight.app` → 접속 정상
- ❌ `https://stock-insight.app` → 접속 안 됨

## 원인 분석

**루트 도메인(`@`)의 DNS 레코드 설정 문제입니다.**

### 확인 사항

1. **Heroku 설정**: 정상
   - 루트 도메인: `stock-insight.app` (ALIAS/ANAME)
   - www 서브도메인: `www.stock-insight.app` (CNAME)
   - SSL 인증서: 둘 다 발급 완료

2. **DNS 설정 문제**
   - www는 CNAME 레코드로 작동함
   - 루트 도메인은 CNAME이 아닌 ALIAS/ANAME 레코드 필요

---

## 해결 방법

### DNS 제공업체에서 루트 도메인 레코드 확인 및 수정

**문제**: 루트 도메인(`@`)에 CNAME 레코드를 사용할 수 없는 DNS 제공업체가 많습니다.

**해결**: ALIAS 또는 ANAME 레코드 사용

---

## DNS 제공업체별 해결 방법

### 1. GoDaddy

**현재 설정 확인:**
1. https://godaddy.com 로그인
2. My Products → `stock-insight.app` 클릭
3. DNS 탭

**수정 방법:**
1. 기존 `@` CNAME 레코드 찾기
2. 레코드 삭제 또는 수정
3. **새 레코드 추가**:
   - **Type**: `ALIAS` (가능한 경우) 또는 `A` 레코드 사용 불가 → Heroku는 ALIAS/ANAME만 지원
   - **Name**: `@` (또는 비워두기)
   - **Value**: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
   - **TTL**: 3600

**⚠️ 주의**: GoDaddy는 루트 도메인에 CNAME을 지원하지 않을 수 있습니다. ALIAS 레코드가 없으면 다음 방법 시도:

**대안 (GoDaddy):**
- **Type**: `A` 레코드 사용 불가 (Heroku는 동적 IP 사용)
- **해결책**: DNS 제공업체를 Cloudflare로 변경 권장 (무료, ALIAS 지원)

---

### 2. Namecheap

**현재 설정 확인:**
1. https://namecheap.com 로그인
2. Domain List → `stock-insight.app` → Manage
3. Advanced DNS 탭

**수정 방법:**
1. 기존 `@` 레코드 찾기
2. 레코드 삭제
3. **새 레코드 추가**:
   - **Type**: `ANAME Record` (Namecheap는 ANAME 지원)
   - **Host**: `@`
   - **Value**: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
   - **TTL**: Automatic
   - Save All Changes

---

### 3. Cloudflare (권장)

**Cloudflare 사용 시:**

1. Cloudflare Dashboard 로그인
2. `stock-insight.app` 도메인 선택
3. DNS 탭

**루트 도메인 설정:**
- **Type**: `CNAME` (Cloudflare는 루트 도메인에 CNAME 지원)
- **Name**: `@`
- **Target**: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
- **Proxy status**: 🟠 **DNS only** (Gray cloud) - **중요!**
- **TTL**: Auto

**Cloudflare 장점:**
- ✅ 루트 도메인에 CNAME 지원
- ✅ 무료
- ✅ 빠른 DNS 전파
- ✅ 추가 보안 기능

---

### 4. AWS Route 53

**Route 53 사용 시:**

1. AWS Console → Route 53
2. Hosted zones → `stock-insight.app` 선택
3. 기존 `@` 레코드 확인

**Route 53는 Alias 레코드 지원:**
- **Type**: `A` 레코드 (Alias 활성화)
- **Name**: 비워두기 (루트 도메인)
- **Alias**: Yes
- **Alias target**: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
- **TTL**: 자동 설정

---

### 5. 네이버 클라우드 플랫폼

**네이버 클라우드 사용 시:**

1. 네이버 클라우드 콘솔 로그인
2. DNS Plus → `stock-insight.app` 선택
3. 레코드 관리

**네이버 클라우드는 CNAME 지원:**
- **레코드 유형**: `CNAME`
- **호스트**: `@`
- **값**: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
- **TTL**: 3600

---

## 일반적인 해결 절차

### 1단계: 현재 DNS 설정 확인

DNS 제공업체의 DNS 관리 페이지에서:
- `@` 또는 루트 도메인 레코드 확인
- 레코드 타입 확인 (CNAME? A? ALIAS?)
- 값 확인 (`transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`)

### 2단계: 레코드 타입 확인

**지원되는 레코드 타입:**
- ✅ **ALIAS/ANAME**: 루트 도메인에 사용 가능
- ✅ **CNAME**: 일부 DNS 제공업체만 루트 도메인 지원
- ❌ **A 레코드**: Heroku는 동적 IP 사용하므로 불가

### 3단계: 레코드 수정 또는 재생성

**ALIAS/ANAME 사용 가능한 경우:**
- 기존 레코드 삭제
- ALIAS/ANAME 레코드로 새로 생성

**CNAME만 사용 가능한 경우 (일부 제공업체):**
- Cloudflare로 DNS 변경 권장
- 또는 DNS 제공업체 문의

---

## 빠른 확인 방법

### 온라인 도구로 DNS 확인

1. **DNS 전파 확인:**
   - https://www.whatsmydns.net/#CNAME/stock-insight.app
   - 여러 지역에서 확인되는지 확인

2. **DNS 레코드 확인:**
   - https://mxtoolbox.com/SuperLookup.aspx
   - 도메인: `stock-insight.app`
   - CNAME 레코드 확인

---

## Cloudflare로 DNS 변경 (권장 해결책)

### 장점

1. ✅ 루트 도메인에 CNAME 지원
2. ✅ 무료
3. ✅ 빠른 DNS 전파
4. ✅ 추가 보안 기능

### 변경 절차

1. **Cloudflare 가입**
   - https://dash.cloudflare.com/sign-up

2. **사이트 추가**
   - "Add a Site" 클릭
   - `stock-insight.app` 입력

3. **DNS 레코드 추가**
   - DNS → Records
   - CNAME 레코드 추가:
     - Name: `@`
     - Target: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
     - Proxy: 🟠 DNS only (Gray cloud)
   - CNAME 레코드 추가 (www):
     - Name: `www`
     - Target: `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`
     - Proxy: 🟠 DNS only (Gray cloud)

4. **네임서버 변경**
   - Cloudflare에서 제공하는 네임서버 확인
   - 도메인 등록업체에서 네임서버 변경

---

## DNS 전파 대기

DNS 변경 후:
- **빠른 경우**: 10분 ~ 1시간
- **일반적인 경우**: 1 ~ 6시간
- **느린 경우**: 24 ~ 48시간

**확인 방법:**
```
https://www.whatsmydns.net/#CNAME/stock-insight.app
```

---

## 확인 체크리스트

- [ ] DNS 제공업체 확인
- [ ] 루트 도메인(`@`) 레코드 타입 확인
- [ ] ALIAS/ANAME 레코드 사용 가능 여부 확인
- [ ] 레코드 수정 또는 재생성
- [ ] DNS 전파 확인 (whatsmydns.net)
- [ ] 브라우저에서 `https://stock-insight.app` 접속 확인

---

**가장 빠른 해결책: DNS 제공업체에서 루트 도메인 레코드를 ALIAS/ANAME로 변경하거나, Cloudflare로 DNS를 변경하는 것입니다!**

