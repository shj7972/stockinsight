# 네이버 robots.txt 인식 문제 해결

## 문제 상황

네이버 사이트 진단 도구에서 "robots.txt가 존재하지 않습니다" 오류가 발생합니다.

## 가능한 원인

1. **경로 문제**: `/robots.txt` 경로가 정확히 매칭되지 않을 수 있음
2. **HTTP 상태 코드**: 200이 아닌 다른 코드를 반환할 수 있음
3. **Content-Type**: 네이버가 인식할 수 있는 Content-Type이 아닐 수 있음
4. **응답 헤더**: 필요한 헤더가 누락될 수 있음
5. **네이버 봇 접근**: 네이버 봇이 아직 접근하지 못했을 수 있음

## 해결 방법

### 확인 사항

1. **브라우저에서 직접 접속**
   ```
   https://stock-insight.app/robots.txt
   ```
   - 정상 작동 시: robots.txt 내용이 텍스트로 표시됨
   - 오류 시: 에러 메시지 확인

2. **HTTP 상태 코드 확인**
   - 정상: 200 OK
   - 오류: 404, 500 등

3. **Content-Type 확인**
   - 정상: `text/plain`
   - 오류: 다른 Content-Type

4. **네이버 사이트 진단 도구 재확인**
   - 설정 후 몇 분 ~ 몇 시간 대기 필요
   - 네이버 봇이 다시 크롤링할 때까지 시간 소요

## 추가 확인 사항

### 네이버 사이트 진단 도구 사용 방법

1. https://searchadvisor.naver.com 접속
2. 웹마스터 도구 → 사이트 진단
3. "robots.txt" 항목 클릭
4. "확인" 버튼 클릭
5. 결과 확인

### 온라인 도구로 확인

- https://www.google.com/webmasters/tools/robots-testing-tool
- URL: `https://stock-insight.app/robots.txt`

## 해결 단계

1. **브라우저에서 직접 접속 확인**
2. **HTTP 상태 코드 및 Content-Type 확인**
3. **네이버 사이트 진단 도구 재확인 (시간 대기)**
4. **문제가 계속되면 추가 조치**

