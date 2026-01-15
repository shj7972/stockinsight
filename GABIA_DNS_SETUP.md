# 가비아 DNS 설정 가이드 - stock-insight.app

## 📋 가비아 DNS 설정 방법

가비아에서 루트 도메인(`@`)을 Heroku에 연결하는 방법입니다.

---

## ⚠️ 중요한 사실: 가비아는 루트 도메인에 CNAME을 지원하지 않습니다

가비아의 특징:
- ❌ 루트 도메인(`@`)에 CNAME 레코드 사용 불가
- ❌ ALIAS/ANAME 레코드 지원하지 않음
- ✅ 서브도메인(www 등)에 CNAME 사용 가능

---

## 🔍 해결 방법

### 방법 1: Cloudflare 사용 (가장 권장!) ⭐

가비아는 루트 도메인에 CNAME/ALIAS를 지원하지 않으므로, **Cloudflare로 DNS를 변경**하는 것이 가장 좋은 방법입니다.

**Cloudflare 장점:**
- ✅ 루트 도메인에 CNAME 지원 (Cloudflare Flattening)
- ✅ 무료
- ✅ 빠른 DNS 전파
- ✅ 추가 보안 기능
- ✅ 가비아 도메인 등록 유지 가능

**절차:**

1. **Cloudflare 가입**
   - https://dash.cloudflare.com/sign-up
   - 무료 계정 생성

2. **사이트 추가**
   - "Add a Site" 클릭
   - `stock-insight.app` 입력
   - 무료 플랜 선택

3. **DNS 레코드 추가**
   - DNS → Records 클릭
   
   **레코드 1: 루트 도메인**
   - Type: `CNAME`
   - Name: `@`
   - Target: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
   - Proxy status: 🟠 **DNS only** (Gray cloud) - **중요!**
   - TTL: Auto
   - Save

   **레코드 2: www 서브도메인**
   - Type: `CNAME`
   - Name: `www`
   - Target: `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`
   - Proxy status: 🟠 **DNS only** (Gray cloud) - **중요!**
   - TTL: Auto
   - Save

4. **네임서버 변경**
   - Cloudflare에서 제공하는 네임서버 확인 (예: `alice.ns.cloudflare.com`, `bob.ns.cloudflare.com`)
   - 가비아 DNS 관리 페이지로 이동
   - 네임서버를 Cloudflare 네임서버로 변경
   - 변경 완료 후 24-48시간 대기 (빠른 경우 1-2시간)

---

### 방법 2: 가비아에서 www로만 접속 (임시 해결책)

가비아를 계속 사용하면서 www로만 접속하도록 설정:

**현재 상태:**
- ✅ `https://www.stock-insight.app` → 접속 정상
- ❌ `https://stock-insight.app` → 접속 안 됨

**해결책:**
- 루트 도메인은 접속하지 않고 www만 사용
- 또는 Heroku에서 루트 도메인을 www로 리다이렉트 설정 (고급 설정)

**권장하지 않음:**
- 사용자 경험 저하
- SEO 영향
- Cloudflare 사용을 권장

---

## 📝 가비아 DNS 설정 방법 (www 서브도메인)

가비아에서 www 서브도메인은 CNAME으로 설정 가능합니다.

### 1. 가비아 DNS 관리 페이지 접속

1. https://www.gabia.com 로그인
2. **"내 도메인"** → **"도메인 관리"** 클릭
3. `stock-insight.app` 도메인 선택
4. **"DNS 관리"** 또는 **"네임서버 관리"** 클릭

### 2. www 서브도메인 설정 (이미 완료된 것으로 보임)

**현재 설정:**
- Type: `CNAME`
- 호스트: `www`
- 값: `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`
- TTL: `3600`

---

## 🌐 Cloudflare로 변경하는 방법 (상세 가이드)

### 1단계: Cloudflare 가입 및 사이트 추가

1. **Cloudflare 가입**
   - https://dash.cloudflare.com/sign-up 접속
   - 이메일로 계정 생성

2. **사이트 추가**
   - "Add a Site" 클릭
   - `stock-insight.app` 입력
   - "Free" 플랜 선택 (무료)
   - "Continue" 클릭

3. **DNS 레코드 스캔**
   - Cloudflare가 기존 DNS 레코드를 자동으로 스캔
   - 확인 후 "Continue" 클릭

### 2단계: DNS 레코드 설정

1. **DNS 탭 클릭**

2. **기존 레코드 확인**
   - 기존 www CNAME 레코드가 있다면 확인
   - 필요시 수정

3. **루트 도메인 레코드 추가**
   - "Add record" 클릭
   - Type: `CNAME`
   - Name: `@`
   - Target: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
   - Proxy status: 🟠 **DNS only** (Gray cloud) - **반드시!**
   - TTL: Auto
   - "Save" 클릭

