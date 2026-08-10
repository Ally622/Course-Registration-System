#!/usr/bin/env python3
"""Quick endpoint test"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(endpoint):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        print(f"{endpoint}: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', False)}")
            if 'schools' in data:
                print(f"  Schools count: {len(data['schools'])}")
            elif 'programmes' in data:
                print(f"  Programmes count: {len(data['programmes'])}")
        else:
            print(f"  Error: {response.text[:100]}")
        print()
    except Exception as e:
        print(f"{endpoint}: ERROR - {e}")
        print()

# Test critical endpoints
print("Testing Critical Public Endpoints:")
print("=" * 40)

test_endpoint("/api/health")
test_endpoint("/api/public/schools")
test_endpoint("/api/public/programmes")

# Test new admin endpoints
print("Testing New Admin Endpoints (expect 401):")
print("=" * 40)
test_endpoint("/admin/announcements")
test_endpoint("/admin/export/students/pdf")
test_endpoint("/registration/history")