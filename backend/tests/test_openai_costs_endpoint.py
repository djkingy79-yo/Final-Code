"""
Tests for the OpenAI Cost Tracking endpoint /api/admin/openai-costs
Tests auth requirements, period parameters, and response shape.
"""
import os
import sys
import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")
if not BASE_URL:
    BASE_URL = "https://criminal-appeals-au-2.preview.emergentagent.com"

# Admin credentials from test_credentials.md
ADMIN_EMAIL = "djkingy79@gmail.com"
ADMIN_PASSWORD = "Grubbygrub88"


class TestOpenAICostsAuth:
    """Test authentication requirements for /api/admin/openai-costs"""

    def test_unauthenticated_returns_401(self):
        """Endpoint requires authentication - returns 401 without session"""
        response = requests.get(f"{BASE_URL}/api/admin/openai-costs")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_admin_auth_returns_200(self):
        """Admin user can access the endpoint"""
        session = requests.Session()
        # Login as admin
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        
        session.headers["Authorization"] = "Bearer " + login_resp.json()["session_token"]
        
        # Access admin endpoint
        response = session.get(f"{BASE_URL}/api/admin/openai-costs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


class TestOpenAICostsPeriods:
    """Test different period parameters"""

    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        session.headers["Authorization"] = "Bearer " + login_resp.json()["session_token"]
        return session

    def test_period_month_default(self, admin_session):
        """Default period=month returns 200 with expected shape"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response shape
        assert data["period"] == "month"
        assert "window" in data
        assert "start" in data["window"]
        assert "end" in data["window"]
        
        # Verify totals shape
        totals = data["totals"]
        assert "cost_usd" in totals
        assert "calls" in totals
        assert "successful_calls" in totals
        assert "failed_calls" in totals
        assert "input_tokens" in totals
        assert "output_tokens" in totals
        assert "total_tokens" in totals
        assert "projected_month_end_usd" in totals
        
        # Verify breakdown arrays exist
        assert "by_model" in data
        assert "by_task_type" in data
        assert "by_report_type" in data
        assert "by_user" in data
        assert "daily" in data
        assert "pricing_note" in data
        
        print(f"Month totals: cost_usd={totals['cost_usd']}, calls={totals['calls']}")

    def test_period_week(self, admin_session):
        """period=week returns last 7 days"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs", params={"period": "week"})
        assert response.status_code == 200
        data = response.json()
        
        assert data["period"] == "week"
        assert "window" in data
        assert "totals" in data
        print(f"Week totals: cost_usd={data['totals']['cost_usd']}, calls={data['totals']['calls']}")

    def test_period_all(self, admin_session):
        """period=all returns full history"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs", params={"period": "all"})
        assert response.status_code == 200
        data = response.json()
        
        assert data["period"] == "all"
        assert "window" in data
        assert "totals" in data
        # projected_month_end_usd should be None for "all" period
        print(f"All-time totals: cost_usd={data['totals']['cost_usd']}, calls={data['totals']['calls']}")


class TestOpenAICostsResponseShape:
    """Test detailed response shape and data types"""

    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        session.headers["Authorization"] = "Bearer " + login_resp.json()["session_token"]
        return session

    def test_totals_numeric_types(self, admin_session):
        """Totals fields are correct numeric types"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs")
        data = response.json()
        totals = data["totals"]
        
        # All should be numeric (int or float)
        assert isinstance(totals["cost_usd"], (int, float))
        assert isinstance(totals["calls"], int)
        assert isinstance(totals["successful_calls"], int)
        assert isinstance(totals["failed_calls"], int)
        assert isinstance(totals["input_tokens"], int)
        assert isinstance(totals["output_tokens"], int)
        assert isinstance(totals["total_tokens"], int)
        # projected_month_end_usd can be None or float
        assert totals["projected_month_end_usd"] is None or isinstance(totals["projected_month_end_usd"], (int, float))

    def test_by_model_shape(self, admin_session):
        """by_model array has correct shape"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs")
        data = response.json()
        
        assert isinstance(data["by_model"], list)
        for item in data["by_model"]:
            assert "model" in item
            assert "calls" in item
            assert "cost_usd" in item

    def test_by_task_type_shape(self, admin_session):
        """by_task_type array has correct shape"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs")
        data = response.json()
        
        assert isinstance(data["by_task_type"], list)
        for item in data["by_task_type"]:
            assert "task_type" in item
            assert "calls" in item
            assert "cost_usd" in item

    def test_by_report_type_shape(self, admin_session):
        """by_report_type array has correct shape"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs")
        data = response.json()
        
        assert isinstance(data["by_report_type"], list)
        for item in data["by_report_type"]:
            assert "report_type" in item
            assert "calls" in item
            assert "cost_usd" in item

    def test_by_user_shape(self, admin_session):
        """by_user array has correct shape"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs")
        data = response.json()
        
        assert isinstance(data["by_user"], list)
        for item in data["by_user"]:
            assert "user_id" in item
            assert "email" in item or item.get("email") is None
            assert "cases" in item
            assert "calls" in item
            assert "cost_usd" in item

    def test_daily_shape(self, admin_session):
        """daily array has correct shape"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs")
        data = response.json()
        
        assert isinstance(data["daily"], list)
        for item in data["daily"]:
            assert "date" in item
            assert "calls" in item
            assert "cost_usd" in item

    def test_pricing_note_present(self, admin_session):
        """pricing_note is a non-empty string"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs")
        data = response.json()
        
        assert isinstance(data["pricing_note"], str)
        assert len(data["pricing_note"]) > 0
        assert "tiktoken" in data["pricing_note"].lower() or "estimated" in data["pricing_note"].lower()


class TestOpenAICostsEmptyData:
    """Test behavior when ai_usage collection is empty or has no data in period"""

    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        session.headers["Authorization"] = "Bearer " + login_resp.json()["session_token"]
        return session

    def test_empty_data_returns_zero_totals(self, admin_session):
        """When no data exists, endpoint returns well-formed response with zero totals"""
        response = admin_session.get(f"{BASE_URL}/api/admin/openai-costs")
        assert response.status_code == 200
        data = response.json()
        
        # Even with no data, response should be well-formed
        totals = data["totals"]
        assert totals["calls"] >= 0
        assert totals["cost_usd"] >= 0
        assert totals["input_tokens"] >= 0
        assert totals["output_tokens"] >= 0
        
        # Arrays should be lists (possibly empty)
        assert isinstance(data["by_model"], list)
        assert isinstance(data["by_task_type"], list)
        assert isinstance(data["by_report_type"], list)
        assert isinstance(data["by_user"], list)
        assert isinstance(data["daily"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
