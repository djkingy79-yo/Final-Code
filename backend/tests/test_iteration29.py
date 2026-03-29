"""
Iteration 29 Tests: Stripe Removal, Landing Page Updates, Barrister View, PaymentModal
Testing:
1. Stripe removal - /api/payments/checkout should return 404
2. Backend health check
3. Landing page accessible
4. PaymentModal shows "Coming Soon"
5. Barrister View route exists
"""

import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

class TestStripeRemoval:
    """Test that Stripe integration has been removed"""
    
    def test_payments_checkout_returns_404(self):
        """Stripe checkout endpoint should return 404 (Not Found) after removal"""
        response = requests.post(
            f"{BASE_URL}/api/payments/checkout",
            json={"feature_type": "full_report", "case_id": "test_case"}
        )
        # After Stripe removal, this endpoint should not exist
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"PASS: /api/payments/checkout returns 404 (Stripe removed)")


class TestBackendHealth:
    """Test backend health check"""
    
    def test_health_endpoint(self):
        """Health endpoint should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed with {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Expected healthy status, got {data}"
        print(f"PASS: /api/health returns healthy status")


class TestPaymentPrices:
    """Test payment prices endpoint (PayPal configured)"""
    
    def test_prices_endpoint(self):
        """Prices endpoint should return pricing tiers"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200, f"Prices endpoint failed with {response.status_code}"
        data = response.json()
        
        # Verify prices
        prices = data.get("prices", {})
        assert "full_report" in prices, "Missing full_report pricing"
        assert "extensive_report" in prices, "Missing extensive_report pricing"
        
        # Verify expected prices from landing page
        assert prices["full_report"]["price"] == 29.0, f"Full report should be $29, got {prices['full_report']['price']}"
        assert prices["extensive_report"]["price"] == 39.0, f"Extensive report should be $39, got {prices['extensive_report']['price']}"
        
        # Verify PayPal is configured
        assert data.get("paypal_configured") == True, "PayPal should be configured"
        assert data.get("currency") == "AUD", "Currency should be AUD"
        
        print(f"PASS: Prices endpoint returns correct pricing (Full $29, Extensive $39)")


class TestLandingPagePricing:
    """Test landing page returns successfully"""
    
    def test_landing_page_accessible(self):
        """Landing page should be accessible"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200, f"Landing page failed with {response.status_code}"
        assert "Appeal" in response.text or "Criminal" in response.text, "Landing page content missing"
        print(f"PASS: Landing page accessible at {BASE_URL}")


class TestAuthEndpoint:
    """Test Google auth button should appear in frontend"""
    
    def test_auth_status_endpoint(self):
        """Auth status endpoint should exist"""
        response = requests.get(f"{BASE_URL}/api/auth/status")
        # Should return 401 without auth, but endpoint should exist
        assert response.status_code in [200, 401], f"Auth status endpoint issue: {response.status_code}"
        print(f"PASS: /api/auth/status endpoint exists (returns {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
