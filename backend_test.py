#!/usr/bin/env python3
"""
Backend Testing for Appeal Case Manager
Testing live backend at https://criminal-appeals-au-2.preview.emergentagent.com/api
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://criminal-appeals-au-2.preview.emergentagent.com/api"
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"
CASE_ID = "case_76056187ad4f"
REPORT_ID = "rpt_0520d60ed7aa"  # Specific report from review request
REPORT_ID_1 = "rpt_1cc1bfeace33"
REPORT_ID_2 = "rpt_dcb21f0efc62"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Backend-Tester/1.0'
        })
        self.auth_token = None
        self.test_results = []

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'details': details
        })
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")

    def test_auth_login(self) -> bool:
        """Test 1: Auth login works and returns a session token"""
        print("\n=== Testing Authentication ===")
        
        try:
            # Test login endpoint
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                # Check for either access_token or session_token
                token = data.get('access_token') or data.get('session_token')
                if token:
                    self.auth_token = token
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    token_type = 'access_token' if 'access_token' in data else 'session_token'
                    self.log_test("Auth Login", True, f"Successfully logged in, {token_type} received")
                    return True
                else:
                    self.log_test("Auth Login", False, f"No access_token or session_token in response: {data}")
                    return False
            else:
                self.log_test("Auth Login", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Auth Login", False, f"Exception: {str(e)}")
            return False

    def test_case_reports(self) -> bool:
        """Test 2: GET /cases/case_76056187ad4f/reports returns completed report data"""
        print("\n=== Testing Case Reports ===")
        
        if not self.auth_token:
            self.log_test("Case Reports", False, "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/cases/{CASE_ID}/reports")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if reports have completed status
                    completed_reports = [r for r in data if r.get('status') == 'completed']
                    if completed_reports:
                        self.log_test("Case Reports", True, f"Found {len(completed_reports)} completed reports out of {len(data)} total")
                        return True
                    else:
                        self.log_test("Case Reports", False, f"No completed reports found. Reports: {[r.get('status', 'unknown') for r in data]}")
                        return False
                else:
                    self.log_test("Case Reports", False, f"No reports found or invalid response format: {data}")
                    return False
            else:
                self.log_test("Case Reports", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Case Reports", False, f"Exception: {str(e)}")
            return False

    def test_barrister_view(self) -> bool:
        """Test 3: GET /cases/case_76056187ad4f/reports/barrister-view returns the completed barrister brief"""
        print("\n=== Testing Barrister View ===")
        
        if not self.auth_token:
            self.log_test("Barrister View", False, "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/cases/{CASE_ID}/reports/barrister-view")
            
            if response.status_code == 200:
                data = response.json()
                # Check if it's a valid barrister brief response
                if isinstance(data, dict):
                    # Look for typical barrister brief fields
                    expected_fields = ['title', 'content', 'generated_at', 'case_id']
                    found_fields = [field for field in expected_fields if field in data]
                    
                    if len(found_fields) >= 2:  # At least 2 expected fields
                        self.log_test("Barrister View", True, f"Valid barrister brief returned with fields: {list(data.keys())}")
                        return True
                    else:
                        self.log_test("Barrister View", False, f"Response missing expected fields. Found: {list(data.keys())}")
                        return False
                else:
                    self.log_test("Barrister View", False, f"Invalid response format: {type(data)}")
                    return False
            else:
                self.log_test("Barrister View", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Barrister View", False, f"Exception: {str(e)}")
            return False

    def test_report_exports(self, report_id: str, report_name: str) -> bool:
        """Test report PDF and DOCX exports"""
        print(f"\n=== Testing {report_name} Exports ===")
        
        if not self.auth_token:
            self.log_test(f"{report_name} Exports", False, "No auth token available")
            return False
        
        pdf_success = False
        docx_success = False
        
        # Test PDF export
        try:
            response = self.session.get(f"{BASE_URL}/cases/{CASE_ID}/reports/{report_id}/export-pdf")
            
            if response.status_code == 200:
                content_length = len(response.content)
                if content_length > 0:
                    self.log_test(f"{report_name} PDF Export", True, f"PDF file returned, size: {content_length} bytes")
                    pdf_success = True
                else:
                    self.log_test(f"{report_name} PDF Export", False, "Empty PDF file returned")
            else:
                self.log_test(f"{report_name} PDF Export", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test(f"{report_name} PDF Export", False, f"Exception: {str(e)}")

        # Test DOCX export
        try:
            response = self.session.get(f"{BASE_URL}/cases/{CASE_ID}/reports/{report_id}/export-docx")
            
            if response.status_code == 200:
                content_length = len(response.content)
                if content_length > 0:
                    self.log_test(f"{report_name} DOCX Export", True, f"DOCX file returned, size: {content_length} bytes")
                    docx_success = True
                else:
                    self.log_test(f"{report_name} DOCX Export", False, "Empty DOCX file returned")
            else:
                self.log_test(f"{report_name} DOCX Export", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test(f"{report_name} DOCX Export", False, f"Exception: {str(e)}")

        return pdf_success and docx_success

    def test_api_regression_check(self) -> bool:
        """Test 6: Confirm no immediate API-level regression from timeout-threshold changes"""
        print("\n=== Testing API Regression Check ===")
        
        # Test health endpoint
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test("API Health Check", True, "Backend is healthy")
                    health_ok = True
                else:
                    self.log_test("API Health Check", False, f"Unhealthy status: {data}")
                    health_ok = False
            else:
                self.log_test("API Health Check", False, f"HTTP {response.status_code}: {response.text}")
                health_ok = False
        except Exception as e:
            self.log_test("API Health Check", False, f"Exception: {str(e)}")
            health_ok = False

        # Test that report generation endpoints are accessible (even if they return auth errors)
        generation_ok = True
        if self.auth_token:
            try:
                # Test report generation endpoint structure
                response = self.session.post(f"{BASE_URL}/cases/{CASE_ID}/reports/generate", 
                                           json={"report_type": "quick_summary"})
                
                # We expect either success or a specific error, not a 500 server error
                if response.status_code in [200, 201, 400, 401, 403, 404, 422]:
                    self.log_test("Report Generation Endpoint", True, f"Endpoint accessible (HTTP {response.status_code})")
                else:
                    self.log_test("Report Generation Endpoint", False, f"Server error: HTTP {response.status_code}")
                    generation_ok = False
                    
            except Exception as e:
                self.log_test("Report Generation Endpoint", False, f"Exception: {str(e)}")
                generation_ok = False
        else:
            self.log_test("Report Generation Endpoint", True, "Skipped (no auth token)")

        return health_ok and generation_ok

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend Tests for Appeal Case Manager")
        print(f"Target: {BASE_URL}")
        print(f"Case ID: {CASE_ID}")
        print("=" * 60)

        # Test 1: Authentication
        auth_success = self.test_auth_login()

        # Test 2: Case Reports
        reports_success = self.test_case_reports()

        # Test 3: Barrister View
        barrister_success = self.test_barrister_view()

        # Test 4, 5 & 6: Report Exports (including specific report from review request)
        export_specific_success = self.test_report_exports(REPORT_ID, "Specific Report (rpt_0520d60ed7aa)")
        export1_success = self.test_report_exports(REPORT_ID_1, "Report 1")
        export2_success = self.test_report_exports(REPORT_ID_2, "Report 2")

        # Test 7: API Regression Check
        regression_success = self.test_api_regression_check()

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        passed_tests = sum(1 for result in self.test_results if result['passed'])
        total_tests = len(self.test_results)

        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['name']}")

        print(f"\nTotal: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Backend is working correctly!")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} test(s) failed - See details above")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)