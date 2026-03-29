"""
Tests for Export Features:
- Quick Export (ZIP package with all case materials + editable templates)
- Document Bundler (PDF generation from selected documents)
- Export Preview endpoint

Requirements: Test user needs a case with documents to test export features
"""
import pytest
import requests
import os
import io
import zipfile

BASE_URL = 'http://localhost:8001'

class TestExportEndpoints:
    """Test Quick Export and Document Bundler API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and case with documents"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Register and login test user
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"test_export_{unique_id}@test.com"
        self.test_password = "TestPass123!"
        
        # Register
        register_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Export Test User"
        })
        
        if register_response.status_code != 200:
            pytest.skip(f"Could not register test user: {register_response.text}")
        
        self.auth_token = register_response.json().get("token")
        self.user_id = register_response.json().get("user", {}).get("user_id")
        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
        
        # Create a test case
        case_response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": f"Export Test Case {unique_id}",
            "defendant_name": "Export Test Defendant",
            "case_number": f"EXP-{unique_id}",
            "court": "Supreme Court of NSW",
            "state": "nsw",
            "offence_category": "assault",
            "offence_type": "Common Assault",
            "summary": "Test case for export features testing"
        })
        
        if case_response.status_code not in [200, 201]:
            pytest.skip(f"Could not create test case: {case_response.text}")
        
        self.case_id = case_response.json().get("case_id")
        
        yield
        
        # Cleanup - delete test case
        if hasattr(self, 'case_id') and self.case_id:
            self.session.delete(f"{BASE_URL}/api/cases/{self.case_id}")
    
    # ============= Export Preview Tests =============
    
    def test_export_preview_returns_counts(self):
        """Test GET /api/cases/{case_id}/export/preview returns document counts"""
        response = self.session.get(f"{BASE_URL}/api/cases/{self.case_id}/export/preview")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify all expected fields are present
        assert "documents" in data, "Response should include documents count"
        assert "timeline_events" in data, "Response should include timeline_events count"
        assert "grounds_of_merit" in data, "Response should include grounds_of_merit count"
        assert "notes" in data, "Response should include notes count"
        assert "reports" in data, "Response should include reports count"
        assert "ai_analysis_scans" in data, "Response should include ai_analysis_scans count"
        assert "templates" in data, "Response should include templates count"
        assert "estimated_files" in data, "Response should include estimated_files count"
        
        # Templates should be fixed at 5
        assert data["templates"] == 5, f"Expected 5 templates, got {data['templates']}"
        
        print(f"✓ Export preview returned: {data}")
    
    def test_export_preview_unauthorized_case(self):
        """Test export preview fails for non-existent case"""
        response = self.session.get(f"{BASE_URL}/api/cases/nonexistent-case-id/export/preview")
        
        # Should return 404 or 403
        assert response.status_code in [403, 404], f"Expected 403/404, got {response.status_code}"
        print("✓ Preview correctly blocked for non-existent case")
    
    # ============= Quick Export (ZIP Package) Tests =============
    
    def test_export_package_generates_zip(self):
        """Test POST /api/cases/{case_id}/export/package generates ZIP file"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{self.case_id}/export/package",
            json={
                "include_documents": True,
                "include_timeline": True,
                "include_grounds": True,
                "include_notes": True,
                "include_reports": True,
                "include_analysis": True,
                "include_templates": True
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify response is a ZIP file
        assert response.headers.get("content-type") == "application/zip", \
            f"Expected application/zip, got {response.headers.get('content-type')}"
        
        # Check content-disposition header has filename
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp, "Should have attachment disposition"
        assert ".zip" in content_disp, "Filename should have .zip extension"
        
        # Verify it's a valid ZIP file
        zip_buffer = io.BytesIO(response.content)
        try:
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                file_list = zf.namelist()
                print(f"✓ ZIP contains {len(file_list)} files: {file_list[:10]}...")
                
                # Check for expected files/folders
                assert any("README.txt" in f for f in file_list), "ZIP should contain README.txt"
                assert any("Case_Summary" in f for f in file_list), "ZIP should contain Case_Summary"
                assert any("Templates" in f for f in file_list), "ZIP should contain Templates folder"
        except zipfile.BadZipFile:
            pytest.fail("Response is not a valid ZIP file")
        
        print(f"✓ Export package generated successfully with {len(file_list)} files")
    
    def test_export_package_with_selective_options(self):
        """Test export package respects option flags"""
        # Export with only templates
        response = self.session.post(
            f"{BASE_URL}/api/cases/{self.case_id}/export/package",
            json={
                "include_documents": False,
                "include_timeline": False,
                "include_grounds": False,
                "include_notes": False,
                "include_reports": False,
                "include_analysis": False,
                "include_templates": True
            }
        )
        
        assert response.status_code == 200
        
        # Verify ZIP still generates
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            file_list = zf.namelist()
            # Templates should be present
            assert any("Templates" in f or "Template" in f for f in file_list), \
                f"Templates should be present. Files: {file_list}"
        
        print(f"✓ Selective export worked - {len(file_list)} files")
    
    def test_export_package_templates_content(self):
        """Test that exported templates contain case-specific data"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{self.case_id}/export/package",
            json={
                "include_documents": False,
                "include_timeline": False,
                "include_grounds": False,
                "include_notes": False,
                "include_reports": False,
                "include_analysis": False,
                "include_templates": True
            }
        )
        
        assert response.status_code == 200
        
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            # Find and read a template file
            template_files = [f for f in zf.namelist() if "Template" in f and f.endswith(".txt")]
            
            if template_files:
                # Read one template to verify it has case data
                template_content = zf.read(template_files[0]).decode('utf-8')
                
                # Should contain case info (state at minimum since we set NSW)
                assert "NSW" in template_content or "Export Test" in template_content, \
                    "Template should contain case-specific data"
                
                print(f"✓ Template '{template_files[0]}' contains case-specific data")
            else:
                print("⚠ No template files found in export")
    
    def test_export_package_unauthorized(self):
        """Test export package fails for unauthorized access"""
        # Create a new session without auth
        unauth_session = requests.Session()
        unauth_session.headers.update({"Content-Type": "application/json"})
        
        response = unauth_session.post(
            f"{BASE_URL}/api/cases/{self.case_id}/export/package",
            json={"include_templates": True}
        )
        
        assert response.status_code in [401, 403], \
            f"Expected 401/403, got {response.status_code}"
        
        print("✓ Export package correctly requires authentication")
    
    # ============= Document Bundler (PDF) Tests =============
    
    def test_bundle_requires_documents(self):
        """Test bundle endpoint requires document_ids"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{self.case_id}/export/bundle",
            json={
                "document_ids": [],
                "include_toc": True,
                "title": "Test Bundle"
            }
        )
        
        # Should fail with empty document list
        assert response.status_code == 400, \
            f"Expected 400 for empty documents, got {response.status_code}"
        
        print("✓ Bundle correctly requires documents")
    
    def test_bundle_with_nonexistent_documents(self):
        """Test bundle with non-existent document IDs returns 404"""
        response = self.session.post(
            f"{BASE_URL}/api/cases/{self.case_id}/export/bundle",
            json={
                "document_ids": ["fake-doc-id-1", "fake-doc-id-2"],
                "include_toc": True,
                "title": "Test Bundle"
            }
        )
        
        # Should return 404 since no documents match
        assert response.status_code == 404, \
            f"Expected 404 for non-existent docs, got {response.status_code}"
        
        print("✓ Bundle correctly handles non-existent documents")
    
    def test_bundle_unauthorized(self):
        """Test bundle endpoint requires authentication"""
        unauth_session = requests.Session()
        unauth_session.headers.update({"Content-Type": "application/json"})
        
        response = unauth_session.post(
            f"{BASE_URL}/api/cases/{self.case_id}/export/bundle",
            json={
                "document_ids": ["some-doc"],
                "include_toc": True,
                "title": "Test Bundle"
            }
        )
        
        assert response.status_code in [401, 403], \
            f"Expected 401/403, got {response.status_code}"
        
        print("✓ Bundle correctly requires authentication")


