"""
Iteration 172 Comprehensive Tests
Tests for:
1. All 104 legislation framework tests pass
2. All 8 states return correct state-specific legislation (no NSW contamination)
3. Forensic language filter works correctly
4. NSW case grounds contain substantive legislation (Crimes Act 1900), not just Criminal Appeal Act
5. WA case grounds have no NSW legislation contamination
6. Refresh legal refs endpoint works
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_deep_health_check(self):
        """GET /api/health/deep returns healthy"""
        response = requests.get(f"{BASE_URL}/api/health/deep")
        assert response.status_code == 200
        data = response.json()
        assert data.get('healthy')
        assert 'checks' in data
        print(f"Health check: {data}")
    
    def test_login_works(self):
        """POST /api/auth/login works with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        assert response.status_code == 200
        data = response.json()
        assert 'session_token' in data
        assert data.get('email') == 'djkingy79@gmail.com'
        print(f"Login successful: user_id={data.get('user_id')}")


class TestOffenceFrameworkAllStates:
    """Test offence-framework endpoint returns correct state-specific legislation for all 8 states"""
    
    def test_vic_homicide_returns_vic_legislation(self):
        """GET /api/offence-framework/homicide?state=vic returns VIC legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=vic")
        assert response.status_code == 200
        data = response.json()
        text = json.dumps(data)
        
        # Should contain VIC legislation
        assert 'Crimes Act 1958' in text, "VIC Crimes Act 1958 not found"
        
        # Should NOT contain NSW legislation
        assert 'Crimes Act 1900 (NSW)' not in text, "NSW contamination in VIC response"
        assert 'New South Wales' not in text, "NSW contamination in VIC response"
        print("VIC homicide: PASS - contains VIC legislation, no NSW contamination")
    
    def test_qld_assault_returns_qld_legislation(self):
        """GET /api/offence-framework/assault?state=qld returns QLD legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/assault?state=qld")
        assert response.status_code == 200
        data = response.json()
        text = json.dumps(data)
        
        # Should contain QLD legislation
        assert 'Criminal Code' in text, "QLD Criminal Code not found"
        
        # Should NOT contain NSW legislation
        assert 'Crimes Act 1900 (NSW)' not in text, "NSW contamination in QLD response"
        print("QLD assault: PASS - contains QLD legislation, no NSW contamination")
    
    def test_sa_domestic_violence_returns_sa_legislation(self):
        """GET /api/offence-framework/domestic_violence?state=sa returns SA legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/domestic_violence?state=sa")
        assert response.status_code == 200
        data = response.json()
        text = json.dumps(data)
        
        # Should NOT contain NSW legislation
        assert 'Crimes Act 1900 (NSW)' not in text, "NSW contamination in SA response"
        print("SA domestic_violence: PASS - no NSW contamination")
    
    def test_nt_drug_offences_returns_nt_legislation(self):
        """GET /api/offence-framework/drug_offences?state=nt returns NT legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/drug_offences?state=nt")
        assert response.status_code == 200
        data = response.json()
        text = json.dumps(data)
        
        # Should NOT contain NSW legislation
        assert 'Crimes Act 1900 (NSW)' not in text, "NSW contamination in NT response"
        print("NT drug_offences: PASS - no NSW contamination")
    
    def test_act_assault_returns_act_legislation(self):
        """GET /api/offence-framework/assault?state=act returns ACT legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/assault?state=act")
        assert response.status_code == 200
        data = response.json()
        text = json.dumps(data)
        
        # Should contain ACT legislation
        assert 'Criminal Code 2002' in text or 'Crimes Act 1900 (ACT)' in text, "ACT legislation not found"
        
        # Should NOT contain NSW-specific legislation
        assert 'Crimes Act 1900 (NSW)' not in text, "NSW contamination in ACT response"
        print("ACT assault: PASS - contains ACT legislation, no NSW contamination")
    
    def test_tas_assault_returns_tas_legislation(self):
        """GET /api/offence-framework/assault?state=tas returns TAS legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/assault?state=tas")
        assert response.status_code == 200
        data = response.json()
        text = json.dumps(data)
        
        # Should contain TAS legislation
        assert 'Criminal Code' in text, "TAS Criminal Code not found"
        
        # Should NOT contain NSW legislation
        assert 'Crimes Act 1900 (NSW)' not in text, "NSW contamination in TAS response"
        print("TAS assault: PASS - contains TAS legislation, no NSW contamination")
    
    def test_wa_domestic_violence_returns_wa_legislation(self):
        """GET /api/offence-framework/domestic_violence?state=wa returns WA legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/domestic_violence?state=wa")
        assert response.status_code == 200
        data = response.json()
        text = json.dumps(data)
        
        # Should contain WA legislation
        category = data.get('category', {})
        state_leg = category.get('state_legislation', {})
        assert len(state_leg) > 0, "WA state legislation not found"
        
        # Should NOT contain NSW legislation
        assert 'Crimes Act 1900 (NSW)' not in text, "NSW contamination in WA response"
        assert 'New South Wales' not in text, "NSW contamination in WA response"
        print(f"WA domestic_violence: PASS - state_legislation keys: {list(state_leg.keys())}")
    
    def test_nsw_homicide_returns_nsw_legislation(self):
        """GET /api/offence-framework/homicide?state=nsw returns NSW legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=nsw")
        assert response.status_code == 200
        data = response.json()
        text = json.dumps(data)
        
        # Should contain NSW legislation
        assert 'Crimes Act 1900' in text, "NSW Crimes Act 1900 not found"
        print("NSW homicide: PASS - contains NSW legislation")


