"""
Production Readiness Test Suite
Tests core API functionality including authentication, event ingestion, and retrieval
"""
import requests
import time
import hmac
import hashlib
import json
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/v1"
HEALTH_URL = "http://localhost:8000/health"

# Test credentials - will be created dynamically
TEST_EMAIL = f"test{int(time.time())}@example.com"
TEST_PASSWORD = "TestPass123"
ACCESS_TOKEN = None
PROJECT_ID = None
API_KEY_ID = None
INGEST_SECRET = "local-super-secret"  # Must match settings.ingest_api_key_secret

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"{status} - {name}")
    if details and not passed:
        print(f"  {Colors.YELLOW}{details}{Colors.RESET}")

def test_health_check():
    """Test: Health Check"""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        passed = response.status_code == 200 and response.json().get("status") == "ok"
        print_test("Health Check", passed)
        return passed
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_user_registration():
    """Test: User Registration"""
    global ACCESS_TOKEN
    try:
        # Register new user
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        passed = response.status_code == 201
        print_test("User Registration", passed, response.text if not passed else "")
        
        if passed:
            # Login to get access token
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            if login_response.status_code == 200:
                ACCESS_TOKEN = login_response.json().get("access_token")
                print_test("User Login", True)
                return True
            else:
                print_test("User Login", False, login_response.text)
                return False
        return passed
    except Exception as e:
        print_test("User Registration", False, str(e))
        return False

def test_project_creation():
    """Test: Project Creation"""
    global PROJECT_ID, API_KEY_ID
    if not ACCESS_TOKEN:
        print_test("Project Creation", False, "No access token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.post(
            f"{BASE_URL}/projects",
            json={"name": "Test Project", "description": "Production readiness test project"},
            headers=headers
        )
        passed = response.status_code in [200, 201]
        if passed:
            data = response.json()
            # Response structure: {"project": {...}, "api_key_id": "...", "api_key_secret": "..."}
            project_data = data.get("project", {})
            PROJECT_ID = project_data.get("id") if isinstance(project_data, dict) else data.get("id")
            API_KEY_ID = data.get("api_key_id")
        print_test("Project Creation", passed, response.text if not passed else "")
        return passed
    except Exception as e:
        print_test("Project Creation", False, str(e))
        return False

