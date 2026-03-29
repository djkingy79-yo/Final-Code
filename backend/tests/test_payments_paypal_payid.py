"""
Test PayPal and PayID Payment Integration
Tests payment prices, payment methods, and payment flow endpoints
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'


class TestPaymentPrices:
    """Test /api/payments/prices endpoint - returns nested prices structure"""
    
    def test_prices_endpoint_returns_correct_structure(self):
        """Verify prices endpoint returns expected price data"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200
        
        data = response.json()
        # Prices are nested under 'prices' key
        prices = data.get("prices", data)  # fallback to data if no 'prices' key
        assert "full_report" in prices
        assert "extensive_report" in prices
        assert "grounds_of_merit" in prices
        # Verify PayPal configured flag
        assert data.get("paypal_configured") == True
    
    def test_full_report_price(self):
        """Verify full_report is $29"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        data = response.json()
        
        prices = data.get("prices", data)
        full_report = prices.get("full_report", {})
        assert full_report.get("price") == 29.00
        assert full_report.get("name") == "Full Detailed Report"
    
    def test_extensive_report_price(self):
        """Verify extensive_report is $39"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        data = response.json()
        
        prices = data.get("prices", data)
        extensive = prices.get("extensive_report", {})
        assert extensive.get("price") == 39.00
        assert extensive.get("name") == "Extensive Log Report"
    
    def test_grounds_of_merit_price(self):
        """Verify grounds_of_merit is $50"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        data = response.json()
        
        prices = data.get("prices", data)
        grounds = prices.get("grounds_of_merit", {})
        assert grounds.get("price") == 50.00


class TestPaymentMethods:
    """Test /api/payments/methods endpoint"""
    
    def test_methods_endpoint_returns_paypal_and_payid(self):
        """Verify payment methods endpoint returns both PayPal and PayID"""
        response = requests.get(f"{BASE_URL}/api/payments/methods")
        assert response.status_code == 200
        
        data = response.json()
        assert "paypal" in data
        assert "payid" in data
    
    def test_paypal_is_enabled(self):
        """Verify PayPal method is enabled with correct details"""
        response = requests.get(f"{BASE_URL}/api/payments/methods")
        data = response.json()
        
        paypal = data.get("paypal", {})
        assert paypal.get("enabled") == True
        assert paypal.get("name") == "PayPal"
        assert "PayPal" in paypal.get("description", "")
        assert "supports" in paypal
    
    def test_payid_is_enabled(self):
        """Verify PayID method is enabled with correct details"""
        response = requests.get(f"{BASE_URL}/api/payments/methods")
        data = response.json()
        
        payid = data.get("payid", {})
        assert payid.get("enabled") == True
        assert payid.get("name") == "PayID / Bank Transfer"
        assert payid.get("payid") == "djkingy79@gmail.com"
        assert payid.get("payid_type") == "email"
        assert "account_name" in payid


class TestHealthEndpoint:
    """Basic health check"""
    
    def test_health_endpoint(self):
        """Verify health endpoint returns healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "healthy"


class TestPayPalCreateOrderRequiresAuth:
    """Test that PayPal order creation requires authentication"""
    
    def test_create_order_without_auth_returns_401(self):
        """Creating PayPal order without auth should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/payments/paypal/create-order",
            json={
                "feature_type": "full_report",
                "case_id": "test-case-123",
                "return_url": "https://example.com/return",
                "cancel_url": "https://example.com/cancel"
            }
        )
        # Should return 401 Unauthorized (not authenticated)
        assert response.status_code == 401


class TestPayIDCreateReferenceRequiresAuth:
    """Test that PayID reference creation requires authentication"""
    
    def test_create_reference_without_auth_returns_401(self):
        """Creating PayID reference without auth should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/payments/payid/create-reference",
            json={
                "feature_type": "full_report",
                "case_id": "test-case-123"
            }
        )
        # Should return 401 Unauthorized (not authenticated)
        assert response.status_code == 401


class TestPayIDPendingRequiresAdmin:
    """Test that PayID pending endpoint requires admin auth"""
    
    def test_pending_payments_without_auth_returns_401(self):
        """Getting pending PayID payments without auth should return 401"""
        response = requests.get(f"{BASE_URL}/api/payments/payid/pending")
        # Should return 401 Unauthorized
        assert response.status_code == 401


class TestPayPalInvalidFeatureType:
    """Test error handling for invalid feature types"""
    
    def test_prices_contains_expected_feature_types(self):
        """Prices endpoint should contain expected feature types"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        data = response.json()
        
        prices = data.get("prices", {})
        # Verify expected feature types are present
        valid_types = {"full_report", "extensive_report", "grounds_of_merit"}
        for feature_type in valid_types:
            assert feature_type in prices, f"Missing feature type: {feature_type}"


class TestLandingPageAccessible:
    """Test that landing page is accessible"""
    
    def test_landing_page_loads(self):
        """Landing page should return 200"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
