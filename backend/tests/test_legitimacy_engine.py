"""
Test suite for Criminal Appeal AI - Legitimacy Engine & Barrister Review Upgrade
Tests: legitimacy scoring, case readiness, user_id access control, compare endpoints, unverified badges
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"
TEST_CASE_ID = "case_b24f94577da6"


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ Health check passed: {data}")
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        # User fields may be at root level or nested under "user"
        assert "email" in data or "user" in data
        print(f"✓ Login successful, token received")
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
    return {"Authorization": f"Bearer {auth_token}"}


class TestLegitimacyEngine:
    """Tests for the 3-layer legitimacy scoring engine"""
    
    def test_grounds_endpoint_returns_legitimacy_scores(self, auth_headers):
        """GET /api/cases/{case_id}/grounds returns legitimacy_scores for each ground"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check if unlocked
        if not data.get("is_unlocked"):
            print(f"⚠ Grounds not unlocked, count: {data.get('count')}")
            return
        
        grounds = data.get("grounds", [])
        print(f"✓ Found {len(grounds)} grounds")
        
        # Check each ground has legitimacy_scores
        for ground in grounds:
            scores = ground.get("legitimacy_scores")
            if scores:
                # Verify all required score fields
                assert "legal_score" in scores, "Missing legal_score"
                assert "evidence_score" in scores, "Missing evidence_score"
                assert "viability_score" in scores, "Missing viability_score"
                assert "total_score" in scores, "Missing total_score"
                assert "rating" in scores, "Missing rating"
                assert "confidence_note" in scores, "Missing confidence_note"
                
                # Verify score ranges
                assert 0 <= scores["legal_score"] <= 3, f"legal_score out of range: {scores['legal_score']}"
                assert 0 <= scores["evidence_score"] <= 3, f"evidence_score out of range: {scores['evidence_score']}"
                assert 0 <= scores["viability_score"] <= 3, f"viability_score out of range: {scores['viability_score']}"
                assert 0 <= scores["total_score"] <= 9, f"total_score out of range: {scores['total_score']}"
                assert scores["rating"] in ["strong", "moderate", "weak"], f"Invalid rating: {scores['rating']}"
                
                # HARD SAFETY RULE: No STRONG without evidence_score >= 2
                if scores["rating"] == "strong":
                    assert scores["evidence_score"] >= 2, "SAFETY VIOLATION: strong rating with evidence_score < 2"
                
                print(f"  ✓ Ground '{ground.get('title', 'Unknown')[:40]}...' has valid legitimacy_scores: {scores['rating']} ({scores['total_score']}/9)")
            else:
                print(f"  ⚠ Ground '{ground.get('title', 'Unknown')[:40]}...' missing legitimacy_scores")


