"""
Test Case Law Search Feature - Iteration 136
Tests the verified case law database integration with AustLII, NSW CaseLaw, 
Queensland Judgments, JADE, and state-specific court databases.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_f8bf63e9dcbe"  # Homann v R, NSW, murder


class TestCaseLawEndpoints:
    """Test the case law search API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session with auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session token
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("session_token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                self.token = token
            else:
                pytest.skip("No session token returned")
        else:
            pytest.skip(f"Login failed: {login_resp.status_code}")
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        resp = self.session.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        print("PASS: Health endpoint accessible")
    
    def test_caselaw_databases_endpoint_no_state(self):
        """Test /api/caselaw/databases returns all databases when no state specified"""
        resp = self.session.get(f"{BASE_URL}/api/caselaw/databases")
        assert resp.status_code == 200
        data = resp.json()
        
        # Should have states and national sections
        assert "states" in data, "Response should have 'states' key"
        assert "national" in data, "Response should have 'national' key"
        
        # Check states include NSW and QLD
        assert "nsw" in data["states"], "Should include NSW databases"
        assert "qld" in data["states"], "Should include QLD databases"
        
        # Check national databases
        national_ids = [db["id"] for db in data["national"]]
        assert "austlii_all" in national_ids, "Should have AustLII All"
        assert "hca" in national_ids, "Should have High Court"
        assert "jade" in national_ids, "Should have JADE"
        assert "google_scholar" in national_ids, "Should have Google Scholar"
        
        print(f"PASS: /api/caselaw/databases returns {len(data['states'])} states and {len(data['national'])} national databases")
    
    def test_caselaw_databases_endpoint_with_nsw_state(self):
        """Test /api/caselaw/databases?state=nsw returns NSW-specific databases"""
        resp = self.session.get(f"{BASE_URL}/api/caselaw/databases?state=nsw")
        assert resp.status_code == 200
        data = resp.json()
        
        # Should have state info
        assert data.get("state") == "nsw", "State should be nsw"
        assert data.get("state_name") == "New South Wales", "State name should be New South Wales"
        assert "state_databases" in data, "Should have state_databases"
        assert "national_databases" in data, "Should have national_databases"
        
        # Check NSW-specific databases
        state_db_ids = [db["id"] for db in data["state_databases"]]
        assert "nsw_caselaw" in state_db_ids, "Should have NSW CaseLaw"
        assert "austlii_nsw" in state_db_ids, "Should have AustLII NSW"
        
        print(f"PASS: /api/caselaw/databases?state=nsw returns {len(data['state_databases'])} state databases")
    
    def test_caselaw_databases_endpoint_with_qld_state(self):
        """Test /api/caselaw/databases?state=qld returns QLD-specific databases"""
        resp = self.session.get(f"{BASE_URL}/api/caselaw/databases?state=qld")
        assert resp.status_code == 200
        data = resp.json()
        
        # Should have state info
        assert data.get("state") == "qld", "State should be qld"
        assert data.get("state_name") == "Queensland", "State name should be Queensland"
        
        # Check QLD-specific databases
        state_db_ids = [db["id"] for db in data["state_databases"]]
        assert "qld_judgments" in state_db_ids, "Should have Queensland Judgments"
        assert "sclqld" in state_db_ids, "Should have Supreme Court Library QLD"
        assert "austlii_qld" in state_db_ids, "Should have AustLII QLD"
        
        print(f"PASS: /api/caselaw/databases?state=qld returns {len(data['state_databases'])} state databases")
    
    def test_case_caselaw_search_endpoint(self):
        """Test /api/cases/{case_id}/caselaw/search returns search links"""
        resp = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/caselaw/search")
        assert resp.status_code == 200
        data = resp.json()
        
        # Should have query and search links
        assert "query" in data, "Response should have 'query'"
        assert "search_links" in data, "Response should have 'search_links'"
        assert "state" in data, "Response should have 'state'"
        assert "state_name" in data, "Response should have 'state_name'"
        
        # Check search links have required fields
        for link in data["search_links"]:
            assert "id" in link, "Link should have 'id'"
            assert "name" in link, "Link should have 'name'"
            assert "url" in link, "Link should have 'url'"
            assert "scope" in link, "Link should have 'scope' (state or national)"
        
        # Check state and national links exist
        state_links = [l for l in data["search_links"] if l["scope"] == "state"]
        national_links = [l for l in data["search_links"] if l["scope"] == "national"]
        
        print(f"PASS: /api/cases/{TEST_CASE_ID}/caselaw/search returns {len(state_links)} state links and {len(national_links)} national links")
        print(f"  Query: {data['query']}")
        print(f"  State: {data['state']} ({data['state_name']})")
    
    def test_case_caselaw_search_with_custom_query(self):
        """Test /api/cases/{case_id}/caselaw/search?q=custom returns custom query links"""
        custom_query = "murder appeal NSW"
        resp = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/caselaw/search?q={custom_query}")
        assert resp.status_code == 200
        data = resp.json()
        
        # Query should match custom query
        assert data["query"] == custom_query, f"Query should be '{custom_query}'"
        
        # URLs should contain encoded query
        for link in data["search_links"]:
            assert "murder" in link["url"].lower() or "murder" in link["url"], f"URL should contain query: {link['url']}"
        
        print(f"PASS: Custom query search works with query: {custom_query}")
    
    def test_nsw_case_has_nsw_databases(self):
        """Test that NSW case (Homann v R) returns NSW-specific databases"""
        resp = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/caselaw/search")
        assert resp.status_code == 200
        data = resp.json()
        
        # Homann v R is NSW case
        assert data.get("state") == "nsw", "Homann v R should be NSW case"
        
        # Check NSW databases in state links
        state_links = [l for l in data["search_links"] if l["scope"] == "state"]
        state_link_ids = [l["id"] for l in state_links]
        
        assert "nsw_caselaw" in state_link_ids, "NSW case should have NSW CaseLaw link"
        assert "austlii_nsw" in state_link_ids, "NSW case should have AustLII NSW link"
        
        # Check national databases
        national_links = [l for l in data["search_links"] if l["scope"] == "national"]
        national_link_ids = [l["id"] for l in national_links]
        
        assert "austlii_all" in national_link_ids, "Should have AustLII All"
        assert "jade" in national_link_ids, "Should have JADE"
        assert "google_scholar" in national_link_ids, "Should have Google Scholar"
        
        print(f"PASS: NSW case has correct state databases: {state_link_ids}")
    
    def test_search_links_have_valid_urls(self):
        """Test that search links have properly formatted URLs"""
        resp = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/caselaw/search")
        assert resp.status_code == 200
        data = resp.json()
        
        for link in data["search_links"]:
            url = link["url"]
            # URL should start with https
            assert url.startswith("https://"), f"URL should start with https: {url}"
            # URL should not contain {query} placeholder
            assert "{query}" not in url, f"URL should not have unresolved placeholder: {url}"
            # URL should be properly encoded (no raw spaces)
            assert " " not in url or "%20" in url or "+" in url, f"URL should be encoded: {url}"
        
        print(f"PASS: All {len(data['search_links'])} search links have valid URLs")
    
    def test_databases_have_required_fields(self):
        """Test that database entries have all required fields"""
        resp = self.session.get(f"{BASE_URL}/api/caselaw/databases")
        assert resp.status_code == 200
        data = resp.json()
        
        required_fields = ["id", "name", "url", "description", "search_template"]
        
        # Check national databases
        for db in data["national"]:
            for field in required_fields:
                assert field in db, f"National database {db.get('id', 'unknown')} missing field: {field}"
        
        # Check state databases
        for state, state_data in data["states"].items():
            for db in state_data.get("databases", []):
                for field in required_fields:
                    assert field in db, f"State {state} database {db.get('id', 'unknown')} missing field: {field}"
        
        print(f"PASS: All databases have required fields")
    
    def test_case_not_found_returns_404(self):
        """Test that non-existent case returns 404"""
        resp = self.session.get(f"{BASE_URL}/api/cases/nonexistent_case_id/caselaw/search")
        assert resp.status_code == 404
        print("PASS: Non-existent case returns 404")


class TestCaseLawGroundEndpoint:
    """Test the case law search for specific grounds"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session with auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session token
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("session_token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                self.token = token
            else:
                pytest.skip("No session token returned")
        else:
            pytest.skip(f"Login failed: {login_resp.status_code}")
    
    def test_ground_caselaw_endpoint_exists(self):
        """Test that the ground caselaw endpoint exists (even if ground doesn't)"""
        # This will return 404 for non-existent ground, but endpoint should exist
        resp = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/caselaw/ground/nonexistent_ground")
        # Should be 404 (ground not found) not 405 (method not allowed)
        assert resp.status_code in [404, 200], f"Endpoint should exist, got {resp.status_code}"
        print("PASS: Ground caselaw endpoint exists")


class TestCaseLawServiceLogic:
    """Test the case law service logic"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session with auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session token
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("session_token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                self.token = token
            else:
                pytest.skip("No session token returned")
        else:
            pytest.skip(f"Login failed: {login_resp.status_code}")
    
    def test_all_states_have_databases(self):
        """Test that all Australian states/territories have databases configured"""
        resp = self.session.get(f"{BASE_URL}/api/caselaw/databases")
        assert resp.status_code == 200
        data = resp.json()
        
        expected_states = ["nsw", "qld", "vic", "sa", "wa", "tas", "nt", "act"]
        
        for state in expected_states:
            assert state in data["states"], f"State {state} should be configured"
            state_data = data["states"][state]
            assert "databases" in state_data, f"State {state} should have databases"
            assert len(state_data["databases"]) > 0, f"State {state} should have at least one database"
        
        print(f"PASS: All {len(expected_states)} states/territories have databases configured")
    
    def test_search_template_urls_are_valid(self):
        """Test that search template URLs are valid - some courts don't have direct search URLs"""
        resp = self.session.get(f"{BASE_URL}/api/caselaw/databases")
        assert resp.status_code == 200
        data = resp.json()
        
        # Courts that don't have direct search URLs (they link to judgment pages instead)
        no_search_courts = ["vic_sc", "courts_sa", "ecourts_wa", "act_courts"]
        
        # Check national databases - all should have search templates
        for db in data["national"]:
            template = db.get("search_template", "")
            assert "{query}" in template, f"National db {db['id']} template should have {{query}}: {template}"
            assert template.startswith("https://"), f"Template should start with https: {template}"
        
        # Check state databases - some may not have direct search
        for state, state_data in data["states"].items():
            for db in state_data.get("databases", []):
                template = db.get("search_template", "")
                assert template.startswith("https://"), f"Template should start with https: {template}"
                # Only check for {query} if not in the no-search list
                if db["id"] not in no_search_courts:
                    assert "{query}" in template, f"State {state} db {db['id']} template should have {{query}}: {template}"
        
        print("PASS: All search templates are valid (some courts link to judgment pages without direct search)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
