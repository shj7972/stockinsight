import os
import news_manager
from dotenv import load_dotenv

# Load environment variables (for OpenAI API Key)
load_dotenv()

def main():
    print("Starting manual news update...")
    try:
        # Force update can be passed as argument if needed, 
        # but here we use the default 50-min logic unless news_data.json is missing.
        news_manager.update_news_now()
        print("News update process finished.")
    except Exception as e:
        print(f"CRITICAL ERROR during news update: {e}")

if __name__ == "__main__":
    main()
