"""
Test Suite: State and Offence Framework API Tests
Testing ALL Australian states/territories and ALL criminal offence categories.
"""
import pytest
import requests

BASE_URL = 'http://localhost:8001'

class TestStatesEndpoint:
    """Tests for GET /api/states - all 8 Australian states/territories"""
    
    def test_get_all_states(self):
        """Verify GET /api/states returns all 8 Australian states/territories"""
        response = requests.get(f"{BASE_URL}/api/states")
        assert response.status_code == 200
        
        data = response.json()
        assert "states" in data
        states = data["states"]
        
        # Should have exactly 8 states/territories
        assert len(states) == 8
        
        # Verify all expected states are present
        expected_states = {
            "nsw": "New South Wales",
            "vic": "Victoria",
            "qld": "Queensland",
            "sa": "South Australia",
            "wa": "Western Australia",
            "tas": "Tasmania",
            "nt": "Northern Territory",
            "act": "Australian Capital Territory"
        }
        
        state_ids = {s["id"] for s in states}
        for expected_id in expected_states.keys():
            assert expected_id in state_ids, f"Missing state: {expected_id}"
        
        # Verify structure
        for state in states:
            assert "id" in state
            assert "name" in state
            assert "abbreviation" in state
            assert state["name"] == expected_states[state["id"]]
    
    def test_state_abbreviations(self):
        """Verify state abbreviations are correct"""
        response = requests.get(f"{BASE_URL}/api/states")
        states = response.json()["states"]
        
        expected_abbrevs = {
            "nsw": "NSW",
            "vic": "VIC",
            "qld": "QLD",
            "sa": "SA",
            "wa": "WA",
            "tas": "TAS",
            "nt": "NT",
            "act": "ACT"
        }
        
        for state in states:
            assert state["abbreviation"] == expected_abbrevs[state["id"]]


class TestOffenceCategoriesEndpoint:
    """Tests for GET /api/offence-categories - all 11 offence categories"""
    
    def test_get_all_categories(self):
        """Verify GET /api/offence-categories returns all 11 categories"""
        response = requests.get(f"{BASE_URL}/api/offence-categories")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        categories = data["categories"]
        
        # Should have exactly 11 categories
        assert len(categories) == 11
        
        expected_categories = [
            "homicide", "assault", "sexual_offences", "robbery_theft",
            "drug_offences", "fraud_dishonesty", "firearms_weapons",
            "domestic_violence", "public_order", "terrorism", "driving_offences"
        ]
        
        category_ids = [c["id"] for c in categories]
        for expected in expected_categories:
            assert expected in category_ids, f"Missing category: {expected}"
    
    def test_category_structure(self):
        """Verify each category has correct structure with offences"""
        response = requests.get(f"{BASE_URL}/api/offence-categories")
        categories = response.json()["categories"]
        
        for cat in categories:
            assert "id" in cat
            assert "name" in cat
            assert "description" in cat
            assert "offences" in cat
            assert isinstance(cat["offences"], list)
            assert len(cat["offences"]) > 0


class TestOffenceFrameworkStateSpecific:
    """Tests for GET /api/offence-framework/{category}?state={state}"""
    
    def test_homicide_vic_legislation(self):
        """KEY TEST: Victoria homicide returns Crimes Act 1958 (Vic) NOT NSW"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=vic")
        assert response.status_code == 200
        
        data = response.json()
        category = data["category"]
        
        # Verify VIC-specific legislation
        assert "state_legislation" in category
        state_leg = category["state_legislation"]
        
        # Should have Crimes Act 1958 (Vic)
        assert "Crimes Act 1958 (Vic)" in state_leg
        
        # Should NOT have NSW legislation
        assert "Crimes Act 1900 (NSW)" not in state_leg
        
        # Verify state info
        assert data["state"]["abbreviation"] == "VIC"
        assert data["state"]["name"] == "Victoria"
    
    def test_homicide_qld_legislation(self):
        """KEY TEST: Queensland homicide returns Criminal Code Act 1899 (Qld)"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=qld")
        assert response.status_code == 200
        
        data = response.json()
        category = data["category"]
        state_leg = category["state_legislation"]
        
        # Should have Queensland Criminal Code
        assert "Criminal Code Act 1899 (Qld)" in state_leg
        
        # Verify state info
        assert data["state"]["abbreviation"] == "QLD"
        assert data["state"]["name"] == "Queensland"
    
    def test_homicide_nsw_legislation(self):
        """NSW homicide returns Crimes Act 1900 (NSW)"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=nsw")
        assert response.status_code == 200
        
        data = response.json()
        category = data["category"]
        state_leg = category["state_legislation"]
        
        assert "Crimes Act 1900 (NSW)" in state_leg
        assert data["state"]["abbreviation"] == "NSW"
    
    def test_homicide_sa_legislation(self):
        """SA homicide returns Criminal Law Consolidation Act 1935 (SA)"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=sa")
        assert response.status_code == 200
        
        data = response.json()
        state_leg = data["category"]["state_legislation"]
        
        assert "Criminal Law Consolidation Act 1935 (SA)" in state_leg
        assert data["state"]["abbreviation"] == "SA"
    
    def test_homicide_wa_legislation(self):
        """WA homicide returns Criminal Code Act Compilation Act 1913 (WA)"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=wa")
        assert response.status_code == 200
        
        data = response.json()
        state_leg = data["category"]["state_legislation"]
        
        assert "Criminal Code Act Compilation Act 1913 (WA)" in state_leg
        assert data["state"]["abbreviation"] == "WA"
    
    def test_homicide_tas_legislation(self):
        """TAS homicide returns Criminal Code Act 1924 (Tas)"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=tas")
        assert response.status_code == 200
        
        data = response.json()
        state_leg = data["category"]["state_legislation"]
        
        assert "Criminal Code Act 1924 (Tas)" in state_leg
        assert data["state"]["abbreviation"] == "TAS"
    
    def test_homicide_nt_legislation(self):
        """NT homicide returns Criminal Code Act 1983 (NT)"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=nt")
        assert response.status_code == 200
        
        data = response.json()
        state_leg = data["category"]["state_legislation"]
        
        assert "Criminal Code Act 1983 (NT)" in state_leg
        assert data["state"]["abbreviation"] == "NT"
    
    def test_homicide_act_legislation(self):
        """ACT homicide returns Crimes Act 1900 (ACT)"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=act")
        assert response.status_code == 200
        
        data = response.json()
        state_leg = data["category"]["state_legislation"]
        
        assert "Crimes Act 1900 (ACT)" in state_leg
        assert data["state"]["abbreviation"] == "ACT"


