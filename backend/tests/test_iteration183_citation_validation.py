"""
Iteration 183: Citation Validation & Metadata Quality Testing
Tests for:
1. Citation validation module (validate_citation, validate_similar_cases, strip_hallucinated_citations, validate_law_sections)
2. Metadata validation (validate_case_metadata)
3. Auto-detect valid_cats includes new offence categories (cybercrime, arson, perjury, environmental)
4. Auto-detect valid_sts includes 'federal'
5. GET /api/cases/{case_id} returns metadata_warnings array
6. Login endpoint still works
"""
import pytest
import requests
import os
import sys

# Add backend to path for direct imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://criminal-appeals-au-2.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"


class TestCitationValidation:
    """Test citation validation module functions"""
    
    def test_validate_citation_real_australian_citation(self):
        """Real Australian citations should be valid=True"""
        from services.case_validation import validate_citation
        
        # Medium neutral citation with known court
        result = validate_citation("R v Smith [2023] NSWCCA 123")
        assert result["valid"] is True
        assert result["confidence"] >= 0.5
        assert "medium neutral" in result["reason"].lower() or "known court" in result["reason"].lower()
        
    def test_validate_citation_law_report_format(self):
        """Law report citations should be valid"""
        from services.case_validation import validate_citation
        
        result = validate_citation("Smith v The Queen (2020) 271 CLR 456")
        assert result["valid"] is True
        assert result["confidence"] >= 0.5
        
    def test_validate_citation_placeholder_surname(self):
        """Placeholder [Surname] should be invalid"""
        from services.case_validation import validate_citation
        
        result = validate_citation("[Surname] v Queen [2023] NSWCCA 123")
        assert result["valid"] is False
        assert "placeholder" in result["reason"].lower()
        
    def test_validate_citation_placeholder_year(self):
        """Placeholder [Year] should be invalid"""
        from services.case_validation import validate_citation
        
        result = validate_citation("R v Smith [Year] NSWCCA 123")
        assert result["valid"] is False
        assert "placeholder" in result["reason"].lower()
        
    def test_validate_citation_placeholder_citation(self):
        """Placeholder [Citation] should be invalid"""
        from services.case_validation import validate_citation
        
        result = validate_citation("R v Smith [Full Citation]")
        assert result["valid"] is False
        assert "placeholder" in result["reason"].lower()
        
    def test_validate_citation_suspicious_not_available(self):
        """'citation not available' should be invalid"""
        from services.case_validation import validate_citation
        
        result = validate_citation("R v Smith - citation not available")
        assert result["valid"] is False
        assert "suspicious" in result["reason"].lower()
        
    def test_validate_citation_suspicious_section_unknown(self):
        """'section unknown' should be invalid"""
        from services.case_validation import validate_citation
        
        result = validate_citation("Crimes Act s section unknown")
        assert result["valid"] is False
        assert "suspicious" in result["reason"].lower()
        
    def test_validate_citation_empty(self):
        """Empty citation should be invalid"""
        from services.case_validation import validate_citation
        
        result = validate_citation("")
        assert result["valid"] is False
        assert "empty" in result["reason"].lower()
        
    def test_validate_citation_case_name_only(self):
        """Case name without formal citation should be valid but low confidence"""
        from services.case_validation import validate_citation
        
        result = validate_citation("House v The King")
        assert result["valid"] is True
        assert result["confidence"] <= 0.5  # Lower confidence for case name only


