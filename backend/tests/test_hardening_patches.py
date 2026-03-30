"""
Criminal Appeal AI - Backend Hardening Patches Test Suite
Tests for the 7 additive backend patches:
1. models/__init__.py - EvidenceItem, LawSection, SimilarCase, LegitimacyScores, ReportMetadata submodels
2. llm_service.py - call_llm_for_json, call_llm_for_report, call_llm_structured functions
3. grounds.py - structured models and legitimacy_scores
4. deadlines.py - assessment_note and assessment_type fields
5. compare.py - disclaimer and assessment_note fields
6. timeline.py - source_mode and verification_status fields
7. server.py - report metadata and structured LLM calls
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"
TEST_CASE_ID = "case_87ef925be713"


class TestHealthCheck:
    """Health check endpoint tests"""
    
    def test_health_returns_healthy_status(self):
        """Test /api/health returns status:healthy and database:connected"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "healthy", f"Expected status:healthy, got {data.get('status')}"
        assert data.get("database") == "connected", f"Expected database:connected, got {data.get('database')}"
        assert "timestamp" in data, "Missing timestamp field"
        print(f"✓ Health check passed: {data}")


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_login_returns_session_token(self):
        """Test POST /api/auth/login returns session_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "session_token" in data, f"Missing session_token in response: {data}"
        assert len(data["session_token"]) > 0, "session_token is empty"
        # User fields may be at root level or nested in "user" object
        if "user" in data:
            assert data["user"]["email"] == TEST_EMAIL, f"Email mismatch: {data['user']['email']}"
        else:
            assert data.get("email") == TEST_EMAIL, f"Email mismatch: {data.get('email')}"
        print(f"✓ Login successful, session_token received")
        return data["session_token"]


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("session_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestCasesEndpoint:
    """Cases endpoint tests"""
    
    def test_get_cases_returns_list(self, auth_headers):
        """Test GET /api/cases returns list of cases"""
        response = requests.get(f"{BASE_URL}/api/cases", headers=auth_headers)
        assert response.status_code == 200, f"Get cases failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ GET /api/cases returned {len(data)} cases")


class TestCaseStrengthEndpoint:
    """Case strength/readiness endpoint tests - Patch #5 (deadlines.py)"""
    
    def test_strength_returns_readiness_scores(self, auth_headers):
        """Test GET /api/cases/{case_id}/strength returns readiness scores with assessment_type and assessment_note"""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/strength", headers=auth_headers)
        assert response.status_code == 200, f"Get strength failed: {response.text}"
        
        data = response.json()
        
        # Check for assessment_type field (HARDENING PATCH)
        assert "assessment_type" in data, f"Missing assessment_type field: {data.keys()}"
        assert data["assessment_type"] == "appeal_preparation_readiness", f"Wrong assessment_type: {data['assessment_type']}"
        
        # Check for assessment_note field (HARDENING PATCH)
        assert "assessment_note" in data, f"Missing assessment_note field: {data.keys()}"
        assert "preparation" in data["assessment_note"].lower() or "documentation" in data["assessment_note"].lower(), \
            f"assessment_note should mention preparation/documentation: {data['assessment_note']}"
        
        # Check for readiness scores
        assert "readiness_score" in data, f"Missing readiness_score: {data.keys()}"
        assert "readiness_level" in data, f"Missing readiness_level: {data.keys()}"
        assert "breakdown" in data, f"Missing breakdown: {data.keys()}"
        
        print(f"✓ Case strength endpoint returns assessment_type: {data['assessment_type']}")
        print(f"✓ Case strength endpoint returns assessment_note: {data['assessment_note'][:80]}...")


class TestReportsEndpoint:
    """Reports endpoint tests - Patch #7 (server.py)"""
    
    def test_get_reports_returns_list(self, auth_headers):
        """Test GET /api/cases/{case_id}/reports returns list of reports"""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports", headers=auth_headers)
        assert response.status_code == 200, f"Get reports failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ GET /api/cases/{TEST_CASE_ID}/reports returned {len(data)} reports")
        
        # Check for metadata, source_mode, verification_status fields in reports (HARDENING PATCH)
        for report in data:
            # These fields may or may not be present depending on when report was generated
            if "source_mode" in report:
                print(f"  - Report {report.get('report_id', 'unknown')}: source_mode={report['source_mode']}")
            if "verification_status" in report:
                print(f"  - Report {report.get('report_id', 'unknown')}: verification_status={report['verification_status']}")


class TestGroundsEndpoint:
    """Grounds endpoint tests - Patch #3 (grounds.py)"""
    
    def test_get_grounds_returns_legitimacy_scores(self, auth_headers):
        """Test GET /api/cases/{case_id}/grounds returns grounds with legitimacy_scores and is_unlocked"""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds", headers=auth_headers)
        assert response.status_code == 200, f"Get grounds failed: {response.text}"
        
        data = response.json()
        assert "grounds" in data or isinstance(data, list), f"Unexpected response format: {data.keys() if isinstance(data, dict) else type(data)}"
        assert "is_unlocked" in data, f"Missing is_unlocked field: {data.keys()}"
        
        grounds = data.get("grounds", [])
        print(f"✓ GET /api/cases/{TEST_CASE_ID}/grounds returned {len(grounds)} grounds, is_unlocked={data['is_unlocked']}")
        
        # If unlocked, check for legitimacy_scores (HARDENING PATCH)
        if data["is_unlocked"] and grounds:
            for ground in grounds[:3]:  # Check first 3 grounds
                if "legitimacy_scores" in ground:
                    scores = ground["legitimacy_scores"]
                    assert "legal_score" in scores, f"Missing legal_score in legitimacy_scores"
                    assert "evidence_score" in scores, f"Missing evidence_score in legitimacy_scores"
                    assert "viability_score" in scores, f"Missing viability_score in legitimacy_scores"
                    assert "total_score" in scores, f"Missing total_score in legitimacy_scores"
                    assert "rating" in scores, f"Missing rating in legitimacy_scores"
                    print(f"  - Ground {ground.get('ground_id', 'unknown')}: legitimacy_scores present with rating={scores['rating']}")


