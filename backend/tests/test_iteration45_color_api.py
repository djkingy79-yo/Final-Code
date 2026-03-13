"""
Iteration 45: Color Overhaul Verification Tests
Testing that backend APIs work correctly after design overhaul
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestIteration45APIs:
    """API tests for iteration 45 - color overhaul verification"""

    def test_health_check(self):
        """Test /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")

    def test_payment_prices_correct(self):
        """Test /api/payments/prices returns correct pricing"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200
        data = response.json()
        
        # Verify pricing structure
        assert "prices" in data
        prices = data["prices"]
        
        # Check $99 grounds of merit
        assert prices["grounds_of_merit"]["price"] == 99
        print("✅ Grounds of merit price: $99 AUD")
        
        # Check $150 full report
        assert prices["full_report"]["price"] == 150
        print("✅ Full report price: $150 AUD")
        
        # Check $200 extensive report
        assert prices["extensive_report"]["price"] == 200
        print("✅ Extensive report price: $200 AUD")
        
        # Verify currency
        assert data["currency"] == "AUD"
        print("✅ Currency: AUD")

    def test_states_endpoint(self):
        """Test /api/states returns all 8 Australian states/territories"""
        response = requests.get(f"{BASE_URL}/api/states")
        assert response.status_code == 200
        data = response.json()
        states = data.get("states", data)  # Handle nested structure
        assert len(states) == 8
        print(f"✅ States endpoint returned {len(states)} states")

    def test_offence_categories(self):
        """Test /api/offence-categories returns categories"""
        response = requests.get(f"{BASE_URL}/api/offence-categories")
        assert response.status_code == 200
        data = response.json()
        categories = data.get("categories", data)  # Handle nested structure
        assert len(categories) >= 10
        print(f"✅ Offence categories returned {len(categories)} categories")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
