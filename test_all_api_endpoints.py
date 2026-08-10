"""
API Endpoint Test Script
Tests all API endpoints to verify they return proper data
Run Flask server first: python app.py
Then run this: python test_all_api_endpoints.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def test_endpoint(method, endpoint, expected_status=200, auth_required=False, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json={})
        else:
            response = requests.request(method, url)
        
        status_match = response.status_code == expected_status
        
        # Check if response is JSON
        is_json = False
        try:
            data = response.json()
            is_json = True
        except:
            data = None
        
        # Result
        if status_match and is_json:
            status_icon = f"{Colors.GREEN}✅{Colors.END}"
            status_text = f"{Colors.GREEN}{response.status_code}{Colors.END}"
        elif auth_required and response.status_code == 401:
            status_icon = f"{Colors.YELLOW}🔒{Colors.END}"
            status_text = f"{Colors.YELLOW}401 (Auth Required){Colors.END}"
        else:
            status_icon = f"{Colors.RED}❌{Colors.END}"
            status_text = f"{Colors.RED}{response.status_code}{Colors.END}"
        
        print(f"{status_icon} {method:6} {endpoint:50} {status_text}")
        
        if data and 'success' in data:
            if not data['success']:
                print(f"      └─ Error: {data.get('message', 'Unknown')}")
        
        return {
            'endpoint': endpoint,
            'status': response.status_code,
            'is_json': is_json,
            'success': status_match
        }
        
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌{Colors.END} {method:6} {endpoint:50} {Colors.RED}CONNECTION FAILED{Colors.END}")
        return {'endpoint': endpoint, 'status': 0, 'is_json': False, 'success': False}
    except Exception as e:
        print(f"{Colors.RED}❌{Colors.END} {method:6} {endpoint:50} {Colors.RED}ERROR: {str(e)}{Colors.END}")
        return {'endpoint': endpoint, 'status': 0, 'is_json': False, 'success': False}

def main():
    print("="*80)
    print(f"{Colors.BLUE}API ENDPOINT TEST SUITE{Colors.END}")
    print("="*80)
    
    results = []
    
    # PUBLIC ENDPOINTS (No Auth Required)
    print(f"\n{Colors.BLUE}═══ PUBLIC API ENDPOINTS (No Authentication) ═══{Colors.END}")
    results.append(test_endpoint("GET", "/api/health", 200, description="Health check"))
    results.append(test_endpoint("GET", "/api/public/schools", 200, description="List all schools"))
    results.append(test_endpoint("GET", "/api/public/schools/1/departments", 200, description="Departments by school"))
    results.append(test_endpoint("GET", "/api/public/departments/1/programmes", 200, description="Programmes by department"))
    results.append(test_endpoint("GET", "/api/public/programmes", 200, description="All programmes"))
    results.append(test_endpoint("GET", "/api/public/courses", 200, description="All courses"))
    
    # AUTH ENDPOINTS
    print(f"\n{Colors.BLUE}═══ AUTHENTICATION ENDPOINTS ═══{Colors.END}")
    results.append(test_endpoint("GET", "/auth/me", 401, True, description="Check session"))
    results.append(test_endpoint("POST", "/auth/login", 400, description="Login (bad request without data)"))
    results.append(test_endpoint("POST", "/auth/register", 400, description="Register (bad request without data)"))
    results.append(test_endpoint("POST", "/auth/logout", 200, description="Logout"))
    
    # STUDENT ENDPOINTS (Require Auth)
    print(f"\n{Colors.BLUE}═══ STUDENT ENDPOINTS (Require Authentication) ═══{Colors.END}")
    results.append(test_endpoint("GET", "/student/dashboard", 401, True, description="Student dashboard"))
    results.append(test_endpoint("GET", "/student/profile", 401, True, description="Student profile"))
    results.append(test_endpoint("GET", "/student/results", 401, True, description="Student results"))
    results.append(test_endpoint("GET", "/student/timetable", 401, True, description="Student timetable"))
    results.append(test_endpoint("GET", "/student/notifications", 401, True, description="Student notifications"))
    
    # REGISTRATION ENDPOINTS (Require Auth)
    print(f"\n{Colors.BLUE}═══ COURSE REGISTRATION ENDPOINTS (Require Authentication) ═══{Colors.END}")
    results.append(test_endpoint("GET", "/registration/courses", 401, True, description="Available courses"))
    results.append(test_endpoint("GET", "/registration/my-courses", 401, True, description="My registered courses"))
    
    # ADMISSION ENDPOINTS (Require Auth)
    print(f"\n{Colors.BLUE}═══ ADMISSION ENDPOINTS (Require Authentication) ═══{Colors.END}")
    results.append(test_endpoint("GET", "/admission/status", 401, True, description="Admission status"))
    results.append(test_endpoint("GET", "/admission/academic-info", 401, True, description="Academic info"))
    results.append(test_endpoint("GET", "/admission/kcse-grades", 401, True, description="KCSE grades"))
    results.append(test_endpoint("GET", "/admission/programmes", 401, True, description="Programmes for admission"))
    
    # ADMIN ENDPOINTS (Require Admin Auth)
    print(f"\n{Colors.BLUE}═══ ADMIN ENDPOINTS (Require Admin Authentication) ═══{Colors.END}")
    results.append(test_endpoint("GET", "/admin/dashboard", 401, True, description="Admin dashboard"))
    results.append(test_endpoint("GET", "/admin/students", 401, True, description="List students"))
    results.append(test_endpoint("GET", "/admin/schools", 401, True, description="List schools"))
    results.append(test_endpoint("GET", "/admin/departments", 401, True, description="List departments"))
    results.append(test_endpoint("GET", "/admin/courses", 401, True, description="List courses"))
    results.append(test_endpoint("GET", "/admin/lecturers", 401, True, description="List lecturers"))
    results.append(test_endpoint("GET", "/admin/semesters", 401, True, description="List semesters"))
    results.append(test_endpoint("GET", "/admin/applications", 401, True, description="List applications"))
    results.append(test_endpoint("GET", "/admin/registrations", 401, True, description="List registrations"))
    
    # SUMMARY
    print("\n" + "="*80)
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed
    
    print(f"Total Endpoints Tested: {total}")
    print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}❌ Failed: {failed}{Colors.END}")
    
    # Check critical endpoints
    print(f"\n{Colors.BLUE}CRITICAL PUBLIC ENDPOINTS:{Colors.END}")
    critical = [
        '/api/public/schools',
        '/api/public/programmes',
        '/api/public/courses'
    ]
    
    for endpoint in critical:
        result = next((r for r in results if r['endpoint'] == endpoint), None)
        if result:
            if result['status'] == 200 and result['is_json']:
                print(f"  {Colors.GREEN}✅{Colors.END} {endpoint}")
            else:
                print(f"  {Colors.RED}❌{Colors.END} {endpoint} - Status: {result['status']}")
    
    print("\n" + "="*80)
    
    if failed == 0:
        print(f"{Colors.GREEN}✅ ALL TESTS PASSED!{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  Some endpoints failed. Check details above.{Colors.END}")
    
    print("="*80)

if __name__ == "__main__":
    print("\n⚠️  Make sure Flask server is running: python app.py")
    print("Press Enter to continue...")
    input()
    main()
