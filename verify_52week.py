import utils
import main

def test_format_price_short():
    print("Testing format_price_short...")
    
    # Test cases
    cases = [
        (15000, "005930.KS", "1.50만"),
        (58200, "005930.KS", "5.82만"),
        (1000, "005930.KS", "1,000"),
        (150.50, "AAPL", "$150.50"),
        (None, "AAPL", "N/A"),
        (1000000, "005930.KS", "100.00만"), # Check larger numbers
    ]
    
    for value, ticker, expected in cases:
        result = utils.format_price_short(value, ticker)
        print(f"Value: {value}, Ticker: {ticker} -> Result: {result}, Expected: {expected}")
        assert result == expected, f"Expected {expected}, got {result}"
        
    print("All format_price_short tests passed!")

if __name__ == "__main__":
    test_format_price_short()
