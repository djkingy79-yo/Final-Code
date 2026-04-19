#!/usr/bin/env python3
"""
Quick Backend Sanity Check for Appeal Case Manager
Testing only the 4 specific endpoints mentioned in the review request
"""

import requests
import sys

# Configuration
BASE_URL = "https://criminal-appeals-au-2.preview.emergentagent.com/api"
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"
CASE_ID = "case_76056187ad4f"

def test_backend_sanity():
    """Run the 4 specific backend sanity tests"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Backend-Sanity-Check/1.0'
    })
    
    results = []
    
    print("=" * 60)
    print("BACKEND SANITY CHECK - Appeal Case Manager")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Case ID: {CASE_ID}")
    print(f"Test Email: {TEST_EMAIL}")
    print("=" * 60)
    print()
    
    # Test 1: Auth Login
    print("1. Testing Auth Login...")
    try:
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = session.post(f"{BASE_URL}/auth/login", json=login_data, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if 'session_token' in data:
                auth_token = data['session_token']
                session.headers.update({
                    'Authorization': f'Bearer {auth_token}'
                })
                user_info = data.get('user', {})
                user_name = user_info.get('name', 'Unknown')
                print(f"   ✅ PASS - Authenticated as: {user_name}")
                results.append(("Auth Login", True, f"User: {user_name}"))
            else:
                print("   ❌ FAIL - No session_token in response")
                results.append(("Auth Login", False, "No session_token"))
                return results
        else:
            print(f"   ❌ FAIL - HTTP {response.status_code}: {response.text[:100]}")
            results.append(("Auth Login", False, f"HTTP {response.status_code}"))
            return results
            
    except Exception as e:
        print(f"   ❌ FAIL - Exception: {str(e)}")
        results.append(("Auth Login", False, f"Exception: {str(e)}"))
        return results
    
    # Test 2: GET /cases/case_76056187ad4f
    print("\n2. Testing GET Case Details...")
    try:
        response = session.get(f"{BASE_URL}/cases/{CASE_ID}", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            case_title = data.get('title', 'Unknown')
            print(f"   ✅ PASS - Case: {case_title}")
            results.append(("GET Case Details", True, f"Case: {case_title}"))
        else:
            print(f"   ❌ FAIL - HTTP {response.status_code}: {response.text[:100]}")
            results.append(("GET Case Details", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"   ❌ FAIL - Exception: {str(e)}")
        results.append(("GET Case Details", False, f"Exception: {str(e)}"))
    
    # Test 3: GET /cases/case_76056187ad4f/timeline
    print("\n3. Testing GET Case Timeline...")
    try:
        response = session.get(f"{BASE_URL}/cases/{CASE_ID}/timeline", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                event_count = len(data)
                print(f"   ✅ PASS - {event_count} timeline events")
                results.append(("GET Case Timeline", True, f"{event_count} events"))
            else:
                print("   ❌ FAIL - Response not a list")
                results.append(("GET Case Timeline", False, "Response not a list"))
        else:
            print(f"   ❌ FAIL - HTTP {response.status_code}: {response.text[:100]}")
            results.append(("GET Case Timeline", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"   ❌ FAIL - Exception: {str(e)}")
        results.append(("GET Case Timeline", False, f"Exception: {str(e)}"))
    
    # Test 4: GET /cases/case_76056187ad4f/grounds
    print("\n4. Testing GET Case Grounds...")
    try:
        response = session.get(f"{BASE_URL}/cases/{CASE_ID}/grounds", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'grounds' in data:
                grounds = data['grounds']
                if isinstance(grounds, list):
                    grounds_count = len(grounds)
                    print(f"   ✅ PASS - {grounds_count} grounds")
                    results.append(("GET Case Grounds", True, f"{grounds_count} grounds"))
                else:
                    print("   ❌ FAIL - 'grounds' key is not a list")
                    results.append(("GET Case Grounds", False, "'grounds' key is not a list"))
            elif isinstance(data, list):
                grounds_count = len(data)
                print(f"   ✅ PASS - {grounds_count} grounds (direct list)")
                results.append(("GET Case Grounds", True, f"{grounds_count} grounds"))
            else:
                print(f"   ❌ FAIL - Response format unexpected: {type(data)}")
                results.append(("GET Case Grounds", False, f"Unexpected format: {type(data)}"))
        else:
            print(f"   ❌ FAIL - HTTP {response.status_code}: {response.text[:100]}")
            results.append(("GET Case Grounds", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"   ❌ FAIL - Exception: {str(e)}")
        results.append(("GET Case Grounds", False, f"Exception: {str(e)}"))
    
    return results

def main():
    results = test_backend_sanity()
    
    # Summary
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, success, details in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name} - {details}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL BACKEND TESTS PASSED - No regression detected")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Backend regression detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())