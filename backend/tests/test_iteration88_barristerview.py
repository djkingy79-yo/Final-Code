"""
Iteration 88 Tests - BarristerView.jsx Merge Logic Rewrite
Tests for the new category-based merge approach in BarristerView.jsx

Key changes tested:
1. MERGE_CATEGORIES exists with 15 categories
2. classifySection function correctly categorises sections
3. parseAnalysis function splits content by ## headings
4. mergeAllReports uses category-based logic
5. cleanSentence truncates to max 80 characters
6. No duplicate function definitions (selectDistinctParagraphs, buildSynthesisSection removed)
7. Section titles use text-slate-900 (visible dark text)
8. Backend health check works
"""

import pytest
import requests
import re

BASE_URL = 'http://localhost:8001'


class TestBackendHealth:
    """Backend health check tests"""
    
    def test_health_endpoint(self):
        """Test that backend health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert data.get("database") == "connected"
        print(f"Health check passed: {data}")


class TestBarristerViewCodeStructure:
    """Tests to verify BarristerView.jsx code structure"""
    
    @pytest.fixture(scope="class")
    def barrister_view_content(self):
        """Read BarristerView.jsx content"""
        with open("/app/frontend/src/pages/BarristerView.jsx", "r") as f:
            return f.read()
    
    def test_merge_categories_exists(self, barrister_view_content):
        """Test that MERGE_CATEGORIES constant exists with 15 categories"""
        # Check MERGE_CATEGORIES is defined
        assert "const MERGE_CATEGORIES = [" in barrister_view_content
        
        # Count the number of category definitions
        category_pattern = r'\{\s*id:\s*"[A-Z_]+"'
        categories = re.findall(category_pattern, barrister_view_content)
        assert len(categories) == 15, f"Expected 15 categories, found {len(categories)}"
        
        # Verify key categories exist
        expected_categories = [
            "EXECUTIVE", "CHRONOLOGY", "EVIDENCE", "GROUNDS", "SENTENCING",
            "COMMON_GROUNDS", "OUTCOME", "PRECEDENT", "STATUTORY", "STRATEGY",
            "SUBMISSIONS", "HEARING", "FORMS", "ACTION", "PLAIN_ENGLISH"
        ]
        for cat in expected_categories:
            assert f'id: "{cat}"' in barrister_view_content, f"Category {cat} not found"
        print(f"MERGE_CATEGORIES verified with {len(categories)} categories")
    
    def test_classify_section_function_exists(self, barrister_view_content):
        """Test that classifySection function exists and uses MERGE_CATEGORIES"""
        assert "const classifySection = (title) =>" in barrister_view_content
        # Verify it iterates over MERGE_CATEGORIES
        assert "for (const cat of MERGE_CATEGORIES)" in barrister_view_content
        print("classifySection function verified")
    
    def test_parse_analysis_function_exists(self, barrister_view_content):
        """Test that parseAnalysis function exists and splits by ## headings"""
        assert "const parseAnalysis = (content) =>" in barrister_view_content
        # Verify it handles ## headings
        assert "^#{1,3}\\s+" in barrister_view_content or "headerMatch" in barrister_view_content
        print("parseAnalysis function verified")
    
    def test_merge_all_reports_uses_categories(self, barrister_view_content):
        """Test that mergeAllReports uses category-based logic"""
        assert "const mergeAllReports = () =>" in barrister_view_content
        # Verify it uses classifySection
        assert "classifySection(section.title)" in barrister_view_content
        # Verify it uses categoryBuckets
        assert "categoryBuckets" in barrister_view_content
        # Verify it iterates over MERGE_CATEGORIES
        assert "MERGE_CATEGORIES.forEach((cat) =>" in barrister_view_content
        print("mergeAllReports category-based logic verified")
    
    def test_clean_sentence_truncates_to_80_chars(self, barrister_view_content):
        """Test that cleanSentence truncates to max 80 characters"""
        assert "const cleanSentence = (s) =>" in barrister_view_content
        # Verify truncation logic
        assert "if (c.length > 80)" in barrister_view_content
        assert 'c.substring(0, 77) + "..."' in barrister_view_content
        print("cleanSentence 80-char truncation verified")
    
    def test_no_duplicate_functions_removed(self, barrister_view_content):
        """Test that old helper functions are removed"""
        # These functions should NOT exist
        assert "selectDistinctParagraphs" not in barrister_view_content, \
            "selectDistinctParagraphs should be removed"
        assert "buildSynthesisSection" not in barrister_view_content, \
            "buildSynthesisSection should be removed"
        print("Old helper functions (selectDistinctParagraphs, buildSynthesisSection) confirmed removed")
    
    def test_section_titles_use_dark_text(self, barrister_view_content):
        """Test that section titles use text-slate-900 (visible dark text)"""
        # Check that text-slate-900 is used for section titles
        # The section title in the Comprehensive Analysis area should use text-slate-900
        assert "text-slate-900" in barrister_view_content
        
        # Verify text-slate-100 is NOT used for section titles (would be invisible on light bg)
        # Count occurrences - text-slate-100 should not appear in section title contexts
        slate_100_count = barrister_view_content.count("text-slate-100")
        slate_900_count = barrister_view_content.count("text-slate-900")
        
        # text-slate-900 should be used much more than text-slate-100
        assert slate_900_count > slate_100_count, \
            f"text-slate-900 ({slate_900_count}) should be more common than text-slate-100 ({slate_100_count})"
        print(f"Section title colors verified: text-slate-900 ({slate_900_count}) > text-slate-100 ({slate_100_count})")
    
    def test_table_of_contents_structure(self, barrister_view_content):
        """Test that Table of Contents shows fixed structural sections"""
        # Verify TOC has fixed sections I-VI
        assert 'data-testid="barrister-toc"' in barrister_view_content
        assert "Table of Contents" in barrister_view_content
        # Check for Roman numerals in TOC
        assert ">I</span>" in barrister_view_content
        assert ">II</span>" in barrister_view_content
        assert ">III</span>" in barrister_view_content
        assert ">IV</span>" in barrister_view_content
        print("Table of Contents structure verified")


class TestFrontendCompilation:
    """Test that frontend compiles without errors"""
    
    def test_frontend_build_succeeds(self):
        """Verify frontend build completed successfully"""
        import subprocess
        result = subprocess.run(
            ["yarn", "build"],
            cwd="/app/frontend",
            capture_output=True,
            text=True,
            timeout=120
        )
        # Build should succeed (exit code 0)
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        assert "The build folder is ready to be deployed" in result.stdout
        print("Frontend build succeeded")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
