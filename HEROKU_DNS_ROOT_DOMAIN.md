# Heroku 루트 도메인 DNS 설정 - A 레코드 vs ALIAS/ANAME

## ⚠️ 중요한 사실: Heroku는 A 레코드를 지원하지 않습니다!

### 왜 A 레코드를 사용할 수 없나요?

1. **동적 IP 주소**
   - Heroku는 로드 밸런서를 사용합니다
   - IP 주소가 동적으로 변경됩니다
   - 여러 IP 주소를 사용합니다 (52.223.46.195, 3.33.193.101 등)

2. **A 레코드의 한계**
   - A 레코드는 고정 IP 주소만 사용 가능
   - IP가 변경되면 A 레코드를 수동으로 업데이트해야 함
   - 로드 밸런서 환경에서는 작동하지 않음

3. **Heroku의 권장 방법**
   - ✅ **CNAME** (서브도메인용)
   - ✅ **ALIAS/ANAME** (루트 도메인용)
   - ❌ **A 레코드** (지원하지 않음)

---

## 현재 확인된 IP 주소들

nslookup 결과에서 확인된 IP 주소들:
- `52.223.46.195`
- `3.33.193.101`
- `15.197.246.237`
- `99.83.183.127`

**⚠️ 이 IP 주소들은:**
- 로드 밸런서 IP 주소입니다
- 동적으로 변경될 수 있습니다
- A 레코드로 사용하면 안 됩니다

---

## 올바른 해결 방법

### 방법 1: ALIAS/ANAME 레코드 사용 (권장)

**DNS 제공업체에서:**
- Type: **ALIAS** 또는 **ANAME**
- Name: `@` (루트 도메인)
- Value: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
- TTL: 3600

**지원하는 DNS 제공업체:**
- ✅ Namecheap (ANAME)
- ✅ AWS Route 53 (Alias)
- ✅ DNSimple (ALIAS)
- ✅ Some.com (ANAME)

---

### 방법 2: Cloudflare 사용 (가장 권장!)

**Cloudflare의 장점:**
- ✅ 루트 도메인에 CNAME 지원 (Cloudflare Flattening)
- ✅ 무료
- ✅ 빠른 DNS 전파
- ✅ 추가 보안 기능

**설정:**
- Type: **CNAME**
- Name: `@`
- Target: `transparent-parakeet-zxdpwyqq4d7vu4hzd0wepwcn.herokudns.com`
- Proxy: 🟠 **DNS only** (Gray cloud)

---

### 방법 3: DNS 제공업체 확인

**현재 DNS 제공업체가 ALIAS/ANAME을 지원하는지 확인:**

1. DNS 관리 페이지 접속
2. 레코드 추가 페이지 확인
3. 레코드 타입 목록 확인
   - **ALIAS** 또는 **ANAME** 옵션이 있는지 확인
   - 있다면 → ALIAS/ANAME 사용
   - 없다면 → Cloudflare로 변경 권장

---

## 다른 Heroku 서비스에서 IP를 본 경우

### 가능한 시나리오들:

1. **잘못 본 경우**
   - herokudns.com을 가리키는 CNAME을 본 것일 수 있음
   - herokudns.com이 여러 IP로 해석되는 것을 본 것일 수 있음

2. **오래된 설정**
   - 예전에는 다를 수 있지만, 현재는 A 레코드를 지원하지 않음

3. **다른 플랫폼**
   - 다른 호스팅 서비스를 Heroku로 착각한 경우

---

## 확인 방법

### 1. 다른 Heroku 서비스 DNS 설정 확인

온라인 도구로 확인:
- https://mxtoolbox.com/SuperLookup.aspx
- 도메인 입력
- CNAME 레코드 확인

**예상 결과:**
- ✅ CNAME → `xxx.herokudns.com` (정상)
- ✅ ALIAS/ANAME → `xxx.herokudns.com` (정상)
- ❌ A 레코드 → 직접 IP 주소 (Heroku 서비스가 아님)

### 2. Heroku 공식 문서 확인

**Heroku 공식 문서:**
- https://devcenter.heroku.com/articles/custom-domains
- 루트 도메인은 **ALIAS 또는 ANAME** 사용 명시
- A 레코드는 언급되지 않음

---

## DNS 제공업체별 해결책

### ALIAS/ANAME 지원하는 경우

| 제공업체 | 레코드 타입 | 설정 방법 |
|---------|------------|----------|
| Namecheap | **ANAME** | Advanced DNS → ANAME Record |
| AWS Route 53 | **Alias** | A 레코드 (Alias 활성화) |
| DNSimple | **ALIAS** | ALIAS 레코드 추가 |
| Cloudflare | **CNAME** | CNAME 레코드 (자동 Flattening) |

### ALIAS/ANAME 지원하지 않는 경우

**해결책:**
1. **Cloudflare로 DNS 변경** (가장 권장!)
2. 또는 DNS 제공업체 문의

---

## 요약

### ❌ 사용할 수 없는 것:
- **A 레코드**: Heroku는 동적 IP를 사용하므로 지원하지 않음

### ✅ 사용해야 하는 것:
- **ALIAS/ANAME**: 루트 도메인용 (지원하는 경우)
- **CNAME**: 서브도메인용 (www)
- **Cloudflare CNAME**: 루트 도메인에 CNAME 사용 가능

---

## 결론

**Heroku는 A 레코드를 지원하지 않습니다.**

**해결 방법:**
1. DNS 제공업체에서 **ALIAS/ANAME** 레코드 사용
2. 또는 **Cloudflare**로 DNS 변경 (루트 도메인에 CNAME 지원)

**현재 DNS 제공업체가 무엇인가요?**
- ALIAS/ANAME을 지원한다면 → ALIAS/ANAME 레코드로 변경
- 지원하지 않는다면 → Cloudflare로 변경 권장

---

**다른 Heroku 서비스에서 본 것은 herokudns.com을 가리키는 CNAME/ALIAS이거나, herokudns.com이 해석되는 IP 주소일 가능성이 높습니다. A 레코드 자체는 Heroku에서 사용할 수 없습니다!**

