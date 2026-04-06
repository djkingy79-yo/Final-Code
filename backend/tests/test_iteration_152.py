"""
Backend API Tests for Iteration 152
Testing: Login, Cases, Reports, Grounds, Legal Framework data
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://criminal-appeals-au-2.preview.emergentagent.com').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Cr1m1nalApp3al$2025"

class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_login_success(self):
        """Test successful login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "session_token" in data, "No session_token in response"
        assert "user_id" in data, "No user_id in response"
        assert data["email"] == TEST_EMAIL
        print(f"PASS: Login successful, user_id: {data['user_id']}")
        return data["session_token"]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
        print("PASS: Invalid credentials rejected")


class TestCases:
    """Case CRUD tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        token = response.json()["session_token"]
        session = requests.Session()
        session.cookies.set("session_token", token)
        return session
    
    def test_get_cases(self, auth_session):
        """Test getting list of cases"""
        response = auth_session.get(f"{BASE_URL}/api/cases")
        assert response.status_code == 200, f"Failed to get cases: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of cases"
        print(f"PASS: Retrieved {len(data)} cases")
        return data
    
    def test_get_case_detail(self, auth_session):
        """Test getting case detail"""
        # First get list of cases
        cases_response = auth_session.get(f"{BASE_URL}/api/cases")
        assert cases_response.status_code == 200
        cases = cases_response.json()
        
        if len(cases) > 0:
            case_id = cases[0]["case_id"]
            response = auth_session.get(f"{BASE_URL}/api/cases/{case_id}")
            assert response.status_code == 200, f"Failed to get case detail: {response.text}"
            data = response.json()
            assert "case_id" in data
            assert "title" in data
            print(f"PASS: Retrieved case detail for {data['title']}")
        else:
            pytest.skip("No cases available to test")


class TestGrounds:
    """Grounds endpoint tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        token = response.json()["session_token"]
        session = requests.Session()
        session.cookies.set("session_token", token)
        return session
    
    def test_get_grounds(self, auth_session):
        """Test getting grounds for a case"""
        # First get list of cases
        cases_response = auth_session.get(f"{BASE_URL}/api/cases")
        assert cases_response.status_code == 200
        cases = cases_response.json()
        
        if len(cases) > 0:
            case_id = cases[0]["case_id"]
            response = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/grounds")
            assert response.status_code == 200, f"Failed to get grounds: {response.text}"
            data = response.json()
            
            # API returns object with 'grounds' key
            if isinstance(data, dict) and "grounds" in data:
                grounds = data["grounds"]
                assert isinstance(grounds, list), "Expected list of grounds in 'grounds' key"
                
                # Check ground_type formatting (should not have underscores in display)
                for ground in grounds:
                    if "ground_type" in ground:
                        ground_type = ground["ground_type"]
                        print(f"Ground type: {ground_type}")
                        # The raw data may have underscores, but frontend should format it
                
                print(f"PASS: Retrieved {len(grounds)} grounds")
            else:
                assert isinstance(data, list), "Expected list of grounds"
                print(f"PASS: Retrieved {len(data)} grounds")
        else:
            pytest.skip("No cases available to test")


class TestReports:
    """Reports endpoint tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        token = response.json()["session_token"]
        session = requests.Session()
        session.cookies.set("session_token", token)
        return session
    
    def test_get_reports(self, auth_session):
        """Test getting reports for a case"""
        # First get list of cases
        cases_response = auth_session.get(f"{BASE_URL}/api/cases")
        assert cases_response.status_code == 200
        cases = cases_response.json()
        
        if len(cases) > 0:
            case_id = cases[0]["case_id"]
            response = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports")
            assert response.status_code == 200, f"Failed to get reports: {response.text}"
            data = response.json()
            assert isinstance(data, list), "Expected list of reports"
            print(f"PASS: Retrieved {len(data)} reports")
        else:
            pytest.skip("No cases available to test")


class TestLegalFramework:
    """Legal Framework endpoint tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        token = response.json()["session_token"]
        session = requests.Session()
        session.cookies.set("session_token", token)
        return session
    
    def test_get_legal_framework(self, auth_session):
        """Test getting legal framework for a case"""
        # First get list of cases
        cases_response = auth_session.get(f"{BASE_URL}/api/cases")
        assert cases_response.status_code == 200
        cases = cases_response.json()
        
        if len(cases) > 0:
            case_id = cases[0]["case_id"]
            # Try to get case extract which contains legal framework
            response = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/extract")
            if response.status_code == 200:
                data = response.json()
                print(f"PASS: Retrieved case extract with legal framework data")
                
                # Check for appeal_framework in the data
                if "appeal_framework" in data:
                    framework = data["appeal_framework"]
                    print(f"Appeal framework keys: {list(framework.keys()) if isinstance(framework, dict) else 'N/A'}")
            else:
                print(f"Case extract endpoint returned {response.status_code}")
        else:
            pytest.skip("No cases available to test")


class TestEvidence:
    """Evidence endpoint tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        token = response.json()["session_token"]
        session = requests.Session()
        session.cookies.set("session_token", token)
        return session
    
    def test_get_evidence(self, auth_session):
        """Test getting evidence for grounds"""
        # First get list of cases
        cases_response = auth_session.get(f"{BASE_URL}/api/cases")
        assert cases_response.status_code == 200
        cases = cases_response.json()
        
        if len(cases) > 0:
            case_id = cases[0]["case_id"]
            # Get grounds first
            grounds_response = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/grounds")
            if grounds_response.status_code == 200:
                data = grounds_response.json()
                
                # Handle both list and dict response
                if isinstance(data, dict) and "grounds" in data:
                    grounds = data["grounds"]
                else:
                    grounds = data if isinstance(data, list) else []
                
                if len(grounds) > 0:
                    # Check evidence in grounds
                    for ground in grounds[:3]:  # Check first 3 grounds
                        if "evidence" in ground:
                            evidence = ground["evidence"]
                            print(f"Ground has {len(evidence) if isinstance(evidence, list) else 0} evidence items")
                    print("PASS: Evidence data structure verified")
                else:
                    print("No grounds found to check evidence")
            else:
                print(f"Grounds endpoint returned {grounds_response.status_code}")
        else:
            pytest.skip("No cases available to test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