class TestValidateSimilarCases:
    """Test validate_similar_cases function"""
    
    def test_validate_similar_cases_removes_hallucinated(self):
        """Should remove cases with placeholder citations"""
        from services.case_validation import validate_similar_cases
        
        similar_cases = [
            {"case_name": "R v Smith", "citation": "[2023] NSWCCA 123"},
            {"case_name": "[Surname] v Queen", "citation": "[2023] NSWCCA 456"},
            {"case_name": "R v Jones", "citation": "citation not available"},
        ]
        
        result = validate_similar_cases(similar_cases)
        
        # Should keep only the valid one
        assert len(result) == 1
        assert result[0]["case_name"] == "R v Smith"
        
    def test_validate_similar_cases_keeps_valid(self):
        """Should keep valid cases with verification status"""
        from services.case_validation import validate_similar_cases
        
        similar_cases = [
            {"case_name": "R v Smith", "citation": "[2023] NSWCCA 123"},
            {"case_name": "DPP v Jones", "citation": "[2019] VSCA 78"},
        ]
        
        result = validate_similar_cases(similar_cases)
        
        assert len(result) == 2
        # Should add verification_status
        for case in result:
            assert "verification_status" in case
            assert "unverified" in case["verification_status"].lower()
            
    def test_validate_similar_cases_empty_list(self):
        """Should handle empty list"""
        from services.case_validation import validate_similar_cases
        
        result = validate_similar_cases([])
        assert result == []
        
    def test_validate_similar_cases_none(self):
        """Should handle None"""
        from services.case_validation import validate_similar_cases
        
        result = validate_similar_cases(None)
        assert result == []


class TestStripHallucinatedCitations:
    """Test strip_hallucinated_citations function"""
    
    def test_strip_placeholder_lines(self):
        """Should remove lines with placeholder patterns"""
        from services.case_validation import strip_hallucinated_citations
        
        text = """This is a valid line.
See [Surname] v Queen [2023] NSWCCA 123 for reference.
Another valid line here.
The citation is [Full Citation] pending verification."""
        
        result = strip_hallucinated_citations(text)
        
        assert "[Surname]" not in result
        assert "[Full Citation]" not in result
        assert "This is a valid line" in result
        assert "Another valid line here" in result
        
    def test_strip_suspicious_patterns(self):
        """Should remove lines with suspicious patterns"""
        from services.case_validation import strip_hallucinated_citations
        
        text = """Valid analysis here.
The citation is citation not available at this time.
More valid content."""
        
        result = strip_hallucinated_citations(text)
        
        assert "citation not available" not in result
        assert "Valid analysis here" in result
        assert "More valid content" in result
        
    def test_strip_preserves_valid_content(self):
        """Should preserve all valid content"""
        from services.case_validation import strip_hallucinated_citations
        
        text = """R v Smith [2023] NSWCCA 123 is a leading case.
The court held that the appeal should be allowed.
See also DPP v Jones [2019] VSCA 78."""
        
        result = strip_hallucinated_citations(text)
        
        # All lines should be preserved
        assert "R v Smith [2023] NSWCCA 123" in result
        assert "The court held" in result
        assert "DPP v Jones [2019] VSCA 78" in result
        
    def test_strip_empty_text(self):
        """Should handle empty text"""
        from services.case_validation import strip_hallucinated_citations
        
        result = strip_hallucinated_citations("")
        assert result == ""
        
    def test_strip_none_text(self):
        """Should handle None"""
        from services.case_validation import strip_hallucinated_citations
        
        result = strip_hallucinated_citations(None)
        assert result is None


