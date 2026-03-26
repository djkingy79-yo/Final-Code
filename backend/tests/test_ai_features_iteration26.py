"""
Test Suite for AI Features - Iteration 26
Tests:
1. Reports (Full/Extensive) - Admin bypass for payment checks
2. Investigate grounds functionality
3. Contradictions scan
4. Quick summary report
"""
import pytest
import requests
import os
import time
import json

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://grounds-analyser.preview.emergentagent.com").rstrip("/")
ADMIN_SESSION_TOKEN = "sFc-8brIFR8jJ1vVbc5ioTxkGjMV5gd92JhLnJfb9nQ"
CASE_ID = "case_cec9b5706fae"


class TestAdminReportGeneration:
    """Test report generation with admin bypass for payment checks"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with admin token"""
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Cookie": f"session_token={ADMIN_SESSION_TOKEN}"
        })
    
    def test_quick_summary_report(self):
        """Test quick summary report generation (free for all)"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports/generate",
            json={"report_type": "quick_summary"},
            timeout=120
        )
        print(f"Quick Summary Response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "report_id" in data or "content" in data, "Response should contain report data"
        print(f"✓ Quick summary report generated successfully")
    
    def test_full_detailed_report_admin_bypass(self):
        """Test full detailed report - admin should bypass payment check"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports/generate",
            json={"report_type": "full_detailed"},
            timeout=180
        )
        print(f"Full Detailed Report Response: {response.status_code}")
        
        # Admin should NOT get 402 Payment Required
        assert response.status_code != 402, f"Admin should bypass payment - got 402 Payment Required"
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "report_id" in data or "content" in data, "Response should contain report data"
        print(f"✓ Full detailed report generated for admin without payment")
    
    def test_extensive_log_report_admin_bypass(self):
        """Test extensive log report - admin should bypass payment check"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports/generate",
            json={"report_type": "extensive_log"},
            timeout=180
        )
        print(f"Extensive Log Report Response: {response.status_code}")
        
        # Admin should NOT get 402 Payment Required
        assert response.status_code != 402, f"Admin should bypass payment - got 402 Payment Required"
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "report_id" in data or "content" in data, "Response should contain report data"
        print(f"✓ Extensive log report generated for admin without payment")


class TestGroundsIdentification:
    """Test grounds auto-identification from documents"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with admin token"""
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Cookie": f"session_token={ADMIN_SESSION_TOKEN}"
        })
    
    def test_auto_identify_grounds(self):
        """Test automatic grounds identification from documents"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/grounds/auto-identify",
            json={},
            timeout=120
        )
        print(f"Auto-Identify Grounds Response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check response structure - can contain grounds or identified_count
        has_grounds_info = (
            "grounds" in data or 
            "grounds_identified" in data or 
            "identified_count" in data or
            isinstance(data, list)
        )
        assert has_grounds_info, f"Response should contain grounds data: {data}"
        
        # Log what we found
        if "identified_count" in data:
            print(f"✓ Grounds auto-identification working - identified {data.get('identified_count', 0)} new grounds")
        else:
            print(f"✓ Grounds auto-identification working")
    
    def test_get_existing_grounds(self):
        """Test getting existing grounds for a case"""
        response = self.session.get(
            f"{BASE_URL}/api/cases/{CASE_ID}/grounds",
            timeout=30
        )
        print(f"Get Grounds Response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Should be a list or dict with grounds
        if isinstance(data, list):
            print(f"✓ Retrieved {len(data)} grounds")
        else:
            grounds = data.get("grounds", [])
            print(f"✓ Retrieved {len(grounds)} grounds")


class TestInvestigateGround:
    """Test ground investigation feature"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with admin token"""
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Cookie": f"session_token={ADMIN_SESSION_TOKEN}"
        })
    
    def get_first_ground_id(self):
        """Get the first ground ID from the case"""
        response = self.session.get(
            f"{BASE_URL}/api/cases/{CASE_ID}/grounds",
            timeout=30
        )
        if response.status_code != 200:
            return None
        
        data = response.json()
        grounds = data if isinstance(data, list) else data.get("grounds", [])
        
        # Find a ground that hasn't been investigated yet or any ground
        for ground in grounds:
            if ground.get("status") != "investigated":
                return ground.get("ground_id")
        
        # Return first ground if all are investigated
        if grounds:
            return grounds[0].get("ground_id")
        return None
    
    def test_investigate_ground(self):
        """Test investigating a specific ground"""
        ground_id = self.get_first_ground_id()
        if not ground_id:
            pytest.skip("No grounds available to investigate")
        
        print(f"Investigating ground: {ground_id}")
        
        response = self.session.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/grounds/{ground_id}/investigate",
            json={},
            timeout=120
        )
        print(f"Investigate Ground Response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Check that investigation returned meaningful data
        assert data, "Investigation should return data"
        print(f"✓ Ground investigation working - returned data with keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")


class TestContradictionsScan:
    """Test contradictions scan feature"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with admin token"""
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Cookie": f"session_token={ADMIN_SESSION_TOKEN}"
        })
    
    def test_contradictions_scan_with_empty_body(self):
        """Test contradictions scan with empty body {}"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/contradictions/scan",
            json={},
            timeout=120
        )
        print(f"Contradictions Scan Response: {response.status_code}")
        
        # Should work with empty body
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Check response structure
        assert "scan_id" in data or "contradictions" in data or "results" in data, \
            f"Response should contain scan results: {list(data.keys()) if isinstance(data, dict) else data}"
        print(f"✓ Contradictions scan working with empty body")
    
    def test_contradictions_scan_with_focus_areas(self):
        """Test contradictions scan with focus areas specified"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/contradictions/scan",
            json={"focus_areas": ["witness_statements", "evidence"]},
            timeout=120
        )
        print(f"Contradictions Scan (with focus) Response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Contradictions scan with focus areas working")
    
    def test_get_previous_scans(self):
        """Test getting previous contradiction scans"""
        response = self.session.get(
            f"{BASE_URL}/api/cases/{CASE_ID}/contradictions/scans",
            timeout=30
        )
        print(f"Get Contradiction Scans Response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list), f"Expected list of scans, got {type(data)}"
        print(f"✓ Retrieved {len(data)} previous contradiction scans")


class TestReportsDataFormat:
    """Test report data format for frontend rendering"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with admin token"""
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Cookie": f"session_token={ADMIN_SESSION_TOKEN}"
        })
    
    def test_report_has_generated_at_field(self):
        """Test that reports have generated_at date field"""
        response = self.session.get(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports",
            timeout=30
        )
        print(f"Get Reports Response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            report = data[0]
            # Either generated_at or created_at should exist
            has_date = "generated_at" in report or "created_at" in report
            assert has_date, f"Report should have generated_at or created_at field: {report.keys()}"
            
            date_field = report.get("generated_at") or report.get("created_at")
            assert date_field is not None, "Date field should not be None"
            print(f"✓ Report has date field: {date_field}")
        else:
            print("No reports found to test date format")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
