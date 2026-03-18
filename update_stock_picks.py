"""
update_stock_picks.py
---------------------
GitHub Actions에서 매일 오전 8시 KST에 실행되는 종목 발굴 업데이트 스크립트.
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

import stock_discovery_manager

if __name__ == "__main__":
    try:
        result = stock_discovery_manager.generate_daily_picks()
        us_count = len(result.get("us_picks", []))
        kr_count = len(result.get("kr_picks", []))
        print(f"[SUCCESS] {result['date']} — US {us_count}종목, KR {kr_count}종목 저장 완료")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] 종목 발굴 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
