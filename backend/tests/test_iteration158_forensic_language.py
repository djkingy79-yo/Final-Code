"""
Iteration 158 Tests: Forensic Appellate Language & Ground Merging
Tests for barrister feedback implementation:
1. Forensic appellate language in confidence notes
2. Ground merging (clustering related grounds under single ground with sub-particulars)
3. Contingent flag for ineffective_counsel
4. Ground-type-specific confidence notes (mens rea, proportionality, etc.)
5. Ineffective counsel cap at moderate unless evidence_score >= 3
"""
import pytest
import requests
import os
import sys
from pathlib import Path

# Portable path resolution — works in Docker, local dev, and CI
ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
FRONTEND_COMPONENTS_DIR = ROOT / "frontend" / "src" / "components"

# Add backend to path for direct imports
sys.path.insert(0, str(BACKEND_DIR))

from services.legitimacy_engine import (  # noqa: E402
    calculate_ground_rating,
    _generate_confidence_note,
)
from services.pipeline.classify import _merge_overlapping_grounds  # noqa: E402
from services.pipeline_models import IssueClassification  # noqa: E402

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthEndpoint:
    """Basic health check to ensure backend is running"""

    @pytest.mark.skipif(not BASE_URL, reason="REACT_APP_BACKEND_URL not set")
    def test_health_returns_200(self):
        """GET /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: Health endpoint returns 200 with status=healthy")


class TestLegitimacyEngineContingentFlag:
    """Test is_contingent flag for ineffective_counsel ground type"""
    
    def test_ineffective_counsel_returns_is_contingent_true(self):
        """Ineffective counsel ground should have is_contingent: true"""
        ground = {
            "ground_type": "ineffective_counsel",
            "supporting_evidence": ["Some evidence text here that is longer than 80 characters to count as strong evidence item"],
            "undermining_items": []
        }
        result = calculate_ground_rating(ground)
        assert result.get("is_contingent") is True, f"Expected is_contingent=True, got {result.get('is_contingent')}"
        print("PASS: ineffective_counsel returns is_contingent=True")
    
    def test_other_ground_types_not_contingent(self):
        """Other ground types should NOT have is_contingent: true"""
        for ground_type in ["miscarriage_of_justice", "sentencing_error", "judicial_error", "procedural_error"]:
            ground = {
                "ground_type": ground_type,
                "supporting_evidence": ["Evidence"],
                "undermining_items": []
            }
            result = calculate_ground_rating(ground)
            assert result.get("is_contingent") is False or result.get("is_contingent") is None, \
                f"Expected is_contingent=False for {ground_type}, got {result.get('is_contingent')}"
        print("PASS: Non-ineffective_counsel grounds do not have is_contingent=True")


class TestLegitimacyEngineConfidenceNotes:
    """Test forensic framing in confidence notes"""
    
    def test_ineffective_counsel_confidence_note_contains_contingent(self):
        """Ineffective counsel confidence note should contain 'CONTINGENT'"""
        note = _generate_confidence_note("ineffective_counsel", 2)
        assert "CONTINGENT" in note, f"Expected 'CONTINGENT' in note, got: {note}"
        print(f"PASS: ineffective_counsel confidence_note contains 'CONTINGENT': {note[:100]}...")
    
    def test_miscarriage_of_justice_confidence_note_contains_mens_rea(self):
        """Miscarriage of justice confidence note should reference mens rea / conviction safety"""
        note = _generate_confidence_note("miscarriage_of_justice", 2)
        assert "mens rea" in note.lower() or "conviction safety" in note.lower(), \
            f"Expected 'mens rea' or 'conviction safety' in note, got: {note}"
        print(f"PASS: miscarriage_of_justice confidence_note contains mens rea framing: {note[:100]}...")
    
    def test_sentencing_error_confidence_note_contains_proportionality(self):
        """Sentencing error confidence note should reference proportionality / moral culpability"""
        note = _generate_confidence_note("sentencing_error", 2)
        assert "proportionality" in note.lower() or "moral culpability" in note.lower(), \
            f"Expected 'proportionality' or 'moral culpability' in note, got: {note}"
        print(f"PASS: sentencing_error confidence_note contains proportionality framing: {note[:100]}...")
    
    def test_jury_irregularity_confidence_note_mentions_sub_particulars(self):
        """Jury irregularity confidence note should mention sub-particulars clustering"""
        note = _generate_confidence_note("jury_irregularity", 2)
        assert "sub-particulars" in note.lower() or "single" in note.lower(), \
            f"Expected sub-particulars guidance in note, got: {note}"
        print(f"PASS: jury_irregularity confidence_note mentions clustering: {note[:100]}...")


class TestIneffectiveCounselCap:
    """Test that ineffective_counsel is capped at moderate unless evidence_score >= 3"""
    
    def test_ineffective_counsel_capped_at_moderate_with_partial_evidence(self):
        """Ineffective counsel with evidence_score=2 should be capped at moderate"""
        # Create ground with enough evidence to normally be 'strong' but evidence_score < 3
        ground = {
            "ground_type": "ineffective_counsel",
            "supporting_evidence": [
                "Evidence item 1 that is longer than 80 characters to count as substantive quote for scoring purposes",
                "Evidence item 2 that is also longer than 80 characters to count as another substantive quote item"
            ],
            "undermining_items": []
        }
        result = calculate_ground_rating(ground)
        # With outcome=2, legal=2, evidence=2, total=6 which would normally be moderate
        # But even if total >= 7, ineffective_counsel should be capped at moderate unless evidence >= 3
        assert result["rating"] in ["moderate", "weak"], \
            f"Expected ineffective_counsel capped at moderate, got {result['rating']}"
        print(f"PASS: ineffective_counsel capped at '{result['rating']}' with evidence_score={result['evidence_support']['score']}")
    
    def test_ineffective_counsel_can_be_strong_with_strong_evidence(self):
        """Ineffective counsel with evidence_score=3 can be rated strong"""
        # Create ground with strong evidence (3+ items, 2+ substantive)
        ground = {
            "ground_type": "ineffective_counsel",
            "supporting_evidence": [
                "Evidence item 1 that is longer than 80 characters to count as substantive quote for scoring purposes",
                "Evidence item 2 that is also longer than 80 characters to count as another substantive quote item",
                "Evidence item 3 that is also longer than 80 characters to count as third substantive quote item",
                "Evidence item 4 short"
            ],
            "undermining_items": []
        }
        result = calculate_ground_rating(ground)
        # With outcome=2, legal=2, evidence=3, total=7 which is strong
        # And evidence_score=3, so cap doesn't apply
        assert result["evidence_support"]["score"] >= 3, \
            f"Expected evidence_score >= 3, got {result['evidence_support']['score']}"
        assert result["total_score"] >= 7, \
            f"Expected total_score >= 7, got {result['total_score']}"
        assert result["rating"] == "strong", \
            f"Expected rating 'strong' with evidence_score=3, got '{result['rating']}'"
        print(f"PASS: ineffective_counsel with evidence_score=3 is '{result['rating']}' (total={result['total_score']})")

class TestGroundMergingFunction:
    """Test _merge_overlapping_grounds clustering logic"""
    
    def _create_issue(self, title, description, ground_type="other"):
        """Helper to create IssueClassification objects"""
        return IssueClassification(
            case_id="test_case",
            user_id="test_user",
            title=title,
            ground_type=ground_type,
            description=description,
            linked_fact_ids=[],
            linked_event_ids=[],
            linked_finding_ids=[],
            classification_confidence="moderate",
            jurisdiction="nsw",
            appellate_pathway="",
            error_identified="",
            materiality=""
        )
    
    def test_jury_issues_clustered_under_procedural_unfairness(self):
        """Jury-related issues should be clustered under 'Procedural Unfairness (Jury Integrity)'"""
        issues = [
            self._create_issue("Judge-alone refusal", "The trial judge refused application for judge-alone trial", "jury_irregularity"),
            self._create_issue("Jury reduction issue", "The jury was reduced improperly", "jury_irregularity"),
            self._create_issue("Juror conduct concern", "A juror exhibited bias during deliberations", "jury_irregularity"),
            self._create_issue("Unrelated ground", "Some other issue", "other"),
        ]
        
        merged = _merge_overlapping_grounds(issues)
        
        # Should have merged jury issues into one
        jury_grounds = [i for i in merged if "jury" in i.title.lower() or "procedural unfairness" in i.title.lower()]
        assert len(jury_grounds) <= 2, f"Expected jury issues to be merged, got {len(jury_grounds)} jury-related grounds"
        
        # Check for parent title
        parent_titles = [i.title for i in merged]
        has_procedural_unfairness = any("Procedural Unfairness" in t for t in parent_titles)
        assert has_procedural_unfairness, f"Expected Procedural Unfairness parent, got {parent_titles}"
        print(f"Merged titles: {parent_titles}")
        print(f"PASS: Jury issues clustering - has_procedural_unfairness={has_procedural_unfairness}, total grounds={len(merged)}")
    
    def test_psychiatric_issues_clustered_under_mens_rea(self):
        """Psychiatric/mental issues should be clustered under mens rea ground"""
        issues = [
            self._create_issue("Psychiatric evidence failure", "The psychiatric evidence was not properly considered", "miscarriage_of_justice"),
            self._create_issue("Mental state determination", "The mental state of the accused was not properly assessed", "miscarriage_of_justice"),
            self._create_issue("Psychosis evidence", "Evidence of psychosis was ignored", "miscarriage_of_justice"),
            self._create_issue("Unrelated sentencing", "Sentence was excessive", "sentencing_error"),
        ]
        
        merged = _merge_overlapping_grounds(issues)
        
        # Check for mens rea parent title
        parent_titles = [i.title for i in merged]
        has_mens_rea = any("Mens Rea" in t or "Mental State" in t for t in parent_titles)
        assert has_mens_rea, f"Expected mens rea parent, got {parent_titles}"
        print(f"Merged titles: {parent_titles}")
        print(f"PASS: Psychiatric issues clustering - has_mens_rea={has_mens_rea}, total grounds={len(merged)}")
    
    def test_sentencing_issues_clustered(self):
        """Sentencing-related issues should be clustered"""
        issues = [
            self._create_issue("Manifest excess", "The sentence was manifestly excessive", "sentencing_error"),
            self._create_issue("Proportionality error", "The sentence was disproportionate to culpability", "sentencing_error"),
            self._create_issue("Moral culpability ignored", "The sentencing judge failed to consider moral culpability", "sentencing_error"),
            self._create_issue("Unrelated procedural", "Procedural issue", "procedural_error"),
        ]
        
        merged = _merge_overlapping_grounds(issues)
        
        # Check for sentencing parent title
        parent_titles = [i.title for i in merged]
        sentencing_grounds = [t for t in parent_titles if "sentencing" in t.lower() or "culpability" in t.lower()]
        assert sentencing_grounds, f"Expected sentencing parent, got {parent_titles}"
        print(f"Merged titles: {parent_titles}")
        print(f"PASS: Sentencing issues clustering - sentencing_grounds={len(sentencing_grounds)}, total grounds={len(merged)}")
    
    def test_ineffective_counsel_preserved_ungrouped(self):
        """Ineffective counsel should be preserved as standalone (not merged)"""
        issues = [
            self._create_issue("Ineffective counsel", "Counsel failed to call witnesses", "ineffective_counsel"),
            self._create_issue("Jury issue", "Jury was biased", "jury_irregularity"),
            self._create_issue("Another jury issue", "Jury reduction", "jury_irregularity"),
        ]
        
        merged = _merge_overlapping_grounds(issues)
        
        # Ineffective counsel should remain separate
        ineffective_grounds = [i for i in merged if i.ground_type == "ineffective_counsel"]
        assert len(ineffective_grounds) >= 1, "Ineffective counsel ground should be preserved"
        print(f"PASS: Ineffective counsel preserved - count={len(ineffective_grounds)}")
    
    def test_small_issue_list_not_merged(self):
        """Lists with <= 3 issues should not be merged"""
        issues = [
            self._create_issue("Issue 1", "Description 1", "jury_irregularity"),
            self._create_issue("Issue 2", "Description 2", "jury_irregularity"),
        ]
        
        merged = _merge_overlapping_grounds(issues)
        
        # Should return same list
        assert len(merged) == len(issues), f"Expected {len(issues)} issues, got {len(merged)}"
        print(f"PASS: Small issue list not merged - input={len(issues)}, output={len(merged)}")


class TestLegitimacyPanelContingentWarning:
    """Test that frontend LegitimacyPanel renders contingent warning"""
    
    def test_legitimacy_panel_has_contingent_warning_code(self):
        """Check that LegitimacyPanel.jsx has contingent warning rendering"""
        with open(FRONTEND_COMPONENTS_DIR / 'LegitimacyPanel.jsx', encoding='utf-8') as f:
            content = f.read()
        
        assert 'is_contingent' in content, "LegitimacyPanel should check is_contingent"
        assert 'contingent-warning' in content, "LegitimacyPanel should have contingent-warning testid"
        assert 'CONTINGENT' in content, "LegitimacyPanel should display CONTINGENT text"
        print("PASS: LegitimacyPanel.jsx has contingent warning rendering code")


class TestGroundsOfMeritWhitespacePre:
    """Test that GroundsOfMerit uses whitespace-pre-line for sub-particulars"""
    
    def test_grounds_description_has_whitespace_pre_line(self):
        """Check that description rendering uses whitespace-pre-line"""
        with open(FRONTEND_COMPONENTS_DIR / 'GroundsOfMerit.jsx', encoding='utf-8') as f:
            content = f.read()
        
        assert 'whitespace-pre-line' in content, "GroundsOfMerit should use whitespace-pre-line for descriptions"
        print("PASS: GroundsOfMerit.jsx uses whitespace-pre-line for description rendering")


class TestAuthenticationFlow:
    """Test login with provided credentials"""

    @pytest.mark.skipif(not BASE_URL, reason="REACT_APP_BACKEND_URL not set")
    def test_login_with_test_credentials(self):
        """Login with djkingy79@gmail.com should succeed"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "djkingy79@gmail.com",
                "password": "Cr1m1nalApp3al$2025"
            },
            timeout=15
        )
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "token" in data or "session_token" in data, f"No token in response: {data}"
        print("PASS: Login with test credentials succeeded")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
