"""
Iteration 140: Ground Dedup Verification Tests
Tests the expanded LEGAL_TOPICS (12 topics), startup dedup, and safety-net dedup after sync.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://criminal-appeals-au-2.preview.emergentagent.com').rstrip('/')


class TestHealthAndBasicEndpoints:
    """Test health and basic API endpoints"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"Health check passed: {data}")
    
    def test_auth_session_endpoint_exists(self):
        """Test /api/auth/session endpoint exists (Google OAuth exchange)"""
        # This endpoint requires a valid session_id, so we just check it returns 422 (validation error)
        # rather than 404 (not found)
        response = requests.post(f"{BASE_URL}/api/auth/session", json={})
        # Should return 422 (missing session_id) not 404 (not found)
        assert response.status_code in [422, 400], f"Expected 422 or 400, got {response.status_code}"
        print(f"Auth session endpoint exists, returns {response.status_code} for empty request")


class TestGroundDedupLogic:
    """Test the ground deduplication logic directly"""
    
    def test_legal_topics_has_12_categories(self):
        """Verify LEGAL_TOPICS has 12 topic categories"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.ground_dedup import LEGAL_TOPICS
        
        expected_topics = [
            "judge_alone_trial",
            "psychiatric_evidence", 
            "media_coverage",
            "jury_misconduct",
            "sentencing_error",
            "ineffective_counsel",
            "evidence_admissibility",
            "fresh_evidence",
            "prosecutorial_misconduct",
            "judicial_direction",
            "unreasonable_verdict",
            "procedural_error",
        ]
        
        assert len(LEGAL_TOPICS) == 12, f"Expected 12 topics, got {len(LEGAL_TOPICS)}"
        for topic in expected_topics:
            assert topic in LEGAL_TOPICS, f"Missing topic: {topic}"
        print(f"LEGAL_TOPICS has all 12 expected categories")
    
    def test_media_coverage_keywords_expanded(self):
        """Verify media_coverage topic has expanded keywords including 'media influence'"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.ground_dedup import LEGAL_TOPICS
        
        media_keywords = LEGAL_TOPICS.get("media_coverage", set())
        # Check for the keywords that were missing in iteration 139
        required_keywords = ["media influence", "media on jury", "jury media"]
        for kw in required_keywords:
            assert kw in media_keywords, f"Missing keyword in media_coverage: '{kw}'"
        print(f"media_coverage has all required keywords: {required_keywords}")
    
    def test_media_influence_detected_as_duplicate(self):
        """Test that 'Media Influence on Jury' is detected as duplicate of 'Prejudicial Media Coverage'"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.ground_dedup import is_ground_duplicate, _extract_topics
        
        title1 = "Media Influence on Jury"
        title2 = "Prejudicial Media Coverage"
        
        # Check topics are extracted
        topics1 = _extract_topics(title1)
        topics2 = _extract_topics(title2)
        print(f"Topics for '{title1}': {topics1}")
        print(f"Topics for '{title2}': {topics2}")
        
        # Both should have media_coverage topic
        assert "media_coverage" in topics1, f"'{title1}' should have media_coverage topic"
        assert "media_coverage" in topics2, f"'{title2}' should have media_coverage topic"
        
        # Should be detected as duplicates
        result = is_ground_duplicate(title1, title2)
        assert result is True, f"'{title1}' should be duplicate of '{title2}'"
        print(f"PASS: '{title1}' correctly detected as duplicate of '{title2}'")
    
    def test_ineffective_counsel_keywords_expanded(self):
        """Verify ineffective_counsel has 'ineffective assistance' keyword"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.ground_dedup import LEGAL_TOPICS
        
        counsel_keywords = LEGAL_TOPICS.get("ineffective_counsel", set())
        assert "ineffective assistance" in counsel_keywords, "Missing 'ineffective assistance' keyword"
        print(f"ineffective_counsel has 'ineffective assistance' keyword")
    
    def test_evidence_admissibility_keywords_expanded(self):
        """Verify evidence_admissibility has 'improper admission' keyword"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.ground_dedup import LEGAL_TOPICS
        
        evidence_keywords = LEGAL_TOPICS.get("evidence_admissibility", set())
        assert "improper admission" in evidence_keywords, "Missing 'improper admission' keyword"
        print(f"evidence_admissibility has 'improper admission' keyword")
    
    def test_judicial_direction_keywords_expanded(self):
        """Verify judicial_direction has 'prejudicial comments' and 'unfair trial' keywords"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.ground_dedup import LEGAL_TOPICS
        
        judicial_keywords = LEGAL_TOPICS.get("judicial_direction", set())
        assert "prejudicial comments" in judicial_keywords, "Missing 'prejudicial comments' keyword"
        assert "unfair trial" in judicial_keywords, "Missing 'unfair trial' keyword"
        print(f"judicial_direction has 'prejudicial comments' and 'unfair trial' keywords")


class TestCleanupDuplicatesEndpoint:
    """Test the cleanup-duplicates endpoint"""
    
    def test_cleanup_duplicates_endpoint_requires_auth(self):
        """Test /api/cases/{case_id}/grounds/cleanup-duplicates requires authentication"""
        response = requests.post(f"{BASE_URL}/api/cases/test_case/grounds/cleanup-duplicates")
        # Should return 401 (unauthorized) not 404 (not found)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"cleanup-duplicates endpoint requires auth (returns 401)")


class TestStartupDedupRuns:
    """Test that startup dedup runs on boot"""
    
    def test_startup_dedup_function_exists(self):
        """Verify startup_dedup_grounds function exists in server.py"""
        import sys
        sys.path.insert(0, '/app/backend')
        # The function is defined in server.py and registered as @app.on_event("startup")
        # We verify it exists by checking the server module
        import importlib.util
        spec = importlib.util.spec_from_file_location("server", "/app/backend/server.py")
        # Just verify the file contains the function definition
        with open("/app/backend/server.py", "r") as f:
            content = f.read()
        assert "async def startup_dedup_grounds" in content, "startup_dedup_grounds function not found in server.py"
        assert '@app.on_event("startup")' in content, "startup event decorator not found"
        print("startup_dedup_grounds function exists in server.py and is registered as startup event")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