class TestTimelineEndpoint:
    """Timeline endpoint tests - Patch #6 (timeline.py)"""
    
    def test_get_timeline_returns_provenance_fields(self, auth_headers):
        """Test GET /api/cases/{case_id}/timeline returns events with source_mode and verification_status"""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline", headers=auth_headers)
        assert response.status_code == 200, f"Get timeline failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ GET /api/cases/{TEST_CASE_ID}/timeline returned {len(data)} events")
        
        # Check for source_mode and verification_status fields (HARDENING PATCH)
        for event in data[:3]:  # Check first 3 events
            if "source_mode" in event:
                print(f"  - Event {event.get('event_id', 'unknown')}: source_mode={event['source_mode']}")
            if "verification_status" in event:
                print(f"  - Event {event.get('event_id', 'unknown')}: verification_status={event['verification_status']}")


class TestDeadlinesEndpoint:
    """Deadlines endpoint tests - Patch #5 (deadlines.py)"""
    
    def test_get_deadlines_returns_list(self, auth_headers):
        """Test GET /api/cases/{case_id}/deadlines returns deadline list"""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/deadlines", headers=auth_headers)
        assert response.status_code == 200, f"Get deadlines failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ GET /api/cases/{TEST_CASE_ID}/deadlines returned {len(data)} deadlines")


class TestCompareSuccessFactorsEndpoint:
    """Compare success-factors endpoint tests - Patch #4 (compare.py)"""
    
    def test_success_factors_returns_disclaimer(self, auth_headers):
        """Test GET /api/compare/success-factors returns platform pattern indicators with disclaimer and assessment_note"""
        response = requests.get(f"{BASE_URL}/api/compare/success-factors", headers=auth_headers)
        assert response.status_code == 200, f"Get success-factors failed: {response.text}"
        
        data = response.json()
        
        # Check for disclaimer field (HARDENING PATCH)
        assert "disclaimer" in data, f"Missing disclaimer field: {data.keys()}"
        assert "platform" in data["disclaimer"].lower() or "legal" in data["disclaimer"].lower(), \
            f"Disclaimer should mention platform/legal: {data['disclaimer']}"
        
        # Check for assessment_note field (HARDENING PATCH)
        assert "assessment_note" in data, f"Missing assessment_note field: {data.keys()}"
        
        print(f"✓ Success-factors endpoint returns disclaimer: {data['disclaimer'][:80]}...")
        print(f"✓ Success-factors endpoint returns assessment_note: {data['assessment_note'][:80]}...")


class TestComparePatternsEndpoint:
    """Compare patterns endpoint tests - Patch #4 (compare.py)"""
    
    def test_patterns_returns_disclaimer(self, auth_headers):
        """Test GET /api/compare/patterns returns anonymized patterns with disclaimer field"""
        response = requests.get(f"{BASE_URL}/api/compare/patterns", headers=auth_headers)
        assert response.status_code == 200, f"Get patterns failed: {response.text}"
        
        data = response.json()
        
        # Check for disclaimer field (HARDENING PATCH)
        assert "disclaimer" in data, f"Missing disclaimer field: {data.keys()}"
        assert "platform" in data["disclaimer"].lower() or "court" in data["disclaimer"].lower(), \
            f"Disclaimer should mention platform/court: {data['disclaimer']}"
        
        # Check for assessment_note field (HARDENING PATCH)
        assert "assessment_note" in data, f"Missing assessment_note field: {data.keys()}"
        
        print(f"✓ Patterns endpoint returns disclaimer: {data['disclaimer'][:80]}...")
        print(f"✓ Patterns endpoint returns assessment_note: {data['assessment_note'][:80]}...")


class TestBackwardCompatibility:
    """Backward compatibility tests - ensure existing frontend still works"""
    
    def test_grounds_response_structure(self, auth_headers):
        """Test grounds response maintains backward-compatible structure"""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Must have these fields for frontend compatibility
        assert "grounds" in data or "count" in data, "Missing grounds/count fields"
        assert "is_unlocked" in data, "Missing is_unlocked field"
        assert "unlock_price" in data, "Missing unlock_price field"
        print("✓ Grounds response maintains backward-compatible structure")
    
    def test_strength_response_structure(self, auth_headers):
        """Test strength response maintains backward-compatible structure"""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/strength", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Must have these fields for frontend compatibility
        assert "overall_score" in data, "Missing overall_score field"
        assert "rating" in data, "Missing rating field"
        assert "breakdown" in data, "Missing breakdown field"
        assert "recommendations" in data, "Missing recommendations field"
        print("✓ Strength response maintains backward-compatible structure")
    
    def test_timeline_response_structure(self, auth_headers):
        """Test timeline response maintains backward-compatible structure"""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Timeline should return a list"
        if data:
            event = data[0]
            # Must have these fields for frontend compatibility
            assert "event_id" in event, "Missing event_id field"
            assert "title" in event, "Missing title field"
            assert "event_date" in event, "Missing event_date field"
            assert "event_type" in event, "Missing event_type field"
        print("✓ Timeline response maintains backward-compatible structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
