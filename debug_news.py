import os
import time
from datetime import datetime
import news_manager
import json

NEWS_DATA_FILE = "static/news_data.json"

def check_file_status():
    if os.path.exists(NEWS_DATA_FILE):
        mod_time = os.path.getmtime(NEWS_DATA_FILE)
        dt = datetime.fromtimestamp(mod_time)
        now = datetime.now()
        diff = now - dt
        print(f"File exists. Last modified: {dt}")
        print(f"Time since modification: {diff}")
        
        # Read content to check titles
        with open(NEWS_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                print(f"First article title: {data[0].get('title')}")
            else:
                print("File is empty or invalid JSON")
    else:
        print("File does not exist")

def test_fetch():
    print("\n--- Testing Fetch ---")
    # We will try to fetch without overwriting the actual file for now, or just let it overwrite since we are debugging
    # But news_manager writes to file. Let's backup the file first.
    
    if os.path.exists(NEWS_DATA_FILE):
        os.rename(NEWS_DATA_FILE, NEWS_DATA_FILE + ".bak")
        
    try:
        # Force fetch by ensuring file doesn't exist (we renamed it)
        news_manager.fetch_and_process_news()
        
        # Check result
        if os.path.exists(NEWS_DATA_FILE):
            print("Fetch completed. New file created.")
            with open(NEWS_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Fetched {len(data)} items.")
                if data:
                     print(f"New article title: {data[0].get('title')}")
        else:
            print("Fetch function ran but file was not created.")
            
    except Exception as e:
        print(f"Error during fetch test: {e}")
        
    # Restore backup
    if os.path.exists(NEWS_DATA_FILE + ".bak"):
        # If new file exists, maybe keep it? No, let's restore for safety unless current is better
        if os.path.exists(NEWS_DATA_FILE):
            os.remove(NEWS_DATA_FILE)
        os.rename(NEWS_DATA_FILE + ".bak", NEWS_DATA_FILE)

if __name__ == "__main__":
    check_file_status()
    # Check if OPENAI_API_KEY is present
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set.")
    else:
        print("OPENAI_API_KEY is set.")
        
    test_fetch()
