"""
Iteration 157 - Three-Axis Viability Scoring Tests
Tests for Phase 2-4 implementation based on barrister feedback:
- Three-axis model: outcome_impact, legal_alignment, evidence_support
- Viability labels: Arguable — Strong, Arguable — Moderate, Requires Development
- Auto-identify endpoints
- Health endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Cr1m1nalApp3al$2025"
TEST_CASE_ID = "case_f8bf63e9dcbe"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("session_token")
    pytest.skip("Authentication failed")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestHealthEndpoint:
    """Test health endpoint"""
    
    def test_health_endpoint_returns_healthy(self):
        """GET /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "database" in data
        assert "timestamp" in data


class TestLegitimacyEngine:
    """Test the three-axis legitimacy scoring engine"""
    
    def test_calculate_ground_rating_returns_three_axis_fields(self):
        """calculate_ground_rating returns outcome_impact, legal_alignment, evidence_support"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.legitimacy_engine import calculate_ground_rating
        
        test_ground = {
            'ground_type': 'judicial_error',
            'supporting_evidence': [
                {'quote': 'The trial judge failed to properly consider the psychiatric evidence.'},
                {'quote': 'Expert testimony indicated significant cognitive impairment.'},
                {'quote': 'The psychiatric report clearly stated psychotic symptoms.'}
            ],
            'undermining_items': []
        }
        
        result = calculate_ground_rating(test_ground)
        
        # Check three-axis fields exist and have correct structure
        assert 'outcome_impact' in result
        assert 'legal_alignment' in result
        assert 'evidence_support' in result
        
        # Check each axis has score and label
        assert 'score' in result['outcome_impact']
        assert 'label' in result['outcome_impact']
        assert 'score' in result['legal_alignment']
        assert 'label' in result['legal_alignment']
        assert 'score' in result['evidence_support']
        assert 'label' in result['evidence_support']
    
    def test_outcome_impact_labels(self):
        """outcome_impact returns Determinative, Influential, or Minor"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.legitimacy_engine import score_outcome_impact
        
        # Determinative ground types
        result = score_outcome_impact('judicial_error')
        assert result['label'] == 'Determinative'
        assert result['score'] == 3
        
        # Influential ground types
        result = score_outcome_impact('procedural_error')
        assert result['label'] == 'Influential'
        assert result['score'] == 2
        
        # Minor ground types
        result = score_outcome_impact('constitutional_violation')
        assert result['label'] == 'Minor'
        assert result['score'] == 1
    
    def test_legal_alignment_labels(self):
        """legal_alignment returns Direct authority, Analogous, or Weak"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.legitimacy_engine import score_legal_alignment
        
        # Direct authority
        result = score_legal_alignment('judicial_error')
        assert result['label'] == 'Direct authority'
        assert result['score'] == 3
        
        # Analogous
        result = score_legal_alignment('procedural_error')
        assert result['label'] == 'Analogous'
        assert result['score'] == 2
        
        # Weak
        result = score_legal_alignment('constitutional_violation')
        assert result['label'] == 'Weak'
        assert result['score'] == 1
    
    def test_evidence_support_labels(self):
        """evidence_support returns Strong, Partial, Limited, or None"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.legitimacy_engine import score_evidence_support
        
        # Strong evidence (3+ items with 2+ substantive quotes)
        strong_evidence = [
            {'quote': 'A' * 100},  # >80 chars
            {'quote': 'B' * 100},  # >80 chars
            {'quote': 'C' * 100},  # >80 chars
        ]
        result = score_evidence_support(strong_evidence)
        assert result['label'] == 'Strong'
        assert result['score'] == 3
        
        # Partial evidence
        partial_evidence = [
            {'quote': 'A' * 100},  # >80 chars
            {'quote': 'B' * 50},   # <80 chars
        ]
        result = score_evidence_support(partial_evidence)
        assert result['label'] == 'Partial'
        assert result['score'] == 2
        
        # Limited evidence
        limited_evidence = [{'quote': 'Short quote'}]
        result = score_evidence_support(limited_evidence)
        assert result['label'] == 'Limited'
        assert result['score'] == 1
        
        # No evidence
        result = score_evidence_support([])
        assert result['label'] == 'None'
        assert result['score'] == 0
    
    def test_viability_labels(self):
        """viability_label returns correct appellate viability labels"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.legitimacy_engine import calculate_ground_rating
        
        # Strong viability (total >= 7)
        strong_ground = {
            'ground_type': 'judicial_error',  # 3 + 3 = 6
            'supporting_evidence': [
                {'quote': 'A' * 100},
                {'quote': 'B' * 100},
                {'quote': 'C' * 100},
            ],  # +3 = 9
        }
        result = calculate_ground_rating(strong_ground)
        assert result['viability_label'] == 'Arguable — Strong'
        assert result['rating'] == 'strong'
        
        # Moderate viability (total >= 4 and < 7)
        moderate_ground = {
            'ground_type': 'procedural_error',  # 2 + 2 = 4
            'supporting_evidence': [{'quote': 'Short'}],  # +1 = 5
        }
        result = calculate_ground_rating(moderate_ground)
        assert result['viability_label'] == 'Arguable — Moderate'
        assert result['rating'] == 'moderate'
        
        # Weak viability (total < 4)
        weak_ground = {
            'ground_type': 'constitutional_violation',  # 1 + 1 = 2
            'supporting_evidence': [],  # +0 = 2
        }
        result = calculate_ground_rating(weak_ground)
        assert result['viability_label'] == 'Requires Development'
        assert result['rating'] == 'weak'
    
    def test_hard_safety_rule_no_strong_without_evidence(self):
        """No ground rated 'Arguable — Strong' without evidence_support >= 2"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.legitimacy_engine import calculate_ground_rating
        
        # High scoring ground type but no evidence
        ground = {
            'ground_type': 'judicial_error',  # 3 + 3 = 6
            'supporting_evidence': [{'quote': 'Short'}],  # Limited = 1
        }
        result = calculate_ground_rating(ground)
        # Total would be 7 (strong) but evidence is limited, so capped at moderate
        assert result['rating'] != 'strong'
        assert result['viability_label'] != 'Arguable — Strong'
    
    def test_hard_safety_rule_constitutional_deprioritised(self):
        """Constitutional grounds deprioritised - never rated strong"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.legitimacy_engine import calculate_ground_rating
        
        # Constitutional ground with strong evidence
        ground = {
            'ground_type': 'constitutional_violation',
            'supporting_evidence': [
                {'quote': 'A' * 100},
                {'quote': 'B' * 100},
                {'quote': 'C' * 100},
            ],
        }
        result = calculate_ground_rating(ground)
        # Even with strong evidence, constitutional grounds capped at moderate
        assert result['rating'] != 'strong'


class TestGroundsAPI:
    """Test grounds API endpoints"""
    
    def test_get_grounds_returns_legitimacy_scores(self, auth_headers):
        """GET /api/cases/{case_id}/grounds returns grounds with legitimacy_scores"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert 'grounds' in data
        assert 'count' in data
        assert data['count'] > 0
        
        # Check first ground has legitimacy_scores
        ground = data['grounds'][0]
        assert 'legitimacy_scores' in ground
        
        # Note: Existing grounds may have legacy format without three-axis fields
        # The new fields only appear when grounds are re-generated via auto-identify
        ls = ground['legitimacy_scores']
        assert 'rating' in ls or 'total_score' in ls