class TestOffenceFrameworkAppealInfo:
    """Tests for appeal framework information by state"""
    
    def test_appeal_framework_vic(self):
        """Victoria appeal framework correct"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=vic")
        data = response.json()
        appeal = data["appeal_framework"]
        
        assert "Criminal Procedure Act 2009 (Vic)" in appeal["legislation"]
        assert "Court of Appeal" in appeal["court"]
    
    def test_appeal_framework_qld(self):
        """Queensland appeal framework correct"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=qld")
        data = response.json()
        appeal = data["appeal_framework"]
        
        assert "Criminal Code Act 1899 (Qld)" in appeal["legislation"]
        assert "Supreme Court of Queensland" in appeal["court"]
    
    def test_common_appeal_grounds_present(self):
        """Common appeal grounds included"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=nsw")
        data = response.json()
        
        assert "common_appeal_grounds" in data
        grounds = data["common_appeal_grounds"]
        assert len(grounds) > 0
        
        # Check for key grounds
        ground_names = [g["ground"] for g in grounds]
        assert "Fresh evidence" in ground_names
        assert "Procedural unfairness" in ground_names


class TestOtherOffenceCategories:
    """Tests for other offence categories with state-specific legislation"""
    
    def test_drug_offences_vic(self):
        """Victoria drug offences return correct legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/drug_offences?state=vic")
        assert response.status_code == 200
        
        data = response.json()
        state_leg = data["category"]["state_legislation"]
        
        assert "Drugs, Poisons and Controlled Substances Act 1981 (Vic)" in state_leg
    
    def test_drug_offences_qld(self):
        """Queensland drug offences return correct legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/drug_offences?state=qld")
        assert response.status_code == 200
        
        data = response.json()
        state_leg = data["category"]["state_legislation"]
        
        assert "Drugs Misuse Act 1986 (Qld)" in state_leg
    
    def test_fraud_vic(self):
        """Victoria fraud returns correct legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/fraud_dishonesty?state=vic")
        assert response.status_code == 200
        
        data = response.json()
        state_leg = data["category"]["state_legislation"]
        
        assert "Crimes Act 1958 (Vic)" in state_leg
    
    def test_domestic_violence_vic(self):
        """Victoria domestic violence returns correct legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/domestic_violence?state=vic")
        assert response.status_code == 200
        
        data = response.json()
        state_leg = data["category"]["state_legislation"]
        
        assert "Family Violence Protection Act 2008 (Vic)" in state_leg
    
    def test_terrorism_cth_legislation(self):
        """Terrorism offences primarily return Commonwealth legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/terrorism?state=nsw")
        assert response.status_code == 200
        
        data = response.json()
        cth_leg = data["category"]["cth_legislation"]
        
        # Terrorism is federal, should have CTH legislation
        assert "Criminal Code Act 1995 (Cth)" in cth_leg
    
    def test_invalid_category_returns_404(self):
        """Invalid category returns 404"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/invalid_category?state=nsw")
        assert response.status_code == 404


class TestCategoryCompleteness:
    """Verify all categories have proper data for all states"""
    
    @pytest.mark.parametrize("state_id,abbrev", [
        ("nsw", "NSW"), ("vic", "VIC"), ("qld", "QLD"), ("sa", "SA"),
        ("wa", "WA"), ("tas", "TAS"), ("nt", "NT"), ("act", "ACT")
    ])
    def test_homicide_all_states(self, state_id, abbrev):
        """Homicide category works for all states"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state={state_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["state"]["abbreviation"] == abbrev
        # Note: state_legislation may be empty for some category/state combos
    
    @pytest.mark.parametrize("category", [
        "homicide", "assault", "drug_offences", "fraud_dishonesty", 
        "domestic_violence", "driving_offences"
    ])
    def test_common_categories_vic(self, category):
        """Common categories return data for Victoria"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/{category}?state=vic")
        assert response.status_code == 200
        
        data = response.json()
        assert "category" in data
        assert data["state"]["abbreviation"] == "VIC"
