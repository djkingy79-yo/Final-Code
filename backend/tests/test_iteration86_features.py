"""
Iteration 86 Feature Tests
Tests for:
- Backend health check
- Generate Report dialog options (4 types)
- Barrister View locked state
- Documents tab cleanup (no Extract Text/OCR Scan buttons)
- Strength rating colours in ReportView
- Delete confirmation dialogs
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

class TestHealthCheck:
    """Backend health check tests"""
    
    def test_health_endpoint_returns_healthy(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "database" in data
        print(f"Health check passed: {data}")


class TestReportTypes:
    """Test report type configuration"""
    
    def test_report_types_in_frontend_code(self):
        """Verify REPORT_TYPES array has correct structure"""
        # This is a code review test - we verify the frontend code has correct report types
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "quick_summary\\|full_detailed\\|extensive_log", 
             "/app/frontend/src/components/ReportsSection.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count >= 3, f"Expected at least 3 report type references, found {count}"
        print(f"Found {count} report type references in ReportsSection.jsx")
    
    def test_barrister_view_option_exists(self):
        """Verify Barrister View option exists in dialog"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "report-type-barrister\\|Barrister View", 
             "/app/frontend/src/components/ReportsSection.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count >= 2, f"Expected Barrister View references, found {count}"
        print(f"Found {count} Barrister View references")
    
    def test_barrister_view_locked_logic(self):
        """Verify Barrister View has locked state logic"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "hasAllReports", 
             "/app/frontend/src/components/ReportsSection.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count >= 5, f"Expected hasAllReports logic, found {count} references"
        print(f"Found {count} hasAllReports references for lock logic")


class TestDocumentsSection:
    """Test Documents tab cleanup"""
    
    def test_no_extract_text_button(self):
        """Verify Extract Text button is removed from Documents tab"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "Extract Text", 
             "/app/frontend/src/components/DocumentsSection.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count == 0, f"Extract Text button should be removed, found {count} references"
        print("Extract Text button correctly removed from Documents tab")
    
    def test_no_ocr_scan_button(self):
        """Verify OCR Scan button is removed from Documents tab action buttons"""
        import subprocess
        # Check for OCR Scan as a main action button (not the per-document OCR)
        result = subprocess.run(
            ["grep", "-c", "OCR Scan", 
             "/app/frontend/src/components/DocumentsSection.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count == 0, f"OCR Scan button should be removed, found {count} references"
        print("OCR Scan button correctly removed from Documents tab")
    
    def test_upload_document_button_exists(self):
        """Verify Upload Document button still exists"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "Upload Document\\|upload-doc-btn", 
             "/app/frontend/src/components/DocumentsSection.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count >= 1, f"Upload Document button should exist, found {count} references"
        print(f"Upload Document button exists with {count} references")


class TestStrengthRatingColours:
    """Test strength rating colour coding in ReportView"""
    
    def test_strong_rating_red_colour(self):
        """Verify Strong rating renders in red"""
        import subprocess
        # Check that text-red-600 is used for Strong ratings
        result = subprocess.run(
            ["grep", "-n", "text-red-600", "/app/frontend/src/pages/ReportView.jsx"],
            capture_output=True, text=True
        )
        assert "text-red-600" in result.stdout, "Strong rating should use text-red-600 class"
        # Verify it's in the context of Strong rating
        result2 = subprocess.run(
            ["grep", "-B2", "text-red-600", "/app/frontend/src/pages/ReportView.jsx"],
            capture_output=True, text=True
        )
        assert "Strong" in result2.stdout, "text-red-600 should be used for Strong rating"
        print("Strong rating correctly uses red colour (text-red-600)")
    
    def test_moderate_rating_blue_colour(self):
        """Verify Moderate rating renders in blue"""
        import subprocess
        # Check that text-blue-600 is used for Moderate ratings
        result = subprocess.run(
            ["grep", "-n", "text-blue-600", "/app/frontend/src/pages/ReportView.jsx"],
            capture_output=True, text=True
        )
        assert "text-blue-600" in result.stdout, "Moderate rating should use text-blue-600 class"
        # Verify it's in the context of Moderate rating
        result2 = subprocess.run(
            ["grep", "-B2", "text-blue-600", "/app/frontend/src/pages/ReportView.jsx"],
            capture_output=True, text=True
        )
        assert "Moderate" in result2.stdout, "text-blue-600 should be used for Moderate rating"
        print("Moderate rating correctly uses blue colour (text-blue-600)")


class TestGeneratingIndicator:
    """Test report generating indicator"""
    
    def test_generating_indicator_has_blue_header(self):
        """Verify generating indicator has blue header"""
        import subprocess
        result = subprocess.run(
            ["grep", "-A5", "report-generating-indicator", 
             "/app/frontend/src/components/ReportsSection.jsx"],
            capture_output=True, text=True
        )
        assert "bg-blue-700" in result.stdout or "blue" in result.stdout.lower(), \
            "Generating indicator should have blue header"
        print("Generating indicator has blue header styling")
    
    def test_generating_indicator_has_progress_steps(self):
        """Verify generating indicator shows progress steps"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "Reading\\|Analysing\\|Writing\\|Finalising", 
             "/app/frontend/src/components/ReportsSection.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count >= 4, f"Expected 4 progress steps, found {count}"
        print(f"Found {count} progress step labels")
    
    def test_generating_indicator_has_elapsed_time(self):
        """Verify generating indicator shows elapsed time"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "genElapsed\\|elapsed", 
             "/app/frontend/src/components/ReportsSection.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count >= 3, f"Expected elapsed time tracking, found {count} references"
        print(f"Found {count} elapsed time references")


class TestDeleteConfirmationDialogs:
    """Test delete confirmation dialogs"""
    
    def test_delete_report_confirmation_dialog(self):
        """Verify delete report has confirmation dialog"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "AlertDialog\\|Delete.*Report\\|confirmDeleteReport", 
             "/app/frontend/src/components/ReportsSection.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count >= 3, f"Expected delete confirmation dialog, found {count} references"
        print(f"Delete report confirmation dialog exists with {count} references")
    
    def test_delete_event_confirmation_in_casedetail(self):
        """Verify delete timeline event has confirmation"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "deleteEventId\\|confirmDeleteEvent", 
             "/app/frontend/src/pages/CaseDetail.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count >= 2, f"Expected delete event confirmation, found {count} references"
        print(f"Delete event confirmation exists with {count} references")
    
    def test_delete_ground_confirmation_in_casedetail(self):
        """Verify delete ground has confirmation"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "deleteGroundId\\|confirmDeleteGround", 
             "/app/frontend/src/pages/CaseDetail.jsx"],
            capture_output=True, text=True
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        assert count >= 2, f"Expected delete ground confirmation, found {count} references"
        print(f"Delete ground confirmation exists with {count} references")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
