# Iteration 42: API tests for Appeal Case Manager
# Tests health check, offence-categories, states endpoints
# Verifies DO NOT UNDO changes did not break functionality

import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'


class TestHealthCheck:
    """Health check endpoint tests"""
    
    def test_health_check_returns_200(self):
        """Verify /api/health returns 200 with healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
        print(f"Health check passed: {data}")


class TestOffenceCategories:
    """Tests for /api/offence-categories endpoint"""
    
    def test_offence_categories_returns_11_categories(self):
        """Verify /api/offence-categories returns exactly 11 categories"""
        response = requests.get(f"{BASE_URL}/api/offence-categories", timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        assert "categories" in data
        categories = data["categories"]
        assert len(categories) == 11, f"Expected 11 categories, got {len(categories)}"
        
        # Verify expected category IDs
        expected_ids = [
            "homicide", "assault", "sexual_offences", "robbery_theft",
            "drug_offences", "fraud_dishonesty", "firearms_weapons",
            "domestic_violence", "public_order", "terrorism", "driving_offences"
        ]
        category_ids = [c["id"] for c in categories]
        for expected_id in expected_ids:
            assert expected_id in category_ids, f"Missing category: {expected_id}"
        
        print(f"All 11 offence categories present: {category_ids}")
    
    def test_offence_categories_have_required_fields(self):
        """Verify each category has id, name, description, offences"""
        response = requests.get(f"{BASE_URL}/api/offence-categories", timeout=10)
        assert response.status_code == 200
        
        for category in response.json()["categories"]:
            assert "id" in category, f"Category missing 'id'"
            assert "name" in category, f"Category missing 'name'"
            assert "description" in category, f"Category missing 'description'"
            assert "offences" in category, f"Category missing 'offences'"
            assert isinstance(category["offences"], list), "Offences should be a list"
            assert len(category["offences"]) > 0, f"Category {category['id']} has no offences"


class TestStates:
    """Tests for /api/states endpoint"""
    
    def test_states_returns_8_states(self):
        """Verify /api/states returns exactly 8 Australian states/territories"""
        response = requests.get(f"{BASE_URL}/api/states", timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        assert "states" in data
        states = data["states"]
        assert len(states) == 8, f"Expected 8 states, got {len(states)}"
        
        # Verify expected state IDs
        expected_ids = ["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act"]
        state_ids = [s["id"] for s in states]
        for expected_id in expected_ids:
            assert expected_id in state_ids, f"Missing state: {expected_id}"
        
        print(f"All 8 Australian states/territories present: {state_ids}")
    
    def test_states_have_required_fields(self):
        """Verify each state has id, name, abbreviation"""
        response = requests.get(f"{BASE_URL}/api/states", timeout=10)
        assert response.status_code == 200
        
        for state in response.json()["states"]:
            assert "id" in state
            assert "name" in state
            assert "abbreviation" in state
            # Verify abbreviation matches expected format
            assert state["abbreviation"].isupper(), f"Abbreviation should be uppercase: {state['abbreviation']}"


class TestPublicEndpoints:
    """Tests for other public endpoints"""
    
    def test_visitor_tracking(self):
        """Verify visitor tracking endpoint works"""
        response = requests.post(f"{BASE_URL}/api/track-visitor", timeout=10)
        # Should return 200 even without session
        assert response.status_code == 200
        data = response.json()
        assert "total_visitors" in data
        print(f"Visitor count: {data.get('total_visitors')}")
    
    def test_visitor_count(self):
        """Verify visitor count endpoint returns valid data"""
        response = requests.get(f"{BASE_URL}/api/visitor-count", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "total_visitors" in data
        assert isinstance(data["total_visitors"], int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
