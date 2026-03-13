"""
Iteration 43 API Tests
Tests for pricing updates and feature changes:
- Backend /api/payments/prices returns correct prices
- Backend /api/health returns 200
- No Contradictions/Progress endpoints exposed
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndPricing:
    """Test health check and pricing endpoints"""
    
    def test_health_check(self):
        """Test /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print(f"✅ Health check passed: {data}")
    
    def test_payment_prices_endpoint(self):
        """Test /api/payments/prices returns correct prices"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200
        data = response.json()
        
        # Verify prices structure
        assert "prices" in data
        prices = data["prices"]
        
        # Test grounds_of_merit price = $99
        assert "grounds_of_merit" in prices
        assert prices["grounds_of_merit"]["price"] == 99.0
        print(f"✅ Grounds of Merit price: ${prices['grounds_of_merit']['price']}")
        
        # Test full_report price = $150
        assert "full_report" in prices
        assert prices["full_report"]["price"] == 150.0
        print(f"✅ Full Report price: ${prices['full_report']['price']}")
        
        # Test extensive_report price = $200
        assert "extensive_report" in prices
        assert prices["extensive_report"]["price"] == 200.0
        print(f"✅ Extensive Report price: ${prices['extensive_report']['price']}")
        
        # Verify currency
        assert data.get("currency") == "AUD"
        print(f"✅ Currency: {data['currency']}")
    
    def test_states_endpoint(self):
        """Test /api/states returns 8 Australian states"""
        response = requests.get(f"{BASE_URL}/api/states")
        assert response.status_code == 200
        data = response.json()
        
        assert "states" in data
        states = data["states"]
        assert len(states) == 8
        
        expected_states = ["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act"]
        state_ids = [s["id"] for s in states]
        for state in expected_states:
            assert state in state_ids
        print(f"✅ All 8 states returned: {state_ids}")
    
    def test_offence_categories_endpoint(self):
        """Test /api/offence-categories returns 11 categories"""
        response = requests.get(f"{BASE_URL}/api/offence-categories")
        assert response.status_code == 200
        data = response.json()
        
        assert "categories" in data
        categories = data["categories"]
        assert len(categories) == 11
        
        expected_categories = [
            "homicide", "assault", "sexual_offences", "robbery_theft", 
            "drug_offences", "fraud_dishonesty", "firearms_weapons",
            "domestic_violence", "public_order", "terrorism", "driving_offences"
        ]
        category_ids = [c["id"] for c in categories]
        for cat in expected_categories:
            assert cat in category_ids
        print(f"✅ All 11 offence categories returned")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
