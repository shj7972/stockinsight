import sys
import os

sys.path.append(os.getcwd())

print("Checking imports...")
try:
    from menus import dashboard
    print("menus.dashboard imported")
except Exception as e:
    print(f"menus.dashboard failed: {e}")

try:
    from menus import yield_calc
    print("menus.yield_calc imported")
except Exception as e:
    print(f"menus.yield_calc failed: {e}")

try:
    from menus import exchange
    print("menus.exchange imported")
except Exception as e:
    print(f"menus.exchange failed: {e}")

try:
    from menus import fear_greed
    print("menus.fear_greed imported")
except Exception as e:
    print(f"menus.fear_greed failed: {e}")

try:
    from menus import etf
    print("menus.etf imported")
except Exception as e:
    print(f"menus.etf failed: {e}")

print("Verification complete.")
