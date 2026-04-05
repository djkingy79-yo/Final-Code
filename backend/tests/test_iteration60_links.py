"""
Iteration 60 - Link Fix Verification Tests
Tests to verify all ReactMarkdown instances have proper link components
with target='_blank' and visible CSS styling
"""
import pytest
import requests

BASE_URL = 'http://localhost:8001'

# ========================
# Backend Health Tests
# ========================
class TestBackendHealth:
    """Backend API health verification"""
    
    def test_health_endpoint_returns_healthy(self):
        """Verify backend health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print("PASS: Backend health endpoint returns healthy")

# ========================
# Frontend Code Verification Tests
# ========================
class TestReactMarkdownLinkComponents:
    """Verify all ReactMarkdown instances have proper link components"""
    
    def test_reportview_has_link_component_with_target_blank(self):
        """ReportView.jsx - MarkdownBlock should have link with target='_blank'"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for ReactMarkdown with remarkPlugins
        assert 'remarkPlugins={[remarkGfm]}' in content, "ReportView.jsx missing remarkPlugins={[remarkGfm]}"
        
        # Check for custom 'a' component with target="_blank"
        assert 'target="_blank"' in content, "ReportView.jsx missing target='_blank' in link component"
        
        # Check for visible CSS classes (text-blue-600 underline)
        assert 'text-blue-600' in content, "ReportView.jsx missing text-blue-600 class for links"
        assert 'underline' in content, "ReportView.jsx missing underline class for links"
        
        # Check for rel="noopener noreferrer" for security
        assert 'rel="noopener noreferrer"' in content, "ReportView.jsx missing rel='noopener noreferrer'"
        
        print("PASS: ReportView.jsx has proper link component with target='_blank' and visible styling")
    
    def test_barristerview_has_link_component_with_target_blank(self):
        """BarristerView.jsx - ReactMarkdown should have link with target='_blank'"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        # Check for ReactMarkdown with remarkPlugins
        assert 'remarkPlugins={[remarkGfm]}' in content, "BarristerView.jsx missing remarkPlugins={[remarkGfm]}"
        
        # Check for custom 'a' component with target="_blank"
        assert 'target="_blank"' in content, "BarristerView.jsx missing target='_blank' in link component"
        
        # Check for visible CSS classes (text-blue-400 for dark theme)
        assert 'text-blue-400' in content, "BarristerView.jsx missing text-blue-400 class for links (dark theme)"
        
        # Check for rel="noopener noreferrer" for security
        assert 'rel="noopener noreferrer"' in content, "BarristerView.jsx missing rel='noopener noreferrer'"
        
        print("PASS: BarristerView.jsx has proper link component with target='_blank' and visible styling")
    
    def test_reportssection_has_link_component_with_target_blank(self):
        """ReportsSection.jsx - Inline report ReactMarkdown should have link with target='_blank'"""
        with open('/app/frontend/src/components/ReportsSection.jsx', 'r') as f:
            content = f.read()
        
        # Check for ReactMarkdown with remarkPlugins
        assert 'remarkPlugins={[remarkGfm]}' in content, "ReportsSection.jsx missing remarkPlugins={[remarkGfm]}"
        
        # Check for custom 'a' component with target="_blank"
        assert 'target="_blank"' in content, "ReportsSection.jsx missing target='_blank' in link component"
        
        # Check for visible CSS classes (text-blue-600 underline)
        assert 'text-blue-600' in content, "ReportsSection.jsx missing text-blue-600 class for links"
        assert 'underline' in content, "ReportsSection.jsx missing underline class for links"
        
        print("PASS: ReportsSection.jsx has proper link component with target='_blank' and visible styling")
    
    def test_groundsofmerit_has_link_component_with_target_blank(self):
        """GroundsOfMerit.jsx - formatAnalysis should have link with target='_blank'"""
        with open('/app/frontend/src/components/GroundsOfMerit.jsx', 'r') as f:
            content = f.read()
        
        # Check for ReactMarkdown import
        assert "import ReactMarkdown from" in content, "GroundsOfMerit.jsx missing ReactMarkdown import"
        
        # Check for ReactMarkdown with remarkPlugins
        assert 'remarkPlugins={[remarkGfm]}' in content, "GroundsOfMerit.jsx missing remarkPlugins={[remarkGfm]}"
        
        # Check for custom 'a' component with target="_blank"
        assert 'target="_blank"' in content, "GroundsOfMerit.jsx missing target='_blank' in link component"
        
        # Check for visible CSS classes (text-blue-600 underline)
        assert 'text-blue-600' in content, "GroundsOfMerit.jsx missing text-blue-600 class for links"
        assert 'underline' in content, "GroundsOfMerit.jsx missing underline class for links"
        
        print("PASS: GroundsOfMerit.jsx has proper link component with target='_blank' and visible styling")
    
    def test_casedetail_progress_has_link_component_with_target_blank(self):
        """CaseDetail.jsx - Progress tab ReactMarkdown should have link with target='_blank'"""
        with open('/app/frontend/src/pages/CaseDetail.jsx', 'r') as f:
            content = f.read()
        
        # Check for ReactMarkdown import
        assert "import ReactMarkdown from" in content, "CaseDetail.jsx missing ReactMarkdown import"
        
        # Check for ReactMarkdown with remarkPlugins
        assert 'remarkPlugins={[remarkGfm]}' in content, "CaseDetail.jsx missing remarkPlugins={[remarkGfm]}"
        
        # Check for custom 'a' component with target="_blank"
        assert 'target="_blank"' in content, "CaseDetail.jsx missing target='_blank' in link component"
        
        # Check for visible CSS classes
        assert 'text-blue-600' in content, "CaseDetail.jsx missing text-blue-600 class for links"
        
        print("PASS: CaseDetail.jsx progress tab has proper link component with target='_blank' and visible styling")


class TestTableComponents:
    """Verify all ReactMarkdown instances have custom table components for responsive tables"""
    
    def test_reportview_has_table_component(self):
        """ReportView.jsx should have custom table component"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert 'table:' in content, "ReportView.jsx missing custom table component"
        assert 'table-wrap' in content or 'overflow' in content, "ReportView.jsx missing table wrapper"
        print("PASS: ReportView.jsx has custom table component")
    
    def test_barristerview_has_table_component(self):
        """BarristerView.jsx should have custom table component"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        assert 'table:' in content, "BarristerView.jsx missing custom table component"
        print("PASS: BarristerView.jsx has custom table component")
    
    def test_reportssection_has_table_component(self):
        """ReportsSection.jsx should have custom table component"""
        with open('/app/frontend/src/components/ReportsSection.jsx', 'r') as f:
            content = f.read()
        
        assert 'table:' in content, "ReportsSection.jsx missing custom table component"
        print("PASS: ReportsSection.jsx has custom table component")
    
    def test_groundsofmerit_has_table_component(self):
        """GroundsOfMerit.jsx should have custom table component"""
        with open('/app/frontend/src/components/GroundsOfMerit.jsx', 'r') as f:
            content = f.read()
        
        assert 'table:' in content, "GroundsOfMerit.jsx missing custom table component"
        print("PASS: GroundsOfMerit.jsx has custom table component")
    
    def test_casedetail_has_table_component(self):
        """CaseDetail.jsx should have custom table component"""
        with open('/app/frontend/src/pages/CaseDetail.jsx', 'r') as f:
            content = f.read()
        
        assert 'table:' in content, "CaseDetail.jsx missing custom table component"
        print("PASS: CaseDetail.jsx has custom table component")


class TestRemarkGfmPlugin:
    """Verify all ReactMarkdown instances have remarkGfm plugin for tables and links"""
    
    def test_all_files_have_remarkgfm_import(self):
        """All files with ReactMarkdown should import remarkGfm"""
        files_to_check = [
            '/app/frontend/src/pages/ReportView.jsx',
            '/app/frontend/src/pages/BarristerView.jsx',
            '/app/frontend/src/components/ReportsSection.jsx',
            '/app/frontend/src/components/GroundsOfMerit.jsx',
            '/app/frontend/src/pages/CaseDetail.jsx'
        ]
        
        for filepath in files_to_check:
            with open(filepath, 'r') as f:
                content = f.read()
            
            assert 'import remarkGfm from' in content, f"{filepath} missing remarkGfm import"
            print(f"PASS: {filepath} has remarkGfm import")


class TestLinkCountAndConsistency:
    """Count and verify consistency of link configurations across all files"""
    
    def test_count_target_blank_occurrences(self):
        """Count target='_blank' occurrences to ensure all links open in new tab"""
        files_to_check = [
            ('/app/frontend/src/pages/ReportView.jsx', 1),  # MarkdownBlock component
            ('/app/frontend/src/pages/BarristerView.jsx', 1),  # Analysis section
            ('/app/frontend/src/components/ReportsSection.jsx', 1),  # Inline report
            ('/app/frontend/src/components/GroundsOfMerit.jsx', 1),  # formatAnalysis
            ('/app/frontend/src/pages/CaseDetail.jsx', 1)  # Progress analysis
        ]
        
        total_count = 0
        for filepath, min_expected in files_to_check:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Count target="_blank" occurrences within ReactMarkdown components block
            count = content.count('target="_blank"')
            assert count >= min_expected, f"{filepath} has {count} target='_blank', expected at least {min_expected}"
            total_count += count
            print(f"PASS: {filepath} has {count} target='_blank' occurrence(s)")
        
        print(f"PASS: Total target='_blank' occurrences: {total_count}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