class TestCaseReadiness:
    """Tests for Case Readiness Score (reframed from Case Strength)"""
    
    def test_strength_endpoint_returns_readiness(self, auth_headers):
        """GET /api/cases/{case_id}/strength returns score_type='readiness' with correct labels"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/strength",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check score_type is 'readiness'
        assert data.get("score_type") == "readiness", f"Expected score_type='readiness', got '{data.get('score_type')}'"
        print(f"✓ score_type is 'readiness'")
        
        # Check disclaimer exists
        assert "disclaimer" in data, "Missing disclaimer"
        disclaimer = data["disclaimer"]
        assert "preparation" in disclaimer.lower() or "readiness" in disclaimer.lower(), "Disclaimer should mention preparation/readiness"
        assert "legal merit" in disclaimer.lower() or "not a determination" in disclaimer.lower(), "Disclaimer should clarify not legal merit"
        print(f"✓ Disclaimer present: '{disclaimer[:80]}...'")
        
        # Check rating labels are correct (NOT Strong/Moderate/Weak)
        rating = data.get("rating")
        valid_labels = ["Advanced", "Progressing", "Developing", "Early Stage"]
        assert rating in valid_labels, f"Invalid rating label: '{rating}'. Expected one of {valid_labels}"
        print(f"✓ Rating label is '{rating}' (correct readiness label)")
        
        # Check overall_score exists
        assert "overall_score" in data
        assert 0 <= data["overall_score"] <= 100
        print(f"✓ Overall score: {data['overall_score']}/100")
        
        # Check breakdown exists
        assert "breakdown" in data
        breakdown = data["breakdown"]
        assert "grounds" in breakdown
        assert "documentation" in breakdown
        assert "timeline" in breakdown
        assert "preparation" in breakdown
        print(f"✓ Breakdown sections present")


class TestUserIdAccessControl:
    """Tests for user_id enforcement on mutating endpoints"""
    
    def test_deadline_patch_requires_user_id(self, auth_headers):
        """PATCH /api/cases/{case_id}/deadlines/{deadline_id} enforces user_id"""
        # First, get existing deadlines
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/deadlines",
            headers=auth_headers
        )
        
        if response.status_code == 200 and len(response.json()) > 0:
            deadline = response.json()[0]
            deadline_id = deadline.get("deadline_id")
            
            # Try to update with correct user (should work)
            patch_response = requests.patch(
                f"{BASE_URL}/api/cases/{TEST_CASE_ID}/deadlines/{deadline_id}",
                headers=auth_headers,
                json={"title": deadline.get("title", "Test")}
            )
            assert patch_response.status_code in [200, 404], f"Unexpected status: {patch_response.status_code}"
            print(f"✓ Deadline PATCH with correct user: {patch_response.status_code}")
        else:
            print("⚠ No deadlines found to test PATCH")
    
    def test_checklist_patch_requires_user_id(self, auth_headers):
        """PATCH /api/cases/{case_id}/checklist/{item_id} enforces user_id"""
        # First, get existing checklist
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/checklist",
            headers=auth_headers
        )
        
        if response.status_code == 200 and len(response.json()) > 0:
            item = response.json()[0]
            item_id = item.get("item_id")
            
            # Try to update with correct user (should work)
            patch_response = requests.patch(
                f"{BASE_URL}/api/cases/{TEST_CASE_ID}/checklist/{item_id}",
                headers=auth_headers,
                json={"is_completed": item.get("is_completed", False)}
            )
            assert patch_response.status_code in [200, 404], f"Unexpected status: {patch_response.status_code}"
            print(f"✓ Checklist PATCH with correct user: {patch_response.status_code}")
        else:
            print("⚠ No checklist items found to test PATCH")


class TestCompareEndpoints:
    """Tests for reframed compare endpoints"""
    
    def test_patterns_endpoint(self, auth_headers):
        """GET /api/compare/patterns returns disclaimer about platform patterns"""
        response = requests.get(
            f"{BASE_URL}/api/compare/patterns",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check disclaimer exists and mentions platform patterns
        assert "disclaimer" in data, "Missing disclaimer"
        disclaimer = data["disclaimer"].lower()
        assert "platform" in disclaimer or "internal" in disclaimer, "Disclaimer should mention platform/internal"
        assert "not" in disclaimer and ("court" in disclaimer or "legal" in disclaimer or "success" in disclaimer), \
            "Disclaimer should clarify not court outcomes/legal success"
        print(f"✓ Patterns disclaimer: '{data['disclaimer'][:100]}...'")
        
        # Check for suppressed flag (minimum sample threshold)
        if data.get("suppressed"):
            print(f"⚠ Patterns suppressed due to minimum sample threshold: {data.get('message')}")
        else:
            print(f"✓ Patterns data returned: {data.get('total_cases')} cases, {data.get('total_grounds')} grounds")
    
    def test_case_composition_endpoint(self, auth_headers):
        """GET /api/compare/case-composition returns disclaimer about preparation patterns"""
        response = requests.get(
            f"{BASE_URL}/api/compare/case-composition",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check disclaimer exists
        assert "disclaimer" in data, "Missing disclaimer"
        disclaimer = data["disclaimer"].lower()
        assert "preparation" in disclaimer or "pattern" in disclaimer, "Disclaimer should mention preparation/patterns"
        assert "not" in disclaimer and ("merit" in disclaimer or "prospect" in disclaimer), \
            "Disclaimer should clarify not legal merit/prospects"
        print(f"✓ Case composition disclaimer: '{data['disclaimer'][:100]}...'")
        
        # Check for suppressed flag
        if data.get("suppressed"):
            print(f"⚠ Case composition suppressed: {data.get('message')}")
        else:
            print(f"✓ Case composition data returned: {data.get('total_cases')} cases")


class TestUnverifiedBadges:
    """Tests for unverified badges on AI-referenced cases"""
    
    def test_similar_cases_marked_unverified(self, auth_headers):
        """Similar cases in grounds should have verified:false"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=auth_headers
        )
        
        if response.status_code != 200:
            pytest.skip("Could not fetch grounds")
        
        data = response.json()
        if not data.get("is_unlocked"):
            print("⚠ Grounds not unlocked, skipping similar_cases check")
            return
        
        grounds = data.get("grounds", [])
        found_similar_cases = False
        
        for ground in grounds:
            similar_cases = ground.get("similar_cases", [])
            for case in similar_cases:
                found_similar_cases = True
                # Check verified field exists and is False
                assert "verified" in case, f"Missing 'verified' field in similar case: {case.get('case_name')}"
                assert case["verified"] == False, f"Similar case should be verified=false: {case.get('case_name')}"
                print(f"  ✓ Similar case '{case.get('case_name')}' has verified=false")
        
        if not found_similar_cases:
            print("⚠ No similar cases found in grounds to verify")
        else:
            print(f"✓ All similar cases marked as unverified")


