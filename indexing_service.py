import os
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 구글 서비스 계정 키 파일 경로 (보안상 .gitignore에 추가 필요)
CREDENTIALS_PATH = os.path.join(BASE_DIR, "google-credentials.json")

def notify_google_indexing(url: str, action_type="URL_UPDATED"):
    """
    Google Indexing API를 통해 특정 URL의 크롤링을 즉시 요청합니다.
    
    :param url: 요청할 웹페이지 도메인 전체 경로 (예: https://stock-insight.app/daily-report)
    :param action_type: "URL_UPDATED" (생성/업데이트) 또는 "URL_DELETED" (삭제)
    :return: (성공 여부 bool, 응답 메시지)
    """
    if not os.path.exists(CREDENTIALS_PATH):
        msg = f"Indexing API skipped: {CREDENTIALS_PATH} 파일을 찾을 수 없습니다."
        print(msg)
        return False, msg
        
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH, scopes=["https://www.googleapis.com/auth/indexing"]
        )
        
        session = AuthorizedSession(credentials)
        endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        
        response = session.post(
            endpoint,
            json={
                "url": url,
                "type": action_type
            }
        )
        
        if response.status_code == 200:
            msg = f"Indexing API success for {url}: {response.json()}"
            print(msg)
            return True, msg
        else:
            msg = f"Indexing API failed: {response.status_code} - {response.text}"
            print(msg)
            return False, msg
            
    except Exception as e:
        msg = f"Indexing API error: {e}"
        print(msg)
        return False, msg

if __name__ == "__main__":
    # 테스트용 단일 실행
    test_url = "https://stock-insight.app/daily-report"
    notify_google_indexing(test_url)
