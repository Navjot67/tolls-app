#!/usr/bin/env python3
"""Quick test script for NJ automation"""
from automation_selenium_nj import extract_toll_info_nj
import json

print("Testing NJ E-ZPass automation...")
print("=" * 60)

result = extract_toll_info_nj(
    violation_number="T13255735180201",
    plate_number="T127211C",
    headless=False
)

print("\n" + "=" * 60)
print("RESULT:")
print("=" * 60)
print(json.dumps(result, indent=2))