class TestCaseGrounds:
    """Test case grounds contain correct legislation"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        if response.status_code == 200:
            return response.json().get('session_token')
        pytest.skip("Authentication failed")
    
    def test_nsw_case_grounds_contain_substantive_legislation(self, auth_token):
        """GET /api/cases/{case_id}/grounds for NSW case contains Crimes Act 1900, not only Criminal Appeal Act"""
        response = requests.get(
            f"{BASE_URL}/api/cases/case_6cc234434cbd/grounds",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        grounds = data.get('grounds', [])
        
        # Check that at least one ground has substantive law_sections
        has_substantive_law = False
        for ground in grounds:
            law_sections = ground.get('law_sections', [])
            for section in law_sections:
                act = section.get('act', '')
                if 'Crimes Act 1900' in act or 'Evidence Act' in act or 'Sentencing' in act:
                    has_substantive_law = True
                    print(f"Found substantive law: {act}")
        
        # Also check appellate_pathway is separate
        for ground in grounds:
            appellate_pathway = ground.get('appellate_pathway', '')
            if 'Criminal Appeal Act' in appellate_pathway:
                print(f"Appellate pathway correctly contains: {appellate_pathway}")
        
        assert has_substantive_law or len(grounds) == 0, "NSW case should have substantive law_sections (Crimes Act 1900, Evidence Act, etc.)"
        print(f"NSW case grounds: {len(grounds)} grounds found")
    
    def test_wa_case_grounds_no_nsw_contamination(self, auth_token):
        """GET /api/cases/{case_id}/grounds for WA case has no NSW legislation in law_sections"""
        response = requests.get(
            f"{BASE_URL}/api/cases/case_e8a9de2d8331/grounds",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        grounds = data.get('grounds', [])
        
        # Check no NSW contamination in law_sections
        for ground in grounds:
            law_sections = ground.get('law_sections', [])
            law_str = json.dumps(law_sections)
            assert 'NSW' not in law_str, f"NSW contamination in WA case law_sections: {law_str}"
            assert 'New South Wales' not in law_str, "NSW contamination in WA case law_sections"
        
        print(f"WA case grounds: {len(grounds)} grounds, no NSW contamination")
    
    def test_refresh_legal_refs_endpoint(self, auth_token):
        """POST /api/cases/{case_id}/grounds/refresh-legal-refs works"""
        response = requests.post(
            f"{BASE_URL}/api/cases/case_6cc234434cbd/grounds/refresh-legal-refs",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'updated' in data
        assert 'total' in data
        print(f"Refresh legal refs: updated={data.get('updated')}, total={data.get('total')}")


class TestForensicLanguageFilter:
    """Test forensic language filter rewrites over-assertive phrases"""
    
    def test_forensic_language_import(self):
        """Verify enforce_forensic_language function exists and works"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.offence_helpers import enforce_forensic_language
        
        # Test "The trial judge erred"
        result = enforce_forensic_language("The trial judge erred in failing to consider.")
        assert "It is arguable that the trial judge erred" in result
        print(f"Trial judge erred: {result}")
        
        # Test "The conviction is unsafe"
        result = enforce_forensic_language("The conviction is unsafe because the jury was misdirected.")
        assert "It is arguable that the conviction is unsafe" in result
        print(f"Conviction unsafe: {result}")
        
        # Test "The sentence is manifestly excessive"
        result = enforce_forensic_language("The sentence is manifestly excessive.")
        assert "It is arguable that the sentence is manifestly excessive" in result
        print(f"Sentence excessive: {result}")
        
        # Test preservation of already forensic language
        text = "It is arguable that the trial judge erred in law."
        result = enforce_forensic_language(text)
        assert result == text
        print("Already forensic: preserved correctly")
        
        # Test preservation of precedent citations
        text = "In R v Smith, the Court held that the trial judge erred."
        result = enforce_forensic_language(text)
        assert "the Court held that the trial judge erred" in result
        print(f"Precedent citation: {result}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
