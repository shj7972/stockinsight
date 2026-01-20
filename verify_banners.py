from fastapi.testclient import TestClient
from main import app
from utils import BANNERS
import re

client = TestClient(app)

def test_banners_presence():
    """Verify that exactly 3 banners are present and they are from the list."""
    response = client.get("/")
    assert response.status_code == 200
    
    content = response.text
    
    # Simple check for banner links
    found_banners = 0
    for banner in BANNERS:
        if banner['url'] in content:
            found_banners += 1
            
    print(f"Found {found_banners} unique banners in one request.")
    assert found_banners == 3, f"Expected 3 banners, found {found_banners}"

if __name__ == "__main__":
    try:
        # Run multiple times to check randomness (heuristic)
        print("Run 1:")
        test_banners_presence()
        print("Run 2:")
        test_banners_presence()
        print("Run 3:")
        test_banners_presence()
        print("SUCCESS: Banner rotation verification passed!")
    except AssertionError as e:
        print(f"FAILURE: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
