import requests
import sys
import json
from datetime import datetime, date
from typing import Dict, Any

class CRMAPITester:
    def __init__(self, base_url="https://customerbase.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data: Dict[Any, Any] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}, Expected: {expected_status}"
            
            if not success:
                try:
                    error_detail = response.json()
                    details += f", Response: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {}
                
            return success, response_data, response.status_code

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}, 0

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_client_status_types_crud(self):
        """Test client status types CRUD operations"""
        print("\n🔍 Testing Client Status Types CRUD...")
        
        # Get initial status types
        success, initial_data, _ = self.run_test("Get Client Status Types", "GET", "client-status-types", 200)
        if not success:
            return False
        
        initial_count = len(initial_data)
        
        # Create new status type
        new_status = {
            "name": "Test Status",
            "color": "#FF5733"
        }
        success, created_status, _ = self.run_test("Create Client Status Type", "POST", "client-status-types", 200, new_status)
        if not success:
            return False
        
        status_id = created_status.get('id')
        if not status_id:
            self.log_test("Create Status Type - ID Check", False, "No ID returned in response")
            return False
        
        # Update status type
        updated_status = {
            "name": "Updated Test Status",
            "color": "#33FF57"
        }
        success, _, _ = self.run_test("Update Client Status Type", "PUT", f"client-status-types/{status_id}", 200, updated_status)
        if not success:
            return False
        
        # Verify update
        success, all_statuses, _ = self.run_test("Get Status Types After Update", "GET", "client-status-types", 200)
        if success:
            updated_found = any(s.get('name') == 'Updated Test Status' for s in all_statuses)
            self.log_test("Verify Status Update", updated_found, f"Updated status found: {updated_found}")
        
        # Delete status type
        success, _, _ = self.run_test("Delete Client Status Type", "DELETE", f"client-status-types/{status_id}", 200)
        if not success:
            return False
        
        # Verify deletion
        success, final_data, _ = self.run_test("Get Status Types After Delete", "GET", "client-status-types", 200)
        if success:
            final_count = len(final_data)
            deletion_verified = final_count == initial_count
            self.log_test("Verify Status Deletion", deletion_verified, f"Count: {initial_count} -> {final_count}")
        
        return True

    def test_clients_crud(self):
        """Test clients CRUD operations"""
        print("\n🔍 Testing Clients CRUD...")
        
        # Get initial clients
        success, initial_data, _ = self.run_test("Get Clients", "GET", "clients", 200)
        if not success:
            return False
        
        initial_count = len(initial_data)
        
        # Create new client
        new_client = {
            "first_name": "Тест",
            "last_name": "Клієнт",
            "phone": "+380123456789",
            "client_status": "ВІП клієнт",
            "crm_link": "https://example.com/crm/123",
            "expected_order_sets": 5,
            "expected_order_amount": 1500.50,
            "sets_ordered_this_month": 2,
            "amount_this_month": 600.25,
            "debt": 100.00,
            "last_contact_date": "2024-01-15",
            "task_description": "Тестова задача",
            "comment": "Тестовий коментар",
            "action_status": {
                "made_order": True,
                "completed_survey": False,
                "notified_about_promotion": True,
                "has_additional_questions": False,
                "need_callback": False,
                "not_answering": False,
                "planning_order": True
            }
        }
        
        success, created_client, _ = self.run_test("Create Client", "POST", "clients", 200, new_client)
        if not success:
            return False
        
        client_id = created_client.get('id')
        if not client_id:
            self.log_test("Create Client - ID Check", False, "No ID returned in response")
            return False
        
        # Update client
        updated_client = {
            "first_name": "Оновлений",
            "debt": 150.00,
            "action_status": {
                "made_order": True,
                "completed_survey": True,
                "notified_about_promotion": True,
                "has_additional_questions": True,
                "need_callback": True,
                "not_answering": False,
                "planning_order": False
            }
        }
        
        success, _, _ = self.run_test("Update Client", "PUT", f"clients/{client_id}", 200, updated_client)
        if not success:
            return False
        
        # Test client filtering
        success, filtered_data, _ = self.run_test("Filter Clients - Made Order", "GET", "clients?status_filter=made_order", 200)
        if success:
            made_order_count = len(filtered_data)
            self.log_test("Client Filtering Works", made_order_count > 0, f"Found {made_order_count} clients with made_order=true")
        
        # Delete client
        success, _, _ = self.run_test("Delete Client", "DELETE", f"clients/{client_id}", 200)
        if not success:
            return False
        
        # Verify deletion
        success, final_data, _ = self.run_test("Get Clients After Delete", "GET", "clients", 200)
        if success:
            final_count = len(final_data)
            deletion_verified = final_count == initial_count
            self.log_test("Verify Client Deletion", deletion_verified, f"Count: {initial_count} -> {final_count}")
        
        return True

    def test_client_statistics(self):
        """Test client statistics endpoint"""
        print("\n🔍 Testing Client Statistics...")
        
        success, stats_data, _ = self.run_test("Get Client Statistics", "GET", "clients/statistics", 200)
        if not success:
            return False
        
        # Verify statistics structure
        required_fields = [
            'total_clients', 'made_order', 'completed_survey', 
            'notified_about_promotion', 'has_additional_questions',
            'need_callback', 'not_answering', 'planning_order'
        ]
        
        missing_fields = [field for field in required_fields if field not in stats_data]
        
        if missing_fields:
            self.log_test("Statistics Structure", False, f"Missing fields: {missing_fields}")
            return False
        else:
            self.log_test("Statistics Structure", True, "All required fields present")
        
        # Verify data types
        for field in required_fields:
            if not isinstance(stats_data[field], int):
                self.log_test("Statistics Data Types", False, f"Field {field} is not integer: {type(stats_data[field])}")
                return False
        
        self.log_test("Statistics Data Types", True, "All fields are integers")
        return True

    def test_daily_reports_crud(self):
        """Test daily reports CRUD operations"""
        print("\n🔍 Testing Daily Reports CRUD...")
        
        # Get initial reports
        success, initial_data, _ = self.run_test("Get Daily Reports", "GET", "daily-reports", 200)
        if not success:
            return False
        
        initial_count = len(initial_data)
        
        # Create new report
        test_date = "2024-01-20"
        new_report = {
            "date": test_date,
            "orders_in_assembly": 10,
            "sets_count": 25,
            "orders_amount": 5000.00,
            "money_received_today": 3000.00,
            "call_attempts": 50,
            "successful_calls": 30,
            "self_messaged_client": 15,
            "responses": 12,
            "chats_today": 20,
            "clients_no_order": 5,
            "comment": "Тестовий звіт"
        }
        
        success, created_report, _ = self.run_test("Create Daily Report", "POST", "daily-reports", 200, new_report)
        if not success:
            return False
        
        report_id = created_report.get('id')
        if not report_id:
            self.log_test("Create Report - ID Check", False, "No ID returned in response")
            return False
        
        # Try to create duplicate report (should fail)
        success, _, status_code = self.run_test("Create Duplicate Report", "POST", "daily-reports", 400, new_report)
        if status_code != 400:
            self.log_test("Duplicate Report Prevention", False, f"Expected 400, got {status_code}")
        else:
            self.log_test("Duplicate Report Prevention", True, "Correctly prevented duplicate")
        
        # Update report
        updated_report = {
            "orders_in_assembly": 15,
            "comment": "Оновлений тестовий звіт"
        }
        
        success, _, _ = self.run_test("Update Daily Report", "PUT", f"daily-reports/{report_id}", 200, updated_report)
        if not success:
            return False
        
        # Delete report
        success, _, _ = self.run_test("Delete Daily Report", "DELETE", f"daily-reports/{report_id}", 200)
        if not success:
            return False
        
        # Verify deletion
        success, final_data, _ = self.run_test("Get Reports After Delete", "GET", "daily-reports", 200)
        if success:
            final_count = len(final_data)
            deletion_verified = final_count == initial_count
            self.log_test("Verify Report Deletion", deletion_verified, f"Count: {initial_count} -> {final_count}")
        
        return True

    def test_error_handling(self):
        """Test API error handling"""
        print("\n🔍 Testing Error Handling...")
        
        # Test 404 errors
        self.run_test("Get Non-existent Client", "GET", "clients/non-existent-id", 404)
        self.run_test("Update Non-existent Client", "PUT", "clients/non-existent-id", 404, {"first_name": "Test"})
        self.run_test("Delete Non-existent Client", "DELETE", "clients/non-existent-id", 404)
        
        self.run_test("Get Non-existent Status Type", "GET", "client-status-types/non-existent-id", 404)
        self.run_test("Update Non-existent Status Type", "PUT", "client-status-types/non-existent-id", 404, {"name": "Test"})
        self.run_test("Delete Non-existent Status Type", "DELETE", "client-status-types/non-existent-id", 404)
        
        self.run_test("Update Non-existent Report", "PUT", "daily-reports/non-existent-id", 404, {"comment": "Test"})
        self.run_test("Delete Non-existent Report", "DELETE", "daily-reports/non-existent-id", 404)
        
        return True

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting CRM API Testing...")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test basic connectivity
        success, _, _ = self.test_root_endpoint()
        if not success:
            print("❌ Cannot connect to API. Stopping tests.")
            return False
        
        # Run all test suites
        test_suites = [
            self.test_client_status_types_crud,
            self.test_clients_crud,
            self.test_client_statistics,
            self.test_daily_reports_crud,
            self.test_error_handling
        ]
        
        for test_suite in test_suites:
            try:
                test_suite()
            except Exception as e:
                print(f"❌ Test suite failed with exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate < 80:
            print("⚠️  Warning: Low success rate indicates significant API issues")
        elif success_rate < 100:
            print("⚠️  Some tests failed - check details above")
        else:
            print("✅ All tests passed!")
        
        return success_rate >= 80

def main():
    tester = CRMAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "base_url": tester.base_url,
        "total_tests": tester.tests_run,
        "passed_tests": tester.tests_passed,
        "success_rate": (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
        "test_details": tester.test_results
    }
    
    with open('/app/backend_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())