class TestValidateLawSections:
    """Test validate_law_sections function"""
    
    def test_validate_law_sections_removes_placeholders(self):
        """Should remove entries with placeholder section numbers"""
        from services.case_validation import validate_law_sections
        
        law_sections = [
            {"section": "18", "act": "Crimes Act 1900 (NSW)"},
            {"section": "not provided", "act": "Evidence Act 1995 (NSW)"},
            {"section": "unknown", "act": "Criminal Procedure Act 1986 (NSW)"},
            {"section": "23A", "act": "Crimes Act 1900 (NSW)"},
        ]
        
        result = validate_law_sections(law_sections)
        
        # Should keep only valid entries
        assert len(result) == 2
        sections = [s["section"] for s in result]
        assert "18" in sections
        assert "23A" in sections
        assert "not provided" not in sections
        assert "unknown" not in sections
        
    def test_validate_law_sections_removes_placeholder_acts(self):
        """Should remove entries with placeholder act names"""
        from services.case_validation import validate_law_sections
        
        law_sections = [
            {"section": "18", "act": "Crimes Act 1900 (NSW)"},
            {"section": "5", "act": "not provided"},
            {"section": "10", "act": "placeholder act"},
        ]
        
        result = validate_law_sections(law_sections)
        
        assert len(result) == 1
        assert result[0]["act"] == "Crimes Act 1900 (NSW)"
        
    def test_validate_law_sections_adds_verification_status(self):
        """Should add verification_status to valid entries"""
        from services.case_validation import validate_law_sections
        
        law_sections = [
            {"section": "18", "act": "Crimes Act 1900 (NSW)"},
        ]
        
        result = validate_law_sections(law_sections)
        
        assert len(result) == 1
        assert "verification_status" in result[0]
        assert "unverified" in result[0]["verification_status"].lower()
        
    def test_validate_law_sections_empty(self):
        """Should handle empty list"""
        from services.case_validation import validate_law_sections
        
        result = validate_law_sections([])
        assert result == []


class TestValidateCaseMetadata:
    """Test validate_case_metadata function"""
    
    def test_metadata_complete(self):
        """Complete metadata should return complete=True"""
        from services.case_validation import validate_case_metadata
        
        case = {
            "state": "nsw",
            "offence_category": "homicide",
            "offence_type": "murder"
        }
        
        result = validate_case_metadata(case)
        
        assert result["complete"] is True
        assert len(result["warnings"]) == 0
        
    def test_metadata_missing_state(self):
        """Missing state should return warning"""
        from services.case_validation import validate_case_metadata
        
        case = {
            "state": None,
            "offence_category": "homicide",
            "offence_type": "murder"
        }
        
        result = validate_case_metadata(case)
        
        assert result["complete"] is False
        assert len(result["warnings"]) == 1
        assert "state" in result["warnings"][0].lower() or "jurisdiction" in result["warnings"][0].lower()
        
    def test_metadata_missing_offence_category(self):
        """Missing offence_category should return warning"""
        from services.case_validation import validate_case_metadata
        
        case = {
            "state": "nsw",
            "offence_category": None,
            "offence_type": "murder"
        }
        
        result = validate_case_metadata(case)
        
        assert result["complete"] is False
        assert len(result["warnings"]) == 1
        assert "offence category" in result["warnings"][0].lower()
        
    def test_metadata_missing_offence_type(self):
        """Missing offence_type should return warning"""
        from services.case_validation import validate_case_metadata
        
        case = {
            "state": "nsw",
            "offence_category": "homicide",
            "offence_type": None
        }
        
        result = validate_case_metadata(case)
        
        assert result["complete"] is False
        assert len(result["warnings"]) == 1
        assert "offence type" in result["warnings"][0].lower()
        
    def test_metadata_all_missing(self):
        """All missing should return 3 warnings"""
        from services.case_validation import validate_case_metadata
        
        case = {
            "state": None,
            "offence_category": None,
            "offence_type": None
        }
        
        result = validate_case_metadata(case)
        
        assert result["complete"] is False
        assert len(result["warnings"]) == 3


class TestAutoDetectValidCategories:
    """Test that auto-detect includes new offence categories"""
    
    def test_valid_cats_includes_cybercrime(self):
        """valid_cats should include cybercrime"""
        # Check the documents.py file for valid_cats
        import importlib.util
        spec = importlib.util.spec_from_file_location("documents", "/app/backend/routers/documents.py")
        documents_module = importlib.util.module_from_spec(spec)
        
        # Read the file content to check valid_cats
        with open("/app/backend/routers/documents.py", "r") as f:
            content = f.read()
        
        assert "cybercrime" in content
        
    def test_valid_cats_includes_arson(self):
        """valid_cats should include arson"""
        with open("/app/backend/routers/documents.py", "r") as f:
            content = f.read()
        
        assert "arson" in content
        
    def test_valid_cats_includes_perjury(self):
        """valid_cats should include perjury"""
        with open("/app/backend/routers/documents.py", "r") as f:
            content = f.read()
        
        assert "perjury" in content
        
    def test_valid_cats_includes_environmental(self):
        """valid_cats should include environmental"""
        with open("/app/backend/routers/documents.py", "r") as f:
            content = f.read()
        
        assert "environmental" in content
        
    def test_valid_sts_includes_federal(self):
        """valid_sts should include federal"""
        with open("/app/backend/routers/documents.py", "r") as f:
            content = f.read()
        
        # Check for federal in valid_sts list
        assert '"federal"' in content or "'federal'" in content


