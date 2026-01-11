# Heroku SSL 인증서 설정 가이드

## 🎯 ACM vs Manual 선택

### ✅ ACM (Automatic Certificate Management) - **권장!**

**ACM을 선택해야 하는 이유:**
- ✅ **자동 인증서 발급**: Let's Encrypt 인증서를 자동으로 발급
- ✅ **자동 갱신**: 인증서 만료 전 자동으로 갱신
- ✅ **무료**: 완전 무료
- ✅ **간편함**: 한 번 설정하면 관리 불필요
- ✅ **.app 도메인 최적**: HTTPS 필수 도메인에 완벽

**ACM 선택 시:**
1. Heroku Dashboard → Settings → SSL Certificate
2. **"Enable Automatic Certificate Management"** 또는 **"ACM"** 선택
3. Save

**설정 후:**
- Heroku가 DNS 전파를 확인하고 자동으로 SSL 인증서 발급
- 발급까지 보통 1-10분 소요
- 인증서는 90일마다 자동 갱신

---

### ⚠️ Manual (수동 설정) - 비권장

**Manual을 선택해야 하는 경우:**
- 회사 내부 인증서 사용 (예: 내부 CA)
- 특정 인증기관(CA)의 인증서 필요
- 고급 SSL 설정 필요

**Manual의 단점:**
- ❌ **비용**: 일부 고급 인증서는 유료
- ❌ **수동 갱신**: 만료 전 수동으로 갱신해야 함
- ❌ **복잡함**: 인증서 파일 직접 관리 필요

**.app 도메인 사용 시:**
- Manual은 권장하지 않습니다
- ACM이 더 간단하고 자동화되어 있습니다

---

## 📋 ACM 설정 단계별 가이드

### 방법 1: Heroku Dashboard에서 설정

1. **Heroku Dashboard 접속**
   - https://dashboard.heroku.com
   - 배포된 앱 선택

2. **Settings 탭 클릭**
   - 좌측 메뉴에서 "Settings" 선택

3. **Domains 섹션 확인**
   - `stock-insight.app` 도메인이 추가되어 있는지 확인
   - DNS Target 값 확인

4. **SSL Certificate 섹션 찾기**
   - Settings 페이지 스크롤
   - "SSL Certificate" 또는 "Certificates" 섹션

5. **ACM 활성화**
   - "Automatic Certificate Management" 또는 "ACM" 옵션 선택
   - 또는 "Enable ACM" 버튼 클릭
   - "Save" 또는 "Enable" 클릭

6. **상태 확인**
   - "Pending" → "Requesting" → "Cert Issued" 순서로 변경됨
   - 발급 완료까지 1-10분 소요

---

### 방법 2: Heroku CLI로 설정

```bash
# 1. ACM 활성화
heroku certs:auto:enable -a <your-app-name>

# 2. 상태 확인
heroku certs:auto -a <your-app-name>

# 3. SSL 인증서 목록 확인
heroku certs -a <your-app-name>
```

**예시:**
```bash
# 앱 이름이 stock-insight-app인 경우
heroku certs:auto:enable -a stock-insight-app
heroku certs:auto -a stock-insight-app
```

---

## ✅ ACM 설정 후 확인 방법

### 1. Heroku Dashboard에서 확인

**Settings → SSL Certificate** 섹션에서:
- ✅ **"Automatic Certificate Management"**: Enabled
- ✅ **상태**: "Cert Issued" 또는 "Cert Active"
- ✅ **Common Name**: `stock-insight.app`
- ✅ **Expires**: 90일 후 (자동 갱신)

### 2. 브라우저에서 확인

설정 후 1-10분 후:
1. 브라우저에서 `https://stock-insight.app` 접속
2. 주소창에 **자물쇠 🔒 아이콘** 표시 확인
3. 자물쇠 아이콘 클릭 → "Connection is secure" 확인

### 3. 온라인 도구로 확인

- https://www.ssllabs.com/ssltest/analyze.html?d=stock-insight.app
- SSL 인증서 정보 확인

---

## ⏰ 예상 소요 시간

### ACM 활성화 후:
- **1-10분**: SSL 인증서 발급 완료
- **최대 1시간**: 드문 경우

### 상태 변화:
```
ACM Enabled → Pending → Requesting → Cert Issued
```

---

## 🚨 문제 해결

### 문제 1: "ACM cannot be enabled" 오류

**원인:**
- DNS가 아직 전파되지 않음
- DNS 설정 오류

**해결:**
1. DNS 전파 확인: https://www.whatsmydns.net/#CNAME/stock-insight.app
2. DNS 설정 재확인
3. 1-2시간 대기 후 다시 시도

### 문제 2: "Pending" 상태에서 진행 안 됨

**원인:**
- DNS 전파가 완전히 완료되지 않음
- Heroku가 DNS를 확인할 수 없음

**해결:**
1. DNS 전파 확인 (여러 지역에서 확인)
2. 1-2시간 대기
3. Heroku Dashboard에서 "Refresh" 또는 "Retry" 클릭
4. 필요시 Heroku CLI로 강제 갱신:
   ```bash
   heroku certs:auto:refresh -a <your-app-name>
   ```

### 문제 3: "Cert Issued"인데 접속 안 됨

**해결:**
1. 브라우저 캐시 삭제
2. 시크릿/프라이빗 모드로 접속 테스트
3. 로컬 DNS 캐시 삭제 (Windows):
   ```powershell
   ipconfig /flushdns
   ```
4. 10-15분 후 다시 시도 (DNS 캐시 전파 시간)

---

## 📝 요약

### ✅ .app 도메인 사용 시 권장 설정:

1. **ACM (Automatic Certificate Management) 선택** ⭐
2. Heroku Dashboard → Settings → SSL Certificate
3. "Enable Automatic Certificate Management" 클릭
4. 1-10분 대기 (SSL 인증서 자동 발급)
5. `https://stock-insight.app` 접속 확인

### 🎯 ACM의 장점:
- ✅ 완전 자동화 (발급 + 갱신)
- ✅ 무료
- ✅ 간편함
- ✅ .app 도메인에 최적화

---

## 💡 추가 팁

### SSL 인증서 갱신 확인:
```bash
# 인증서 만료일 확인
heroku certs -a <your-app-name>
```

### 수동 갱신 (필요시):
```bash
# ACM이 자동 갱신하지만, 필요시 수동 트리거
heroku certs:auto:refresh -a <your-app-name>
```

### 도메인별 인증서 확인:
```bash
# 모든 도메인과 인증서 확인
heroku domains -a <your-app-name>
heroku certs -a <your-app-name>
```

---

**결론: `.app` 도메인 사용 시 ACM을 선택하는 것이 가장 좋습니다!**

