# DNS 설정 가이드 - stock-insight.app (구체적 가이드)

## ✅ Heroku에서 확인한 DNS Target 값

```
www.stock-insight.app → fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com
stock-insight.app → transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com
```

---

## 📝 DNS 제공업체에 입력할 값

### 레코드 1: 루트 도메인 (stock-insight.app)

| 항목 | 입력값 |
|------|--------|
| **타입** | `CNAME` |
| **호스트/이름** | `@` (또는 비워두기) |
| **값/Target** | `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com` |
| **TTL** | `3600` (또는 기본값) |

### 레코드 2: www 서브도메인 (www.stock-insight.app)

| 항목 | 입력값 |
|------|--------|
| **타입** | `CNAME` |
| **호스트/이름** | `www` |
| **값/Target** | `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com` |
| **TTL** | `3600` (또는 기본값) |

---

## 🎯 주요 DNS 제공업체별 입력 방법

### **GoDaddy**

1. https://godaddy.com 로그인
2. **My Products** → `stock-insight.app` 도메인 클릭
3. **DNS** 탭 클릭
4. **Records** 섹션에서:

   **레코드 1 추가:**
   - **Add** 클릭
   - **Type**: `CNAME`
   - **Name**: `@` (또는 비워두기)
   - **Value**: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
   - **TTL**: `600 seconds`
   - **Save**

   **레코드 2 추가:**
   - **Add** 클릭
   - **Type**: `CNAME`
   - **Name**: `www`
   - **Value**: `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`
   - **TTL**: `600 seconds`
   - **Save**

### **Namecheap**

1. https://namecheap.com 로그인
2. **Domain List** → `stock-insight.app` → **Manage** 클릭
3. **Advanced DNS** 탭
4. **Host Records** 섹션:

   **레코드 1 추가:**
   - **Add New Record** 클릭
   - **Type**: `CNAME Record`
   - **Host**: `@`
   - **Value**: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
   - **TTL**: `Automatic`
   - ✓ (체크) 클릭

   **레코드 2 추가:**
   - **Add New Record** 클릭
   - **Type**: `CNAME Record`
   - **Host**: `www`
   - **Value**: `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`
   - **TTL**: `Automatic`
   - ✓ (체크) 클릭
   - **Save All Changes** 클릭

### **Cloudflare**

⚠️ **중요:** Cloudflare 사용 시 Proxy를 **비활성화**해야 합니다 (Gray cloud 🟠)

1. Cloudflare Dashboard 로그인
2. `stock-insight.app` 도메인 선택
3. **DNS** 탭
4. **Records**:

   **레코드 1 추가:**
   - **Add record** 클릭
   - **Type**: `CNAME`
   - **Name**: `@`
   - **Target**: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
   - **Proxy status**: 🟠 **DNS only** (Gray cloud) - **필수!**
   - **TTL**: `Auto`
   - **Save**

   **레코드 2 추가:**
   - **Add record** 클릭
   - **Type**: `CNAME`
   - **Name**: `www`
   - **Target**: `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`
   - **Proxy status**: 🟠 **DNS only** (Gray cloud) - **필수!**
   - **TTL**: `Auto`
   - **Save**

### **AWS Route 53**

1. AWS Console → Route 53
2. **Hosted zones** → `stock-insight.app` 선택
3. **Create record**:

   **레코드 1:**
   - **Record name**: 비워두기 (루트 도메인용)
   - **Record type**: `CNAME - Routes traffic to another domain name`
   - **Value**: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
   - **TTL**: `300`
   - **Create records**

   **레코드 2:**
   - **Create record** 클릭
   - **Record name**: `www`
   - **Record type**: `CNAME - Routes traffic to another domain name`
   - **Value**: `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`
   - **TTL**: `300`
   - **Create records**

### **네이버 클라우드 플랫폼**

1. 네이버 클라우드 콘솔 로그인
2. **DNS Plus** → `stock-insight.app` 선택
3. **레코드 관리**

   **레코드 1 추가:**
   - **레코드 추가** 클릭
   - **레코드 유형**: `CNAME`
   - **호스트**: `@` (또는 비워두기)
   - **값**: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
   - **TTL**: `3600`
   - **저장**

   **레코드 2 추가:**
   - **레코드 추가** 클릭
   - **레코드 유형**: `CNAME`
   - **호스트**: `www`
   - **값**: `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`
   - **TTL**: `3600`
   - **저장**

---

## ✅ 설정 완료 후 확인

### 1. DNS 전파 확인 (24-48시간 소요 가능)

온라인 도구 사용:
- https://www.whatsmydns.net/#CNAME/stock-insight.app
- https://dnschecker.org/#CNAME/stock-insight.app

**확인할 값:**
- `stock-insight.app` → `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
- `www.stock-insight.app` → `fast-marten-w0ntx5lmj4ir9jlmyj65hgpz.herokudns.com`

### 2. 브라우저에서 직접 접속 테스트

설정 후 10분~1시간 정도 기다린 후:

```
https://stock-insight.app
https://www.stock-insight.app
```

**정상 작동 시:**
- ✅ HTTPS로 접속됨
- ✅ 브라우저 주소창에 자물쇠 🔒 아이콘 표시
- ✅ 사이트가 정상적으로 로드됨

### 3. SSL 인증서 확인

Heroku는 자동으로 SSL 인증서를 발급합니다 (1-10분 소요).

**Heroku Dashboard에서 확인:**
- Settings → SSL Certificate
- "Automatic Certificate Management (ACM)" 활성화 확인

---

## 🚨 주의사항

1. **기존 레코드 확인**
   - 기존에 `@` 또는 `www`에 대한 A 레코드나 CNAME 레코드가 있다면 **삭제**하거나 **수정**하세요.
   - 같은 호스트에 여러 레코드가 있으면 충돌이 발생할 수 있습니다.

2. **Cloudflare 사용 시**
   - 반드시 Proxy를 **비활성화** (Gray cloud 🟠)해야 합니다.
   - Orange cloud (Proxy 활성화) 상태에서는 작동하지 않습니다.

3. **DNS 전파 대기**
   - DNS 변경 사항이 전 세계에 전파되는 데 **24-48시간**이 걸릴 수 있습니다.
   - 빠른 경우 10분~1시간 내에 작동할 수도 있습니다.

---

## 📞 문제 해결

### "DNS_PROBE_FINISHED_NXDOMAIN" 오류

- DNS 레코드가 아직 전파되지 않았을 수 있습니다.
- 24-48시간 대기 또는 다른 DNS 체커로 확인

### SSL 인증서 오류

- Heroku에서 SSL 인증서 발급 대기 (1-10분)
- Heroku Dashboard → Settings → SSL Certificate 확인

### "Too many redirects" 오류

- Cloudflare 사용 시 Proxy 비활성화 확인
- DNS 레코드 타입 확인 (CNAME이어야 함)

---

**설정 완료 후 위 URL로 접속하여 정상 작동하는지 확인하세요!**

