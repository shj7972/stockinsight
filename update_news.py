import os
import news_manager
from dotenv import load_dotenv

# Load environment variables (for OpenAI API Key)
load_dotenv()

def main():
    print("Starting manual news update...")
    try:
        # Always force update in CI environment (GitHub Actions)
        # The freshness check doesn't work correctly in CI because
        # git checkout resets file modification times.
        news_manager.update_news_now(force=True)
        print("News update process finished.")
    except Exception as e:
        print(f"CRITICAL ERROR during news update: {e}")

if __name__ == "__main__":
    main()
