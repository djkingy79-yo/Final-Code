"""
Test Terms Acceptance Feature

Tests for:
- GET /api/auth/me returns terms_accepted status
- POST /api/auth/accept-terms endpoint
- Terms acceptance persists in database
"""

import pytest
import requests
import uuid

BASE_URL = 'http://localhost:8001'

# Module: Auth Terms Tests
class TestTermsAcceptance:
    """Tests for terms acceptance functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create test user without terms accepted"""
        import subprocess
        
        self.user_id = f"test-terms-{uuid.uuid4().hex[:8]}"
        self.session_token = f"test_terms_session_{uuid.uuid4().hex}"
        
        # Create test user via mongosh
        mongo_script = f'''
        use('test_database');
        db.users.insertOne({{
          user_id: "{self.user_id}",
          email: "test.terms.{self.user_id}@example.com",
          name: "Terms Test User",
          terms_accepted: false,
          created_at: new Date()
        }});
        db.user_sessions.insertOne({{
          user_id: "{self.user_id}",
          session_token: "{self.session_token}",
          expires_at: new Date(Date.now() + 7*24*60*60*1000),
          created_at: new Date()
        }});
        '''
        subprocess.run(['mongosh', '--eval', mongo_script], capture_output=True)
        
        yield
        
        # Cleanup
        cleanup_script = f'''
        use('test_database');
        db.users.deleteOne({{user_id: "{self.user_id}"}});
        db.user_sessions.deleteOne({{session_token: "{self.session_token}"}});
        '''
        subprocess.run(['mongosh', '--eval', cleanup_script], capture_output=True)
    
    def test_get_me_returns_terms_accepted_false(self):
        """Test GET /api/auth/me returns terms_accepted: false for new user"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {self.session_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "terms_accepted" in data
        assert not data["terms_accepted"]
        assert data["terms_accepted_at"] is None
    
    def test_accept_terms_endpoint(self):
        """Test POST /api/auth/accept-terms accepts terms"""
        response = requests.post(
            f"{BASE_URL}/api/auth/accept-terms",
            headers={
                "Authorization": f"Bearer {self.session_token}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Terms accepted"
        assert data["terms_accepted"]
    
    def test_get_me_returns_terms_accepted_true_after_accept(self):
        """Test GET /api/auth/me returns terms_accepted: true after accepting"""
        # First accept terms
        accept_response = requests.post(
            f"{BASE_URL}/api/auth/accept-terms",
            headers={
                "Authorization": f"Bearer {self.session_token}",
                "Content-Type": "application/json"
            }
        )
        assert accept_response.status_code == 200
        
        # Then verify
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {self.session_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["terms_accepted"]
        assert data["terms_accepted_at"] is not None
    
    def test_accept_terms_requires_auth(self):
        """Test POST /api/auth/accept-terms requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/auth/accept-terms",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401


# Module: Existing user with terms already accepted
class TestExistingUserWithTerms:
    """Tests for users who have already accepted terms"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create test user with terms already accepted"""
        import subprocess
        
        self.user_id = f"test-terms-existing-{uuid.uuid4().hex[:8]}"
        self.session_token = f"test_terms_existing_{uuid.uuid4().hex}"
        
        # Create test user with terms_accepted: true
        mongo_script = f'''
        use('test_database');
        db.users.insertOne({{
          user_id: "{self.user_id}",
          email: "test.existing.{self.user_id}@example.com",
          name: "Existing Terms User",
          terms_accepted: true,
          terms_accepted_at: new Date().toISOString(),
          created_at: new Date()
        }});
        db.user_sessions.insertOne({{
          user_id: "{self.user_id}",
          session_token: "{self.session_token}",
          expires_at: new Date(Date.now() + 7*24*60*60*1000),
          created_at: new Date()
        }});
        '''
        subprocess.run(['mongosh', '--eval', mongo_script], capture_output=True)
        
        yield
        
        # Cleanup
        cleanup_script = f'''
        use('test_database');
        db.users.deleteOne({{user_id: "{self.user_id}"}});
        db.user_sessions.deleteOne({{session_token: "{self.session_token}"}});
        '''
        subprocess.run(['mongosh', '--eval', cleanup_script], capture_output=True)
    
    def test_existing_user_terms_accepted_true(self):
        """Test GET /api/auth/me returns terms_accepted: true for existing user"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {self.session_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["terms_accepted"]
        assert data["terms_accepted_at"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