4. **www 서브도메인 레코드 확인/수정**
   - 기존 www 레코드가 있다면:
     - Target을 `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`로 확인/수정
     - Proxy status: 🟠 **DNS only** (Gray cloud)
   - 없다면 새로 추가:
     - Type: `CNAME`
     - Name: `www`
     - Target: `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`
     - Proxy status: 🟠 **DNS only** (Gray cloud)
     - TTL: Auto
     - "Save" 클릭

### 3단계: 네임서버 변경

1. **Cloudflare에서 네임서버 확인**
   - DNS 설정 후 "Continue" 클릭
   - 제공되는 네임서버 확인 (예):
     ```
     alice.ns.cloudflare.com
     bob.ns.cloudflare.com
     ```

2. **가비아에서 네임서버 변경**

   **방법 A: 가비아 웹사이트에서 변경**
   1. https://www.gabia.com 로그인
   2. **"내 도메인"** → **"도메인 관리"**
   3. `stock-insight.app` 선택
   4. **"네임서버 관리"** 또는 **"DNS 관리"** 클릭
   5. **"네임서버 변경"** 또는 **"Nameserver 변경"** 클릭
   6. Cloudflare에서 제공한 네임서버 입력:
      - 네임서버 1: `alice.ns.cloudflare.com` (예)
      - 네임서버 2: `bob.ns.cloudflare.com` (예)
   7. 저장

   **방법 B: 고객센터에 문의**
   - 가비아 고객센터: 1588-5824
   - Cloudflare 네임서버로 변경 요청

3. **네임서버 전파 대기**
   - 보통 1-24시간 소요
   - 빠른 경우 10분~1시간

### 4단계: Cloudflare에서 완료 확인

1. Cloudflare Dashboard로 돌아가기
2. "Done, check nameservers" 클릭
3. 네임서버 전파 확인
4. 전파 완료 후 "Check again" 클릭
5. "Activate" 클릭

---

## ✅ 설정 후 확인

### 1. DNS 전파 확인

온라인 도구로 확인:
- https://www.whatsmydns.net/#NS/stock-insight.app
- Cloudflare 네임서버로 변경되었는지 확인
- https://www.whatsmydns.net/#CNAME/stock-insight.app
- CNAME 레코드가 정상적으로 확인되는지 확인

### 2. 브라우저에서 접속 확인

네임서버 전파 완료 후 (1-24시간):
```
https://stock-insight.app
https://www.stock-insight.app
```

**정상 작동 시:**
- ✅ HTTPS로 접속됨
- ✅ 자물쇠 🔒 아이콘 표시
- ✅ 사이트가 정상적으로 로드됨

---

## ⚠️ 주의사항

### Cloudflare Proxy 설정

**중요:** Cloudflare에서 Proxy를 활성화하면 안 됩니다!

- ✅ **DNS only** (Gray cloud 🟠): 사용
- ❌ **Proxied** (Orange cloud 🟠): 사용하지 않음

**이유:**
- Heroku와 함께 사용할 때 Proxy를 활성화하면 작동하지 않을 수 있습니다
- DNS only를 사용하면 Cloudflare는 DNS만 처리하고 트래픽은 직접 Heroku로 전달됩니다

---

## 📞 가비아 고객센터 문의 (필요시)

네임서버 변경이 어려운 경우:
- **가비아 고객센터**: 1588-5824
- **이메일**: help@gabia.com
- **운영시간**: 평일 09:00~18:00

---

## 📋 설정 체크리스트

### Cloudflare 설정
- [ ] Cloudflare 가입 완료
- [ ] 사이트 추가 (`stock-insight.app`)
- [ ] 루트 도메인 CNAME 레코드 추가 (`@` → herokudns.com)
- [ ] www 서브도메인 CNAME 레코드 확인/수정
- [ ] Proxy status: DNS only (Gray cloud) 설정
- [ ] 네임서버 확인

### 가비아 설정
- [ ] 가비아 로그인
- [ ] 도메인 관리 페이지 접속
- [ ] 네임서버를 Cloudflare 네임서버로 변경
- [ ] 네임서버 변경 완료 확인

### 확인
- [ ] DNS 전파 확인 (whatsmydns.net)
- [ ] `https://stock-insight.app` 접속 확인
- [ ] `https://www.stock-insight.app` 접속 확인
- [ ] SSL 인증서 확인 (자물쇠 아이콘)

---

## 🎯 권장 순서

1. **Cloudflare 가입 및 DNS 설정** (5분)
2. **가비아에서 네임서버 변경** (5분)
3. **네임서버 전파 대기** (1-24시간)
4. **접속 확인**

---

**결론: 가비아는 루트 도메인에 CNAME/ALIAS를 지원하지 않으므로, Cloudflare로 DNS를 변경하는 것이 가장 좋은 해결책입니다!**

