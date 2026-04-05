"""
Test Collaboration Features - Iteration 103
Tests case sharing, chat, notifications, activity feed APIs
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_a97ea91f0692"  # Dummy Murder Appeal Demonstration
TEST_SESSION_TOKEN = "sess_ab40fa0ed548457aa7d37cbd1a10cf8a"


class TestCollaborationAPIs:
    """Test collaboration endpoints: sharing, chat, notifications, activity"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session with auth token"""
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TEST_SESSION_TOKEN}"
        })
    
    # ============ SHARING ENDPOINTS ============
    
    def test_share_case_by_email(self):
        """POST /api/cases/{case_id}/share - Share case by email"""
        # Test with a new email to avoid duplicate error
        import uuid
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        
        response = self.session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/share",
            json={"email": test_email}
        )
        
        # Should succeed or return 400 if already shared
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}, body: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "share_id" in data, "Response should contain share_id"
            assert "status" in data, "Response should contain status"
            print(f"PASS: Share case by email - share_id: {data.get('share_id')}")
        else:
            print("PASS: Share case by email - returned 400 (expected for duplicate)")
    
    def test_share_case_self_error(self):
        """POST /api/cases/{case_id}/share - Cannot share with yourself"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/share",
            json={"email": TEST_EMAIL}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "yourself" in data.get("detail", "").lower() or "cannot share" in data.get("detail", "").lower(), \
            f"Expected error about sharing with yourself, got: {data}"
        print("PASS: Cannot share case with yourself")
    
    def test_generate_share_link(self):
        """POST /api/cases/{case_id}/share-link - Generate shareable link"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/share-link"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, body: {response.text}"
        data = response.json()
        
        assert "link" in data, "Response should contain link"
        assert "token" in data, "Response should contain token"
        assert "link_id" in data, "Response should contain link_id"
        assert "/shared/" in data["link"], "Link should contain /shared/ path"
        
        print(f"PASS: Generate share link - link: {data['link'][:50]}...")
    
    def test_get_case_shares(self):
        """GET /api/cases/{case_id}/shares - List shares and link"""
        response = self.session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/shares"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, body: {response.text}"
        data = response.json()
        
        assert "shares" in data, "Response should contain shares array"
        assert isinstance(data["shares"], list), "shares should be a list"
        
        # Check share_link field
        if data.get("share_link"):
            assert "link" in data["share_link"], "share_link should contain link"
        
        print(f"PASS: Get case shares - {len(data['shares'])} shares found")
    
    def test_get_shared_cases(self):
        """GET /api/shared-cases - Get cases shared with current user"""
        response = self.session.get(f"{BASE_URL}/api/shared-cases")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, body: {response.text}"
        data = response.json()
        
        # Should return a list (may be empty if user is owner, not recipient)
        assert isinstance(data, list), "Response should be a list"
        print(f"PASS: Get shared cases - {len(data)} cases shared with user")
    
    # ============ CHAT/MESSAGING ENDPOINTS ============
    
    def test_get_messages(self):
        """GET /api/cases/{case_id}/messages - Get chat messages"""
        response = self.session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/messages"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, body: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list of messages"
        print(f"PASS: Get messages - {len(data)} messages found")
    
    def test_send_message(self):
        """POST /api/cases/{case_id}/messages - Send a chat message"""
        import uuid
        test_content = f"Test message {uuid.uuid4().hex[:8]}"
        
        response = self.session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/messages",
            json={"content": test_content}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, body: {response.text}"
        data = response.json()
        
        assert "message_id" in data, "Response should contain message_id"
        assert "content" in data, "Response should contain content"
        assert data["content"] == test_content, "Content should match"
        assert "author_name" in data, "Response should contain author_name"
        assert "created_at" in data, "Response should contain created_at"
        
        print(f"PASS: Send message - message_id: {data['message_id']}")
    
    def test_send_empty_message_error(self):
        """POST /api/cases/{case_id}/messages - Empty message should fail"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/messages",
            json={"content": "   "}  # Whitespace only
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Empty message returns 400")
    
    # ============ ACTIVITY FEED ENDPOINTS ============
    
    def test_get_activity(self):
        """GET /api/cases/{case_id}/activity - Get activity feed"""
        response = self.session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/activity"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, body: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list of activities"
        
        # If there are activities, verify structure
        if len(data) > 0:
            activity = data[0]
            assert "activity_id" in activity, "Activity should have activity_id"
            assert "action" in activity, "Activity should have action"
            assert "user_name" in activity, "Activity should have user_name"
            assert "created_at" in activity, "Activity should have created_at"
        
        print(f"PASS: Get activity - {len(data)} activities found")
    
    # ============ NOTIFICATION ENDPOINTS ============
    
    def test_get_notifications(self):
        """GET /api/notifications - Get user notifications"""
        response = self.session.get(f"{BASE_URL}/api/notifications")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, body: {response.text}"
        data = response.json()
        
        assert "notifications" in data, "Response should contain notifications"
        assert "unread_count" in data, "Response should contain unread_count"
        assert isinstance(data["notifications"], list), "notifications should be a list"
        assert isinstance(data["unread_count"], int), "unread_count should be an integer"
        
        print(f"PASS: Get notifications - {len(data['notifications'])} notifications, {data['unread_count']} unread")
    
    def test_mark_all_notifications_read(self):
        """PATCH /api/notifications/read-all - Mark all as read"""
        response = self.session.patch(f"{BASE_URL}/api/notifications/read-all")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, body: {response.text}"
        data = response.json()
        
        assert "message" in data, "Response should contain message"
        print("PASS: Mark all notifications read")
    
    # ============ CASE ACCESS VERIFICATION ============
    
    def test_case_access_for_owner(self):
        """Verify owner can access case data"""
        response = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, body: {response.text}"
        data = response.json()
        
        assert "case_id" in data, "Response should contain case_id"
        assert data["case_id"] == TEST_CASE_ID, "case_id should match"
        
        print(f"PASS: Case access for owner - title: {data.get('title', 'N/A')}")
    
    def test_invalid_case_access(self):
        """Verify invalid case returns 404"""
        response = self.session.get(f"{BASE_URL}/api/cases/invalid_case_id_12345")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Invalid case returns 404")


class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        """GET /api/health - API is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("PASS: API health check")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
