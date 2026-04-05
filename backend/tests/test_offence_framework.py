"""
Tests for Offence Framework Integration
Testing offence categories API and case creation with offence types
"""

import pytest
import requests

BASE_URL = 'http://localhost:8001'

# Expected 11 offence categories
EXPECTED_CATEGORIES = [
    "homicide", "assault", "sexual_offences", "robbery_theft", "drug_offences",
    "fraud_dishonesty", "firearms_weapons", "domestic_violence", "public_order",
    "terrorism", "driving_offences"
]


class TestOffenceCategories:
    """Test offence categories API endpoint - public endpoint, no auth required"""
    
    def test_get_offence_categories_returns_all_11(self):
        """Verify GET /api/offence-categories returns all 11 categories"""
        response = requests.get(f"{BASE_URL}/api/offence-categories")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "categories" in data
        assert len(data["categories"]) == 11, f"Expected 11 categories, got {len(data['categories'])}"
        
        # Verify all expected categories are present
        category_ids = [cat["id"] for cat in data["categories"]]
        for expected in EXPECTED_CATEGORIES:
            assert expected in category_ids, f"Missing category: {expected}"
    
    def test_offence_category_structure(self):
        """Verify each category has required fields"""
        response = requests.get(f"{BASE_URL}/api/offence-categories")
        data = response.json()
        
        for category in data["categories"]:
            assert "id" in category
            assert "name" in category
            assert "description" in category
            assert "offences" in category
            assert isinstance(category["offences"], list)
            assert len(category["offences"]) > 0, f"Category {category['id']} has no offences"
    
    def test_drug_offences_category_offences(self):
        """Verify drug_offences category has correct offences list"""
        response = requests.get(f"{BASE_URL}/api/offence-categories")
        data = response.json()
        
        drug_cat = next((c for c in data["categories"] if c["id"] == "drug_offences"), None)
        assert drug_cat is not None
        
        assert "Drug Possession" in drug_cat["offences"]
        assert "Drug Supply" in drug_cat["offences"]
        assert "Drug Trafficking" in drug_cat["offences"]


class TestOffenceFrameworkDetails:
    """Test offence framework detail endpoint"""
    
    def test_get_drug_offences_framework(self):
        """Verify GET /api/offence-framework/drug_offences returns detailed framework"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/drug_offences")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "category" in data
        assert "common_appeal_grounds" in data
        assert "human_rights" in data
        
        # Verify category details
        assert data["category"]["name"] == "Drug Offences"
        assert "nsw_legislation" in data["category"]
        assert "cth_legislation" in data["category"]
        assert "defences" in data["category"]
        assert "key_elements" in data["category"]
    
    def test_get_homicide_framework(self):
        """Verify GET /api/offence-framework/homicide returns detailed framework"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["category"]["name"] == "Homicide"
        assert "Murder" in data["category"]["offences"]
        assert "Manslaughter" in data["category"]["offences"]
    
    def test_invalid_offence_category_returns_404(self):
        """Verify invalid category returns 404"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/invalid_category")
        
        assert response.status_code == 404
        assert "not found" in response.json().get("detail", "").lower()


class TestCaseCreationWithOffenceType:
    """Test case creation with offence type - requires auth"""
    
    @pytest.fixture(autouse=True)
    def setup_session(self):
        """Create test user and session"""
        import subprocess
        result = subprocess.run([
            "mongosh", "--quiet", "--eval", """
            use('test_database');
            var userId = 'test-user-offence-case-' + Date.now();
            var sessionToken = 'test_session_offence_case_' + Date.now();
            db.users.insertOne({
              user_id: userId,
              email: 'test.offence.case.' + Date.now() + '@example.com',
              name: 'Offence Case Test User',
              terms_accepted: true,
              created_at: new Date()
            });
            db.user_sessions.insertOne({
              user_id: userId,
              session_token: sessionToken,
              expires_at: new Date(Date.now() + 7*24*60*60*1000),
              created_at: new Date()
            });
            print(sessionToken);
            """
        ], capture_output=True, text=True)
        
        self.session_token = result.stdout.strip().split('\n')[-1]
        self.headers = {
            "Authorization": f"Bearer {self.session_token}",
            "Content-Type": "application/json"
        }
        yield
        # Cleanup will happen automatically
    
    def test_create_case_with_drug_offences(self):
        """Create case with drug_offences category and specific offence type"""
        case_data = {
            "title": "R v Test - Drug Supply Appeal",
            "defendant_name": "Test Defendant",
            "case_number": "2024/TEST001",
            "offence_category": "drug_offences",
            "offence_type": "Drug Supply"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cases",
            headers=self.headers,
            json=case_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["offence_category"] == "drug_offences"
        assert data["offence_type"] == "Drug Supply"
        assert data["title"] == "R v Test - Drug Supply Appeal"
        
        # Store case_id for verification
        case_id = data["case_id"]
        
        # Verify GET returns same offence fields
        get_response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}",
            headers=self.headers
        )
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["offence_category"] == "drug_offences"
        assert get_data["offence_type"] == "Drug Supply"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/cases/{case_id}", headers=self.headers)
    
    def test_create_case_with_assault_category(self):
        """Create case with assault category"""
        case_data = {
            "title": "R v Test - GBH Appeal",
            "defendant_name": "Test Defendant",
            "offence_category": "assault",
            "offence_type": "Assault Occasioning GBH"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cases",
            headers=self.headers,
            json=case_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["offence_category"] == "assault"
        assert data["offence_type"] == "Assault Occasioning GBH"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/cases/{data['case_id']}", headers=self.headers)
    
    def test_create_case_default_offence_category(self):
        """Create case without offence fields - should default to homicide"""
        case_data = {
            "title": "R v Test - Default Category",
            "defendant_name": "Test Defendant"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cases",
            headers=self.headers,
            json=case_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Default is homicide
        assert data["offence_category"] == "homicide"
        assert data["offence_type"] is None or data["offence_type"] == ""
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/cases/{data['case_id']}", headers=self.headers)
    
    def test_update_case_offence_type(self):
        """Create case and update offence type"""
        # Create
        case_data = {
            "title": "R v Test - Update Offence",
            "defendant_name": "Test Defendant",
            "offence_category": "homicide",
            "offence_type": "Murder"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/cases",
            headers=self.headers,
            json=case_data
        )
        
        assert create_response.status_code == 200
        case_id = create_response.json()["case_id"]
        
        # Update
        update_data = {
            "title": "R v Test - Update Offence",
            "defendant_name": "Test Defendant",
            "offence_category": "drug_offences",
            "offence_type": "Drug Trafficking"
        }
        
        update_response = requests.put(
            f"{BASE_URL}/api/cases/{case_id}",
            headers=self.headers,
            json=update_data
        )
        
        assert update_response.status_code == 200
        updated_data = update_response.json()
        
        assert updated_data["offence_category"] == "drug_offences"
        assert updated_data["offence_type"] == "Drug Trafficking"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/cases/{case_id}", headers=self.headers)


class TestFullOffenceFramework:
    """Test the full offence framework endpoint"""
    
    def test_get_full_framework(self):
        """Verify GET /api/offence-framework returns complete framework"""
        response = requests.get(f"{BASE_URL}/api/offence-framework")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "categories" in data
        assert "common_appeal_grounds" in data
        assert "human_rights" in data
        assert "appeal_framework" in data
        
        assert len(data["categories"]) == 11


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