def create_hmac_headers(body_dict: dict, endpoint: str):
    """Create HMAC authentication headers"""
    ts = str(int(time.time()))
    body_json = json.dumps(body_dict, separators=(',', ':'))
    body_bytes = body_json.encode('utf-8')
    
    msg = f"{ts}:POST:{endpoint}:{body_json}"
    sig = hmac.new(
        INGEST_SECRET.encode('utf-8'),
        msg.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return {
        "Content-Type": "application/json",
        "x-api-key-id": API_KEY_ID,
        "x-api-timestamp": ts,
        "x-api-signature": sig
    }, body_bytes

def test_event_ingestion():
    """Test: Event Ingestion with HMAC"""
    global PROJECT_ID, API_KEY_ID
    if not PROJECT_ID or not API_KEY_ID:
        print_test("Event Ingestion", False, f"No project - PROJECT_ID={PROJECT_ID}, API_KEY_ID={API_KEY_ID}")
        return False
    
    try:
        payload = {
            "project_id": PROJECT_ID,
            "events": [
                {
                    "name": "test_event",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "props": {"test": "value", "count": 1}
                }
            ]
        }
        
        headers, body_bytes = create_hmac_headers(payload, "/v1/events")
        
        response = requests.post(
            f"{BASE_URL}/events",
            data=body_bytes,
            headers=headers
        )
        passed = response.status_code in [200, 201]
        print_test("Event Ingestion (HMAC)", passed, response.text if not passed else "")
        return passed
    except Exception as e:
        print_test("Event Ingestion (HMAC)", False, str(e))
        return False

def test_batch_event_ingestion():
    """Test: Batch Event Ingestion"""
    if not PROJECT_ID or not API_KEY_ID:
        print_test("Batch Event Ingestion", False, "No project created")
        return False
    
    try:
        payload = {
            "project_id": PROJECT_ID,
            "events": [
                {"name": f"batch_event_{i}", "ts": datetime.now(timezone.utc).isoformat(), "props": {"index": i}}
                for i in range(5)
            ]
        }
        
        headers, body_bytes = create_hmac_headers(payload, "/v1/events")
        
        response = requests.post(
            f"{BASE_URL}/events",
            data=body_bytes,
            headers=headers
        )
        passed = response.status_code in [200, 201]
        print_test("Batch Event Ingestion", passed, response.text if not passed else "")
        return passed
    except Exception as e:
        print_test("Batch Event Ingestion", False, str(e))
        return False

def test_event_retrieval():
    """Test: Event Retrieval with JWT"""
    if not ACCESS_TOKEN or not PROJECT_ID:
        print_test("Event Retrieval", False, "No authentication or project")
        return False
    
    # Wait a moment for events to be processed
    time.sleep(1)
    
    try:
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(
            f"{BASE_URL}/events",
            params={"project_id": PROJECT_ID, "limit": 10},
            headers=headers
        )
        passed = response.status_code == 200
        if passed:
            events = response.json().get("events", [])
            print_test(f"Event Retrieval ({len(events)} events)", passed)
        else:
            print_test("Event Retrieval", passed, response.text)
        return passed
    except Exception as e:
        print_test("Event Retrieval", False, str(e))
        return False

def test_project_listing():
    """Test: List Projects"""
    if not ACCESS_TOKEN:
        print_test("Project Listing", False, "No access token")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(f"{BASE_URL}/projects", headers=headers)
        data = response.json()
        passed = response.status_code == 200 and ("items" in data or isinstance(data, list))
        print_test("Project Listing", passed)
        return passed
    except Exception as e:
        print_test("Project Listing", False, str(e))
        return False

def test_unicode_event():
    """Test: Unicode Support in Events"""
    if not PROJECT_ID or not API_KEY_ID:
        print_test("Unicode Event", False, "No project created")
        return False
    
    try:
        payload = {
            "project_id": PROJECT_ID,
            "events": [
                {
                    "name": "测试事件🎉",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "props": {"message": "Hello 世界", "emoji": "✅🚀"}
                }
            ]
        }
        
        headers, body_bytes = create_hmac_headers(payload, "/v1/events")
        
        response = requests.post(
            f"{BASE_URL}/events",
            data=body_bytes,
            headers=headers
        )
        passed = response.status_code in [200, 201]
        print_test("Unicode Event Support", passed, response.text if not passed else "")
        return passed
    except Exception as e:
        print_test("Unicode Event Support", False, str(e))
        return False

def test_invalid_auth():
    """Test: Invalid Authentication Rejection"""
    try:
        headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(
            f"{BASE_URL}/events",
            params={"project_id": "test"},
            headers=headers
        )
        passed = response.status_code == 401
        print_test("Invalid Auth Rejection", passed)
        return passed
    except Exception as e:
        print_test("Invalid Auth Rejection", False, str(e))
        return False

def test_validation():
    """Test: Input Validation"""
    if not ACCESS_TOKEN:
        print_test("Input Validation", False, "No access token")
        return False
    
    try:
        # Try to create project without name
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.post(
            f"{BASE_URL}/projects",
            json={"description": "No name provided"},
            headers=headers
        )
        passed = response.status_code == 422
        print_test("Input Validation (Missing Fields)", passed)
        return passed
    except Exception as e:
        print_test("Input Validation", False, str(e))
        return False

def run_all_tests():
    """Run all production readiness tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}PRODUCTION READINESS TEST SUITE{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    test_results = []
    
    print(f"{Colors.YELLOW}[1/10] Infrastructure{Colors.RESET}")
    test_results.append(test_health_check())
    print()
    
    print(f"{Colors.YELLOW}[2/10] Authentication - Registration & Login{Colors.RESET}")
    test_results.append(test_user_registration())
    print()
    
    print(f"{Colors.YELLOW}[3/10] Project Management - Create{Colors.RESET}")
    test_results.append(test_project_creation())
    print()
    
    print(f"{Colors.YELLOW}[4/10] Event Ingestion - HMAC Auth{Colors.RESET}")
    test_results.append(test_event_ingestion())
    print()
    
    print(f"{Colors.YELLOW}[5/10] Batch Event Ingestion{Colors.RESET}")
    test_results.append(test_batch_event_ingestion())
    print()
    
    print(f"{Colors.YELLOW}[6/10] Unicode Support{Colors.RESET}")
    test_results.append(test_unicode_event())
    print()
    
    print(f"{Colors.YELLOW}[7/10] Event Retrieval - JWT Auth{Colors.RESET}")
    test_results.append(test_event_retrieval())
    print()
    
    print(f"{Colors.YELLOW}[8/10] Project Listing{Colors.RESET}")
    test_results.append(test_project_listing())
    print()
    
    print(f"{Colors.YELLOW}[9/10] Security - Invalid Auth{Colors.RESET}")
    test_results.append(test_invalid_auth())
    print()
    
    print(f"{Colors.YELLOW}[10/10] Input Validation{Colors.RESET}")
    test_results.append(test_validation())
    print()
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    percentage = (passed / total) * 100
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    if percentage == 100:
        print(f"{Colors.GREEN}✓ ALL TESTS PASSED!{Colors.RESET}")
    elif percentage >= 80:
        print(f"{Colors.YELLOW}⚠ MOSTLY PASSING{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ SOME TESTS FAILED{Colors.RESET}")
    
    print(f"\nPassed: {passed}/{total} ({percentage:.1f}%)")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    return percentage >= 80

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        exit(1)
