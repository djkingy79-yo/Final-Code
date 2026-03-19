#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Justitia AI - Criminal Appeal Case Management
Tests all CRUD operations, authentication, and AI report generation
"""

import requests
import sys
import json
import time
from datetime import datetime
from io import BytesIO

class JustitiaAPITester:
    def __init__(self, base_url="https://barrister-toolkit.preview.emergentagent.com"):
        self.base_url = base_url
        self.session_token = "test_session_notes_1770882054339"  # Updated test session
        self.user_id = "test-user-notes-1770882054339"
        self.tests_run = 0
        self.tests_passed = 0
        self.case_id = "case_64f57656cd75"  # Use existing test case
        self.document_id = None
        self.event_id = None
        self.report_id = None
        self.note_id = None
        self.ground_ids = []  # Track created grounds for testing

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.session_token:
            headers['Authorization'] = f'Bearer {self.session_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if files:
                # Remove Content-Type for file uploads
                headers.pop('Content-Type', None)
                
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, headers=headers)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n" + "="*50)
        print("TESTING HEALTH & BASIC ENDPOINTS")
        print("="*50)
        
        self.run_test("Root endpoint", "GET", "", 200)
        self.run_test("Health check", "GET", "health", 200)

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION")
        print("="*50)
        
        success, user_data = self.run_test("Get current user", "GET", "auth/me", 200)
        if success and user_data:
            print(f"   User: {user_data.get('name')} ({user_data.get('email')})")
            return True
        return False

    def test_case_management(self):
        """Test case CRUD operations"""
        print("\n" + "="*50)
        print("TESTING CASE MANAGEMENT")
        print("="*50)
        
        # Get initial cases
        self.run_test("Get all cases (initial)", "GET", "cases", 200)
        
        # Use existing test case
        print(f"   Using existing test case ID: {self.case_id}")
            
        # Get specific case
        success, response = self.run_test("Get specific case", "GET", f"cases/{self.case_id}", 200)
        if success and response:
            print(f"   Case title: {response.get('title')}")
            print(f"   Defendant: {response.get('defendant_name')}")
        
        return True

    def test_document_management(self):
        """Test document upload and management"""
        print("\n" + "="*50)
        print("TESTING DOCUMENT MANAGEMENT")
        print("="*50)
        
        if not self.case_id:
            print("❌ No case ID available for document testing")
            return False
            
        # Get initial documents
        self.run_test("Get case documents (initial)", "GET", f"cases/{self.case_id}/documents", 200)
        
        # Create a test file
        test_content = "This is a test legal brief document for the criminal appeal case."
        test_file = BytesIO(test_content.encode('utf-8'))
        
        # Upload document
        files = {'file': ('test_brief.txt', test_file, 'text/plain')}
        form_data = {
            'category': 'brief',
            'description': 'Test legal brief document'
        }
        
        success, response = self.run_test(
            "Upload document", 
            "POST", 
            f"cases/{self.case_id}/documents", 
            200, 
            data=form_data, 
            files=files
        )
        
        if success and response:
            self.document_id = response.get('document_id')
            print(f"   Uploaded document ID: {self.document_id}")
        
        # Get documents after upload
        self.run_test("Get case documents (after upload)", "GET", f"cases/{self.case_id}/documents", 200)
        
        if self.document_id:
            # Get specific document
            self.run_test("Get specific document", "GET", f"cases/{self.case_id}/documents/{self.document_id}", 200)
        
        return True

    def test_timeline_management(self):
        """Test timeline event management"""
        print("\n" + "="*50)
        print("TESTING TIMELINE MANAGEMENT")
        print("="*50)
        
        if not self.case_id:
            print("❌ No case ID available for timeline testing")
            return False
            
        # Get initial timeline
        self.run_test("Get case timeline (initial)", "GET", f"cases/{self.case_id}/timeline", 200)
        
        # Create timeline event
        event_data = {
            "title": "Initial Arrest",
            "description": "Defendant was arrested on suspicion of murder",
            "event_date": "2024-01-15T10:30:00Z",
            "event_type": "arrest"
        }
        
        success, response = self.run_test("Create timeline event", "POST", f"cases/{self.case_id}/timeline", 200, event_data)
        if success and response:
            self.event_id = response.get('event_id')
            print(f"   Created event ID: {self.event_id}")
        
        # Get timeline after creation
        self.run_test("Get case timeline (after create)", "GET", f"cases/{self.case_id}/timeline", 200)
        
        if self.event_id:
            # Update timeline event
            update_event_data = {
                "title": "Initial Arrest (Updated)",
                "description": "Defendant was arrested on suspicion of murder - updated details",
                "event_date": "2024-01-15T10:30:00Z",
                "event_type": "arrest"
            }
            self.run_test("Update timeline event", "PUT", f"cases/{self.case_id}/timeline/{self.event_id}", 200, update_event_data)
        
        return True

    def test_notes_management(self):
        """Test notes CRUD operations and pin functionality"""
        print("\n" + "="*50)
        print("TESTING NOTES MANAGEMENT")
        print("="*50)
        
        if not self.case_id:
            print("❌ No case ID available for notes testing")
            return False
            
        # Get initial notes
        self.run_test("Get case notes (initial)", "GET", f"cases/{self.case_id}/notes", 200)
        
        # Create a new note
        note_data = {
            "title": "Test Legal Opinion Note",
            "content": "This is a test legal opinion regarding the criminal appeal case. The evidence suggests potential grounds for appeal based on procedural irregularities.",
            "category": "legal_opinion",
            "is_pinned": False
        }
        
        success, response = self.run_test("Create new note", "POST", f"cases/{self.case_id}/notes", 200, note_data)
        if success and response:
            self.note_id = response.get('note_id')
            print(f"   Created note ID: {self.note_id}")
            print(f"   Note title: {response.get('title')}")
            print(f"   Note category: {response.get('category')}")
        
        if not self.note_id:
            print("❌ Cannot continue notes testing without note ID")
            return False
            
        # Get specific note
        self.run_test("Get specific note", "GET", f"cases/{self.case_id}/notes/{self.note_id}", 200)
        
        # Update note
        update_data = {
            "title": "Updated Legal Opinion Note",
            "content": "This is an updated legal opinion with additional analysis of the criminal appeal case.",
            "category": "strategy"
        }
        self.run_test("Update note", "PUT", f"cases/{self.case_id}/notes/{self.note_id}", 200, update_data)
        
        # Toggle pin status
        success, response = self.run_test("Pin note", "PATCH", f"cases/{self.case_id}/notes/{self.note_id}/pin", 200)
        if success and response:
            print(f"   Note pinned status: {response.get('is_pinned')}")
        
        # Toggle pin status again (unpin)
        success, response = self.run_test("Unpin note", "PATCH", f"cases/{self.case_id}/notes/{self.note_id}/pin", 200)
        if success and response:
            print(f"   Note pinned status: {response.get('is_pinned')}")
        
        # Create additional notes to test sorting
        note_categories = ["general", "evidence_note", "question", "action_item"]
        additional_note_ids = []
        
        for i, category in enumerate(note_categories):
            note_data = {
                "title": f"Test {category.replace('_', ' ').title()} Note {i+1}",
                "content": f"This is a test {category} note for testing sorting and categorization.",
                "category": category,
                "is_pinned": i % 2 == 0  # Pin every other note
            }
            
            success, response = self.run_test(f"Create {category} note", "POST", f"cases/{self.case_id}/notes", 200, note_data)
            if success and response:
                additional_note_ids.append(response.get('note_id'))
        
        # Get all notes after creation (should be sorted by pinned status then date)
        success, response = self.run_test("Get all notes (sorted)", "GET", f"cases/{self.case_id}/notes", 200)
        if success and response:
            print(f"   Total notes created: {len(response)}")
            pinned_count = sum(1 for note in response if note.get('is_pinned'))
            print(f"   Pinned notes: {pinned_count}")
        
        # Store additional note IDs for cleanup
        self.additional_note_ids = additional_note_ids
        
        return True

    def test_ai_report_generation(self):
        """Test AI-powered report generation"""
        print("\n" + "="*50)
        print("TESTING AI REPORT GENERATION")
        print("="*50)
        
        if not self.case_id:
            print("❌ No case ID available for report testing")
            return False
            
        # Get initial reports
        self.run_test("Get case reports (initial)", "GET", f"cases/{self.case_id}/reports", 200)
        
        # Generate Quick Summary report
        print("   Generating Quick Summary report (this may take 10-15 seconds)...")
        report_data = {"report_type": "quick_summary"}
        
        success, response = self.run_test("Generate Quick Summary report", "POST", f"cases/{self.case_id}/reports/generate", 200, report_data)
        if success and response:
            self.report_id = response.get('report_id')
            print(f"   Generated report ID: {self.report_id}")
            print(f"   Report title: {response.get('title')}")
        
        # Get reports after generation
        self.run_test("Get case reports (after generate)", "GET", f"cases/{self.case_id}/reports", 200)
        
        if self.report_id:
            # Get specific report
            self.run_test("Get specific report", "GET", f"cases/{self.case_id}/reports/{self.report_id}", 200)
        
        return True

    def test_grounds_of_merit(self):
        """Test Grounds of Merit functionality"""
        print("\n" + "="*50)
        print("TESTING GROUNDS OF MERIT")
        print("="*50)
        
        # Get initial grounds (should be empty or existing)
        success, response = self.run_test("Get initial grounds", "GET", f"cases/{self.case_id}/grounds", 200)
        initial_count = len(response) if success and response else 0
        print(f"   Initial grounds count: {initial_count}")
        
        # Create a ground manually
        ground_data = {
            "title": "Inadequate Legal Representation at Trial",
            "ground_type": "ineffective_counsel",
            "description": "Defense counsel failed to present key evidence and did not adequately cross-examine prosecution witnesses, resulting in a miscarriage of justice.",
            "strength": "strong",
            "supporting_evidence": ["Trial transcript pages 45-67", "Witness statement from John Smith", "Expert opinion on defense strategy"]
        }
        
        success, response = self.run_test("Create ground manually", "POST", f"cases/{self.case_id}/grounds", 201, ground_data)
        if success and response.get('ground_id'):
            ground_id = response['ground_id']
            self.ground_ids.append(ground_id)
            print(f"   Created ground ID: {ground_id}")
            print(f"   Ground type: {response.get('ground_type')}")
            print(f"   Strength: {response.get('strength')}")
        
        # Get grounds list after creation
        success, response = self.run_test("Get grounds after creation", "GET", f"cases/{self.case_id}/grounds", 200)
        if success:
            print(f"   Total grounds now: {len(response)}")
        
        # Get specific ground
        if self.ground_ids:
            ground_id = self.ground_ids[0]
            success, response = self.run_test("Get specific ground", "GET", f"cases/{self.case_id}/grounds/{ground_id}", 200)
            if success:
                print(f"   Retrieved ground: {response.get('title')}")
        
        # Test AI investigation of ground
        if self.ground_ids:
            ground_id = self.ground_ids[0]
            print("   🤖 Testing AI investigation (may take 10-15 seconds)...")
            success, response = self.run_test("AI investigate ground", "POST", f"cases/{self.case_id}/grounds/{ground_id}/investigate", 200)
            if success:
                print(f"   Investigation status: {response.get('status')}")
                if response.get('analysis'):
                    print(f"   Analysis length: {len(response['analysis'])} chars")
                if response.get('law_sections'):
                    print(f"   Law sections found: {len(response['law_sections'])}")
                if response.get('similar_cases'):
                    print(f"   Similar cases found: {len(response['similar_cases'])}")
        
        # Test AI auto-identify grounds
        print("   🤖 Testing AI auto-identify (may take 15-20 seconds)...")
        success, response = self.run_test("AI auto-identify grounds", "POST", f"cases/{self.case_id}/grounds/auto-identify", 200)
        if success:
            identified_count = response.get('identified_count', 0)
            print(f"   AI identified {identified_count} new grounds")
            if response.get('grounds'):
                for ground in response['grounds']:
                    if ground.get('ground_id'):
                        self.ground_ids.append(ground['ground_id'])
                        print(f"   - {ground.get('title', 'Untitled')} ({ground.get('ground_type', 'unknown')})")
        
        # Test updating a ground
        if self.ground_ids:
            ground_id = self.ground_ids[0]
            update_data = {
                "strength": "moderate",
                "status": "confirmed"
            }
            success, response = self.run_test("Update ground", "PUT", f"cases/{self.case_id}/grounds/{ground_id}", 200, update_data)
            if success:
                print(f"   Updated strength: {response.get('strength')}")
                print(f"   Updated status: {response.get('status')}")
        
        return True

    def test_cleanup_operations(self):
        """Test delete operations"""
        print("\n" + "="*50)
        print("TESTING CLEANUP OPERATIONS")
        print("="*50)
        
        # Delete notes
        if hasattr(self, 'note_id') and self.note_id:
            self.run_test("Delete main note", "DELETE", f"cases/{self.case_id}/notes/{self.note_id}", 200)
        
        if hasattr(self, 'additional_note_ids'):
            for i, note_id in enumerate(self.additional_note_ids):
                if note_id:
                    self.run_test(f"Delete additional note {i+1}", "DELETE", f"cases/{self.case_id}/notes/{note_id}", 200)
        
        # Delete report
        if self.report_id:
            self.run_test("Delete report", "DELETE", f"cases/{self.case_id}/reports/{self.report_id}", 200)
        
        # Delete document
        if self.document_id:
            self.run_test("Delete document", "DELETE", f"cases/{self.case_id}/documents/{self.document_id}", 200)
        
        # Delete timeline event
        if self.event_id:
            self.run_test("Delete timeline event", "DELETE", f"cases/{self.case_id}/timeline/{self.event_id}", 200)
        
        # Delete grounds of merit
        for i, ground_id in enumerate(self.ground_ids):
            if ground_id:
                self.run_test(f"Delete ground {i+1}", "DELETE", f"cases/{self.case_id}/grounds/{ground_id}", 200)
        
        # Note: Not deleting the test case since it's a shared test case

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n" + "="*50)
        print("TESTING ERROR HANDLING")
        print("="*50)
        
        # Test invalid case ID
        self.run_test("Get non-existent case", "GET", "cases/invalid-case-id", 404)
        
        # Test invalid report generation
        invalid_report_data = {"report_type": "invalid_type"}
        self.run_test("Generate invalid report type", "POST", f"cases/invalid-case/reports/generate", 404, invalid_report_data)
        
        # Test unauthorized access (without token)
        old_token = self.session_token
        self.session_token = None
        self.run_test("Unauthorized access", "GET", "cases", 401)
        self.session_token = old_token

def main():
    print("🏛️  JUSTITIA AI - CRIMINAL APPEAL CASE MANAGEMENT API TESTING")
    print("=" * 70)
    print(f"Backend URL: https://barrister-toolkit.preview.emergentagent.com")
    print(f"Test User: test-user-notes-1770882054339")
    print(f"Session Token: test_session_notes_1770882054339")
    print(f"Test Case ID: case_64f57656cd75")
    print("=" * 70)
    
    tester = JustitiaAPITester()
    
    # Run all test suites
    try:
        tester.test_health_check()
        
        if not tester.test_authentication():
            print("\n❌ Authentication failed - stopping tests")
            return 1
            
        tester.test_case_management()
        tester.test_document_management()
        tester.test_timeline_management()
        tester.test_notes_management()  # Add notes testing
        tester.test_grounds_of_merit()  # Add grounds of merit testing
        tester.test_ai_report_generation()
        tester.test_error_handling()
        tester.test_cleanup_operations()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        return 1
    
    # Print final results
    print("\n" + "="*70)
    print("📊 FINAL TEST RESULTS")
    print("="*70)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {tester.tests_run - tester.tests_passed} TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())