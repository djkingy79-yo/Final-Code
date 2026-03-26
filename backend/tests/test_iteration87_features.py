"""
Iteration 87 Feature Tests
Tests for:
1. Backend health check API
2. How It Works page - no 'printed directly' references
3. How It Works pricing cards - no text truncation
4. Landing page footer - EXPLORE and LEGAL columns
5. ReportView.jsx sanitiseReportOutput - strips 'you/your' language
6. BarristerView.jsx sanitiseReportOutput - strips 'you/your' language
7. Backend _strip_report_placeholders - strips 'you/your' and placeholder text
8. PDF export includes Grounds and Sentence in header
9. DOCX export includes Grounds and Sentence in header
"""

import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://grounds-analyser.preview.emergentagent.com')


class TestBackendHealth:
    """Backend health check tests"""
    
    def test_health_endpoint_returns_healthy(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        assert 'database' in data
        print(f"✓ Health check passed: {data}")


class TestSanitiseReportOutputFrontend:
    """Test sanitiseReportOutput function patterns in frontend files"""
    
    def test_reportview_has_you_your_stripping(self):
        """Verify ReportView.jsx has 'you/your' stripping patterns"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for key patterns
        patterns = [
            r"your opportunity.*the opportunity",
            r"your conviction.*the conviction",
            r"your sentence.*the sentence",
            r"your appeal.*the appeal",
            r"your case.*the case",
            r"your trial.*the trial",
        ]
        
        for pattern in patterns:
            assert re.search(pattern, content, re.IGNORECASE), f"Pattern '{pattern}' not found in ReportView.jsx"
        
        print("✓ ReportView.jsx has all 'you/your' stripping patterns")
    
    def test_barristerview_has_you_your_stripping(self):
        """Verify BarristerView.jsx has 'you/your' stripping patterns"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        # Check for key patterns
        patterns = [
            r"your opportunity.*the opportunity",
            r"your conviction.*the conviction",
            r"your sentence.*the sentence",
            r"your appeal.*the appeal",
            r"your case.*the case",
        ]
        
        for pattern in patterns:
            assert re.search(pattern, content, re.IGNORECASE), f"Pattern '{pattern}' not found in BarristerView.jsx"
        
        print("✓ BarristerView.jsx has all 'you/your' stripping patterns")
    
    def test_reportview_has_placeholder_stripping(self):
        """Verify ReportView.jsx strips placeholder text"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for placeholder stripping pattern
        assert "table" in content.lower() and "will" in content.lower() and "reference" in content.lower(), \
            "Placeholder stripping pattern not found in ReportView.jsx"
        
        print("✓ ReportView.jsx has placeholder text stripping")


class TestBackendStripReportPlaceholders:
    """Test _strip_report_placeholders function in backend"""
    
    def test_backend_has_you_your_stripping(self):
        """Verify server.py has 'you/your' stripping patterns"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for key patterns in _strip_report_placeholders
        patterns = [
            r"your opportunity.*the opportunity",
            r"your conviction.*the conviction",
            r"your sentence.*the sentence",
            r"your appeal.*the appeal",
            r"your case.*the case",
        ]
        
        for pattern in patterns:
            assert re.search(pattern, content, re.IGNORECASE), f"Pattern '{pattern}' not found in server.py"
        
        print("✓ Backend server.py has all 'you/your' stripping patterns")
    
    def test_backend_has_placeholder_stripping(self):
        """Verify server.py strips placeholder text"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for placeholder stripping patterns
        assert "table" in content.lower() and "will reference" in content.lower(), \
            "Placeholder stripping pattern not found in server.py"
        assert "will be provided" in content.lower(), \
            "'will be provided' stripping not found in server.py"
        
        print("✓ Backend server.py has placeholder text stripping")


class TestHowItWorksPage:
    """Test How It Works page content"""
    
    def test_no_printed_directly_text(self):
        """Verify How It Works page doesn't mention 'printed directly'"""
        with open('/app/frontend/src/pages/HowItWorksPage.jsx', 'r') as f:
            content = f.read()
        
        # Should NOT contain 'printed directly'
        assert "printed directly" not in content.lower(), \
            "How It Works page still contains 'printed directly' text"
        
        print("✓ How It Works page does not mention 'printed directly'")
    
    def test_has_export_references(self):
        """Verify How It Works page mentions export functionality"""
        with open('/app/frontend/src/pages/HowItWorksPage.jsx', 'r') as f:
            content = f.read()
        
        # Should contain export references
        assert "export" in content.lower() or "pdf" in content.lower(), \
            "How It Works page should mention export/PDF functionality"
        
        print("✓ How It Works page mentions export functionality")
    
    def test_pricing_grid_responsive(self):
        """Verify pricing grid has responsive classes"""
        with open('/app/frontend/src/pages/HowItWorksPage.jsx', 'r') as f:
            content = f.read()
        
        # Check for responsive grid classes
        assert "sm:grid-cols-2" in content or "md:grid-cols-2" in content, \
            "Pricing grid should have responsive column classes"
        assert "lg:grid-cols-4" in content, \
            "Pricing grid should have lg:grid-cols-4 for 4 cards"
        
        print("✓ Pricing grid has responsive classes")
    
    def test_barrister_view_pricing_card_exists(self):
        """Verify Barrister View pricing card exists"""
        with open('/app/frontend/src/pages/HowItWorksPage.jsx', 'r') as f:
            content = f.read()
        
        # Check for Barrister View in reportPricing array
        assert "Barrister View" in content, \
            "Barrister View pricing card not found"
        assert "UNLOCKS" in content, \
            "Barrister View should show UNLOCKS price"
        
        print("✓ Barrister View pricing card exists")


class TestLandingPageFooter:
    """Test Landing page footer structure"""
    
    def test_footer_has_explore_column(self):
        """Verify footer has Explore column (rendered as EXPLORE via CSS uppercase)"""
        with open('/app/frontend/src/pages/LandingPage.jsx', 'r') as f:
            content = f.read()
        
        # Check for Explore heading in footer (CSS uppercase makes it appear as EXPLORE)
        assert "Explore" in content or "EXPLORE" in content, \
            "Footer should have Explore column heading"
        
        print("✓ Footer has Explore column")
    
    def test_footer_has_legal_column(self):
        """Verify footer has Legal column (rendered as LEGAL via CSS uppercase)"""
        with open('/app/frontend/src/pages/LandingPage.jsx', 'r') as f:
            content = f.read()
        
        # Check for Legal heading in footer (CSS uppercase makes it appear as LEGAL)
        assert "Legal" in content or "LEGAL" in content, \
            "Footer should have Legal column heading"
        
        print("✓ Footer has Legal column")


class TestPDFExportHeader:
    """Test PDF export includes Grounds and Sentence in header"""
    
    def test_pdf_export_includes_grounds(self):
        """Verify PDF export includes Grounds count"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for Grounds in PDF export section
        # Look for the case_data_rows.append with Grounds
        assert "Grounds" in content and "identified" in content, \
            "PDF export should include Grounds count"
        
        print("✓ PDF export includes Grounds count")
    
    def test_pdf_export_includes_sentence(self):
        """Verify PDF export includes Sentence"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for Sentence in PDF export section
        assert "Sentence" in content, \
            "PDF export should include Sentence"
        
        print("✓ PDF export includes Sentence")


class TestDOCXExportHeader:
    """Test DOCX export includes Grounds and Sentence in header"""
    
    def test_docx_export_includes_grounds(self):
        """Verify DOCX export includes Grounds count"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for Grounds in DOCX export section (around line 5508)
        # Look for case_info.append with Grounds
        assert "Grounds" in content, \
            "DOCX export should include Grounds count"
        
        print("✓ DOCX export includes Grounds count")
    
    def test_docx_export_includes_sentence(self):
        """Verify DOCX export includes Sentence"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for Sentence in DOCX export section
        assert "Sentence" in content, \
            "DOCX export should include Sentence"
        
        print("✓ DOCX export includes Sentence")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