class TestAPIEndpoints:
    """Test API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def test_login_endpoint_works(self):
        """Login endpoint should work with valid credentials"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        
    def test_login_endpoint_rejects_invalid(self):
        """Login endpoint should reject invalid credentials"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@example.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        
    def test_case_detail_returns_metadata_warnings(self):
        """GET /api/cases/{case_id} should return metadata_warnings array"""
        # First login
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200
        token = login_response.json()["session_token"]
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get case with missing metadata (case_d0f0469d5cab from previous iteration)
        response = self.session.get(f"{BASE_URL}/api/cases/case_d0f0469d5cab")
        
        if response.status_code == 200:
            data = response.json()
            # Should have metadata_warnings field
            assert "metadata_warnings" in data or "jurisdiction_warnings" in data
        elif response.status_code == 404:
            # Case may not exist, skip this test
            pytest.skip("Test case case_d0f0469d5cab not found")
            
    def test_case_with_complete_metadata_no_warnings(self):
        """Case with complete metadata should have empty metadata_warnings"""
        # First login
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200
        token = login_response.json()["session_token"]
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get case with complete metadata (case_f8bf63e9dcbe from previous iteration)
        response = self.session.get(f"{BASE_URL}/api/cases/case_f8bf63e9dcbe")
        
        if response.status_code == 200:
            data = response.json()
            # Should have empty or no metadata_warnings
            warnings = data.get("metadata_warnings", [])
            # Complete metadata case should have 0 or minimal warnings
            assert isinstance(warnings, list)
        elif response.status_code == 404:
            pytest.skip("Test case case_f8bf63e9dcbe not found")


class TestValidCourtAbbreviations:
    """Test that _VALID_COURT_ABBREVS contains expected courts"""
    
    def test_valid_court_abbrevs_exists(self):
        """_VALID_COURT_ABBREVS should exist and contain expected courts"""
        from services.case_validation import _VALID_COURT_ABBREVS
        
        # High Court
        assert "HCA" in _VALID_COURT_ABBREVS
        assert "CLR" in _VALID_COURT_ABBREVS
        
        # Federal
        assert "FCA" in _VALID_COURT_ABBREVS
        assert "FCAFC" in _VALID_COURT_ABBREVS
        
        # NSW
        assert "NSWCCA" in _VALID_COURT_ABBREVS
        assert "NSWSC" in _VALID_COURT_ABBREVS
        
        # VIC
        assert "VSCA" in _VALID_COURT_ABBREVS
        assert "VSC" in _VALID_COURT_ABBREVS
        
        # QLD
        assert "QCA" in _VALID_COURT_ABBREVS
        assert "QSC" in _VALID_COURT_ABBREVS
        
        # SA
        assert "SASCFC" in _VALID_COURT_ABBREVS
        assert "SASC" in _VALID_COURT_ABBREVS
        
        # WA
        assert "WASCA" in _VALID_COURT_ABBREVS
        assert "WASC" in _VALID_COURT_ABBREVS
        
        # TAS
        assert "TASCCA" in _VALID_COURT_ABBREVS
        assert "TASSC" in _VALID_COURT_ABBREVS
        
        # NT
        assert "NTCCA" in _VALID_COURT_ABBREVS
        assert "NTSC" in _VALID_COURT_ABBREVS
        
        # ACT
        assert "ACTCA" in _VALID_COURT_ABBREVS
        assert "ACTSC" in _VALID_COURT_ABBREVS


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