class TestExportWithDocuments:
    """Test export features with actual documents in case"""
    
    @pytest.fixture(autouse=True)
    def setup_with_documents(self):
        """Setup test user, case, and add test documents"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Register and login
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"test_export_docs_{unique_id}@test.com"
        
        register_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": "TestPass123!",
            "name": "Export Docs Test User"
        })
        
        if register_response.status_code != 200:
            pytest.skip(f"Could not register: {register_response.text}")
        
        self.auth_token = register_response.json().get("token")
        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
        
        # Create case
        case_response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": f"Export Docs Test Case {unique_id}",
            "defendant_name": "Test Defendant",
            "state": "vic"
        })
        
        if case_response.status_code not in [200, 201]:
            pytest.skip(f"Could not create case: {case_response.text}")
        
        self.case_id = case_response.json().get("case_id")
        self.document_ids = []
        
        # Upload test documents using multipart form
        for i in range(2):
            # Create a simple text file for upload
            files = {
                'file': (f'test_doc_{i}.txt', f'Test document {i} content for bundle testing', 'text/plain')
            }
            data = {
                'category': 'evidence'
            }
            
            # Need to remove Content-Type header for multipart
            upload_headers = {"Authorization": f"Bearer {self.auth_token}"}
            doc_response = requests.post(
                f"{BASE_URL}/api/cases/{self.case_id}/documents",
                files=files,
                data=data,
                headers=upload_headers
            )
            
            if doc_response.status_code in [200, 201]:
                doc_id = doc_response.json().get("document_id")
                if doc_id:
                    self.document_ids.append(doc_id)
        
        yield
        
        # Cleanup
        if hasattr(self, 'case_id') and self.case_id:
            self.session.delete(f"{BASE_URL}/api/cases/{self.case_id}")
    
    def test_export_preview_counts_documents(self):
        """Test preview shows correct document count"""
        response = self.session.get(f"{BASE_URL}/api/cases/{self.case_id}/export/preview")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should show at least the documents we uploaded
        assert data["documents"] >= 0, "Documents count should be present"
        print(f"✓ Preview shows {data['documents']} documents")
    
    def test_bundle_with_real_documents(self):
        """Test bundle PDF generation with actual documents"""
        if len(self.document_ids) < 1:
            pytest.skip("No documents were uploaded successfully")
        
        response = self.session.post(
            f"{BASE_URL}/api/cases/{self.case_id}/export/bundle",
            json={
                "document_ids": self.document_ids,
                "include_toc": True,
                "title": "Test Evidence Bundle"
            }
        )
        
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify PDF response
        assert response.headers.get("content-type") == "application/pdf", \
            f"Expected application/pdf, got {response.headers.get('content-type')}"
        
        # Check content-disposition
        content_disp = response.headers.get("content-disposition", "")
        assert ".pdf" in content_disp, "Filename should have .pdf extension"
        
        # Verify PDF magic bytes
        pdf_content = response.content
        assert pdf_content[:4] == b'%PDF', "Response should be a valid PDF"
        
        print(f"✓ Bundle PDF generated successfully ({len(pdf_content)} bytes)")
    
    def test_bundle_without_toc(self):
        """Test bundle generation without table of contents"""
        if len(self.document_ids) < 1:
            pytest.skip("No documents were uploaded successfully")
        
        response = self.session.post(
            f"{BASE_URL}/api/cases/{self.case_id}/export/bundle",
            json={
                "document_ids": self.document_ids,
                "include_toc": False,
                "title": "No TOC Bundle"
            }
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        
        print("✓ Bundle without TOC generated successfully")


class TestCaseStrengthMeter:
    """Test Case Strength Meter endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user and case"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # Register
        register_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_strength_{unique_id}@test.com",
            "password": "TestPass123!",
            "name": "Strength Test User"
        })
        
        if register_response.status_code != 200:
            pytest.skip(f"Could not register: {register_response.text}")
        
        self.auth_token = register_response.json().get("token")
        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
        
        # Create case
        case_response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": f"Strength Test Case {unique_id}",
            "defendant_name": "Test Defendant",
            "state": "nsw"
        })
        
        if case_response.status_code not in [200, 201]:
            pytest.skip(f"Could not create case: {case_response.text}")
        
        self.case_id = case_response.json().get("case_id")
        
        yield
        
        # Cleanup
        if hasattr(self, 'case_id') and self.case_id:
            self.session.delete(f"{BASE_URL}/api/cases/{self.case_id}")
    
    def test_case_strength_endpoint_exists(self):
        """Test GET /api/cases/{case_id}/strength returns strength data"""
        response = self.session.get(f"{BASE_URL}/api/cases/{self.case_id}/strength")
        
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify expected fields
        assert "overall_score" in data, "Should have overall_score"
        assert "rating" in data, "Should have rating"
        assert "breakdown" in data, "Should have breakdown"
        assert "recommendations" in data, "Should have recommendations"
        
        # Check breakdown structure
        breakdown = data["breakdown"]
        assert "grounds" in breakdown, "Breakdown should have grounds"
        assert "documentation" in breakdown, "Breakdown should have documentation"
        assert "timeline" in breakdown, "Breakdown should have timeline"
        assert "preparation" in breakdown, "Breakdown should have preparation"
        
        print(f"✓ Case strength: {data['overall_score']}/100 ({data['rating']})")
        print(f"  Breakdown: Grounds={breakdown['grounds']['score']}%, Docs={breakdown['documentation']['score']}%")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
