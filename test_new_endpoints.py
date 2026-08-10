#!/usr/bin/env python3
"""Test the new endpoints I added"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint_exists(endpoint):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        print(f"{endpoint}: Status {response.status_code}")
        if response.status_code == 401:
            print("  ✅ Endpoint exists (requires auth)")
        elif response.status_code == 404:
            print("  ❌ Endpoint NOT FOUND")
        elif response.status_code == 200:
            print("  ✅ Endpoint works (no auth required)")
        else:
            print(f"  ⚠️  Unexpected status: {response.status_code}")
        print()
    except Exception as e:
        print(f"{endpoint}: ERROR - {e}")
        print()

print("Testing NEW Admin Endpoints I Added:")
print("=" * 50)

# Announcements CRUD
test_endpoint_exists("/admin/announcements")

# Export endpoints  
test_endpoint_exists("/admin/export/students/pdf")
test_endpoint_exists("/admin/export/students/excel") 
test_endpoint_exists("/admin/export/registrations/pdf")
test_endpoint_exists("/admin/export/registrations/excel")

# Registration history
test_endpoint_exists("/registration/history")

print("All endpoints should return 401 (auth required) - this means they exist!")