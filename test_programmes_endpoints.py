"""
Test script for programmes endpoints.
Tests all three available endpoints for fetching programmes.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(endpoint, requires_auth=False):
    """Test a single endpoint"""
    print(f"\n{'='*70}")
    print(f"Testing: {endpoint}")
    print('='*70)
    
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"URL: {url}")
        
        headers = {"Content-Type": "application/json"}
        
        # Make request
        response = requests.get(url, headers=headers, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Not set')}")
        
        # Try to parse JSON
        try:
            data = response.json()
            print(f"Success: {data.get('success', 'N/A')}")
            
            if data.get('success'):
                if 'schools' in data:
                    schools = data['schools']
                    total = data.get('total_programmes', 'N/A')
                    print(f"Total Programmes: {total}")
                    print(f"Schools: {len(schools)}")
                    
                    # Show summary
                    for school in schools:
                        school_name = school.get('school_name', 'Unknown')
                        progs = school.get('programmes', [])
                        print(f"  - {school_name}: {len(progs)} programmes")
                        
                        # Show first 2 programmes
                        for i, prog in enumerate(progs[:2]):
                            print(f"    {i+1}. {prog.get('programme_name', 'N/A')}")
                            print(f"       Code: {prog.get('programme_code', 'N/A')}")
                            print(f"       Dept: {prog.get('department_name', 'N/A')}")
                        
                        if len(progs) > 2:
                            print(f"    ... and {len(progs)-2} more")
                    
                    print(f"\n✅ SUCCESS: Endpoint returned {total} programmes")
                elif 'programmes' in data:
                    progs = data['programmes']
                    print(f"Programmes: {len(progs)}")
                    print(f"✅ SUCCESS: Endpoint returned {len(progs)} programmes")
                else:
                    print(f"⚠️  Response structure unexpected")
                    print(f"Keys: {list(data.keys())}")
            else:
                message = data.get('message', 'No error message')
                print(f"❌ FAILED: {message}")
                
        except json.JSONDecodeError:
            print(f"❌ FAILED: Response is not JSON")
            print(f"Response text (first 200 chars): {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Cannot connect to {BASE_URL}")
        print(f"   Make sure Flask server is running!")
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT: Server took too long to respond")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


def main():
    print("\n" + "="*70)
    print("PROGRAMMES ENDPOINTS TEST SUITE")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print("\nTesting 3 endpoints:")
    print("  1. /api/programmes (Direct API endpoint)")
    print("  2. /api/public/programmes (Public API)")
    print("  3. /admission/programmes (Requires authentication)")
    
    # Test public endpoints
    test_endpoint("/api/programmes")
    test_endpoint("/api/public/programmes")
    
    # Test authenticated endpoint (will fail without login)
    print("\n" + "="*70)
    print("NOTE: /admission/programmes requires authentication")
    print("Testing without auth (expected to fail)...")
    print("="*70)
    test_endpoint("/admission/programmes", requires_auth=True)
    
    print("\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70)
    print("\nSummary:")
    print("  - /api/programmes should work (public)")
    print("  - /api/public/programmes should work (public)")
    print("  - /admission/programmes requires login (will return 401/403 or redirect)")
    print("\nIf any public endpoint fails, check:")
    print("  1. Is Flask server running? (python app.py)")
    print("  2. Is database connected?")
    print("  3. Does programmes table have data?")
    print("  4. Check Flask server logs for errors")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