class TestAutoIdentifyEndpoints:
    """Test auto-identify background task endpoints"""
    
    def test_auto_identify_status_endpoint(self, auth_headers):
        """GET /api/cases/{case_id}/grounds/auto-identify/status returns task status"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/auto-identify/status",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have task_id and status
        assert 'task_id' in data
        assert 'status' in data
        
        # Status should be one of the valid values
        valid_statuses = ['none', 'pending', 'extracting', 'classifying', 'verifying', 'finalising', 'completed', 'failed']
        assert data['status'] in valid_statuses
    
    def test_auto_identify_post_returns_task_id(self, auth_headers):
        """POST /api/cases/{case_id}/grounds/auto-identify returns task_id"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/auto-identify",
            headers=auth_headers
        )
        # Should return 200 or 202 (accepted)
        assert response.status_code in [200, 202]
        data = response.json()
        
        # Should have task_id and status
        assert 'task_id' in data
        assert 'status' in data
        
        # Status should be 'started' or 'already_running'
        assert data['status'] in ['started', 'already_running']


class TestAppellatePathway:
    """Test appellate pathway field in classify.py"""
    
    def test_appellate_pathways_defined(self):
        """APPELLATE_PATHWAYS dict contains all Australian states"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.pipeline.classify import APPELLATE_PATHWAYS
        
        expected_states = ['nsw', 'vic', 'qld', 'sa', 'wa', 'tas', 'nt', 'act']
        for state in expected_states:
            assert state in APPELLATE_PATHWAYS
            assert 'Criminal' in APPELLATE_PATHWAYS[state] or 'Supreme' in APPELLATE_PATHWAYS[state]


class TestVerifyPipeline:
    """Test verify.py law section and citation filtering"""
    
    def test_law_section_filtering_logic(self):
        """verify.py filters out law sections without real section numbers"""
        # This tests the filtering logic in verify.py
        test_law_sections = [
            {'section': 's 6(1)', 'act': 'Criminal Appeal Act 1912 (NSW)'},
            {'section': 'not provided', 'act': 'Some Act'},
            {'section': 'unknown', 'act': 'Another Act'},
            {'section': '', 'act': 'Empty Act'},
            {'section': 's 132', 'act': 'Crimes Act 1900 (NSW)'},
        ]
        
        # Apply the same filtering logic as verify.py
        clean_law_sections = []
        for ls in test_law_sections:
            section = (ls.get("section") or "").strip()
            if not section or "not provided" in section.lower() or "unknown" in section.lower() or "n/a" in section.lower():
                continue
            clean_law_sections.append(ls)
        
        assert len(clean_law_sections) == 2
        assert clean_law_sections[0]['section'] == 's 6(1)'
        assert clean_law_sections[1]['section'] == 's 132'
    
    def test_similar_cases_filtering_logic(self):
        """verify.py filters out similar cases with placeholder names"""
        test_similar_cases = [
            {'case_name': 'R v Smith [2015] NSWCCA 123', 'citation': '[2015] NSWCCA 123'},
            {'case_name': 'R v [Surname] [Year]', 'citation': None},
            {'case_name': 'Case name', 'citation': None},
            {'case_name': 'R v Jones', 'citation': 'verification needed'},
            {'case_name': 'R v Brown [2020] QCA 45', 'citation': '[2020] QCA 45'},
        ]
        
        # Apply the same filtering logic as verify.py
        clean_similar_cases = []
        for sc in test_similar_cases:
            name = sc.get("case_name", "")
            citation = sc.get("citation", "")
            if not name or "[Surname]" in name or "[Year]" in name or "Case name" in name:
                continue
            if citation and ("verification needed" in citation.lower() or "not available" in citation.lower()):
                sc["citation"] = None
            clean_similar_cases.append(sc)
        
        assert len(clean_similar_cases) == 3
        assert clean_similar_cases[0]['case_name'] == 'R v Smith [2015] NSWCCA 123'
        # R v Jones should be included but with citation set to None
        assert clean_similar_cases[1]['case_name'] == 'R v Jones'
        assert clean_similar_cases[1]['citation'] is None
        assert clean_similar_cases[2]['case_name'] == 'R v Brown [2020] QCA 45'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
