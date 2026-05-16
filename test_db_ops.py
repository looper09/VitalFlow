#!/usr/bin/env python3
"""Test database operations to diagnose the issue"""

from dotenv import load_dotenv
load_dotenv('.env')

from models_compat import (
    add_hospital, get_all_hospitals,
    add_item, get_all_items
)

print("=" * 60)
print("DATABASE OPERATION TEST")
print("=" * 60)

# Test Hospital
print("\n[TEST] add_hospital function:")
hospitals_before = get_all_hospitals()
count_before = len(hospitals_before) if hospitals_before else 0
print(f"  Hospitals before: {count_before}")

success, msg = add_hospital("Test Hospital ✓", "Test Zone", "+1-555-0000", "test_user")
print(f"  Result: success={success}, msg='{msg}'")

hospitals_after = get_all_hospitals()
count_after = len(hospitals_after) if hospitals_after else 0
print(f"  Hospitals after: {count_after}")
print(f"  Added: {count_after > count_before}")

if hospitals_after:
    print(f"  Last hospital: {hospitals_after[-1]}")

# Test Item
print("\n[TEST] add_item function:")
items_before = get_all_items()
count_before = len(items_before) if items_before else 0
print(f"  Items before: {count_before}")

success, msg = add_item("Test Equipment ✓", "Testing", "units", "test_user")
print(f"  Result: success={success}, msg='{msg}'")

items_after = get_all_items()
count_after = len(items_after) if items_after else 0
print(f"  Items after: {count_after}")
print(f"  Added: {count_after > count_before}")

if items_after:
    print(f"  Last item: {items_after[-1]}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