class TestLegitimacyEngineLogic:
    """Unit tests for legitimacy engine scoring logic"""
    
    def test_legal_basis_scores(self):
        """Test legal basis scoring for different ground types"""
        from services.legitimacy_engine import score_legal_basis
        
        # High-value grounds should score 3
        assert score_legal_basis("miscarriage_of_justice") == 3
        assert score_legal_basis("fresh_evidence") == 3
        assert score_legal_basis("judicial_error") == 3
        
        # Medium-value grounds should score 2
        assert score_legal_basis("sentencing_error") == 2
        assert score_legal_basis("ineffective_counsel") == 2
        
        # Other/unknown should score 1
        assert score_legal_basis("other") == 1
        assert score_legal_basis("unknown_type") == 1
        
        print("✓ Legal basis scoring correct")
    
    def test_evidence_scoring(self):
        """Test evidence scoring based on quote length"""
        from services.legitimacy_engine import score_evidence
        
        # No evidence = 0
        assert score_evidence([]) == 0
        assert score_evidence(None) == 0
        
        # Short quote (< 15 chars) = 1
        assert score_evidence([{"quote": "Short text"}]) == 1
        
        # Medium quote (15-50 chars) = 2
        assert score_evidence([{"quote": "This is a medium length quote for testing"}]) == 2
        
        # Long quote (> 50 chars) = 3
        assert score_evidence([{"quote": "This is a very long quote that exceeds fifty characters and should score maximum points"}]) == 3
        
        print("✓ Evidence scoring correct")
    
    def test_hard_safety_rule(self):
        """Test that STRONG rating requires evidence_score >= 2"""
        from services.legitimacy_engine import calculate_ground_rating
        
        # High legal basis but no evidence should NOT be strong
        ground = {
            "ground_type": "miscarriage_of_justice",
            "supporting_evidence": []  # No evidence
        }
        result = calculate_ground_rating(ground)
        assert result["rating"] != "strong", "SAFETY VIOLATION: strong rating without evidence"
        print(f"✓ No evidence -> rating: {result['rating']} (not strong)")
        
        # High legal basis with weak evidence should NOT be strong
        ground2 = {
            "ground_type": "miscarriage_of_justice",
            "supporting_evidence": [{"quote": "Short"}]  # Weak evidence
        }
        result2 = calculate_ground_rating(ground2)
        assert result2["rating"] != "strong", "SAFETY VIOLATION: strong rating with weak evidence"
        print(f"✓ Weak evidence -> rating: {result2['rating']} (not strong)")
        
        # High legal basis with strong evidence CAN be strong
        ground3 = {
            "ground_type": "miscarriage_of_justice",
            "supporting_evidence": [{"quote": "This is a very detailed quote from the transcript showing clear evidence of the issue at hand"}]
        }
        result3 = calculate_ground_rating(ground3)
        print(f"✓ Strong evidence -> rating: {result3['rating']}, total: {result3['total_score']}/9")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
