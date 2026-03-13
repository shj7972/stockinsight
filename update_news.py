import os
import news_manager
import indexing_service
from dotenv import load_dotenv
import sys

# Load environment variables (for OpenAI API Key)
load_dotenv()

def main():
    print("Starting manual news update...")
    try:
        # Always force update in CI environment (GitHub Actions)
        # The freshness check doesn't work correctly in CI because
        # git checkout resets file modification times.
        print("Calling news_manager.update_news_now(force=True)...")
        news_manager.update_news_now(force=True)
        print("News update process finished.")
        
        # Ping Google Indexing API to let it know daily report and home is updated
        print("Notifying Google Indexing API...")
        indexing_service.notify_google_indexing("https://stock-insight.app/")
        indexing_service.notify_google_indexing("https://stock-insight.app/daily-report")
        print("Indexing notification finished.")
    except Exception as e:
        print(f"CRITICAL ERROR during news update: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
