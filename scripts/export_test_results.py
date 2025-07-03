#!/usr/bin/env python3
"""
TestRail Test Results Export Script

This script exports test results from JUnit XML to TestRail test runs.
Configuration is loaded from .env file only.
"""

import os
import xml.etree.ElementTree as ET
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urljoin
import logging
from dotenv import load_dotenv
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Represents a test result from JUnit XML"""
    class_name: str
    test_name: str
    status: str  # passed, failed, skipped
    time: float
    error_message: Optional[str] = None
    failure_message: Optional[str] = None

class TestRailAPI:
    """TestRail API client"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated request to TestRail API"""
        url = urljoin(f"{self.base_url}/", f"index.php?/api/v2/{endpoint}")
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project by ID"""
        return self._make_request('GET', f'get_project/{project_id}')
    
    def get_suites(self, project_id: int) -> List[Dict]:
        """Get all suites for a project"""
        result = self._make_request('GET', f'get_suites/{project_id}')
        return result if result else []
    
    def get_sections(self, project_id: int, suite_id: int) -> List[Dict]:
        """Get all sections for a suite"""
        result = self._make_request('GET', f'get_sections/{project_id}&suite_id={suite_id}')
        if result is None:
            return []
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'sections' in result:
            return result['sections']
        else:
            logger.warning(f"Unexpected response format for get_sections: {type(result)}")
            return []
    
    def get_cases(self, project_id: int, suite_id: int, section_id: Optional[int] = None) -> List[Dict]:
        """Get all cases for a suite or section"""
        endpoint = f'get_cases/{project_id}&suite_id={suite_id}'
        if section_id:
            endpoint += f'&section_id={section_id}'
        result = self._make_request('GET', endpoint)
        if result is None:
            return []
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'cases' in result:
            return result['cases']
        else:
            logger.warning(f"Unexpected response format for get_cases: {type(result)}")
            return []
    
    def create_test_run(self, project_id: int, suite_id: int, name: str, description: str = "", case_ids: List[int] = None) -> Optional[Dict]:
        """Create a new test run"""
        data = {
            'suite_id': suite_id,
            'name': name,
            'description': description,
            'include_all': True if not case_ids else False
        }
        if case_ids:
            data['case_ids'] = case_ids
        
        return self._make_request('POST', f'add_run/{project_id}', data)
    
    def add_result(self, run_id: int, case_id: int, status_id: int, comment: str = "", elapsed: str = None) -> Optional[Dict]:
        """Add a test result to a run"""
        data = {
            'status_id': status_id,
            'comment': comment
        }
        if elapsed:
            data['elapsed'] = elapsed
        
        return self._make_request('POST', f'add_result_for_case/{run_id}/{case_id}', data)

class ResultParser:
    """Parser for JUnit XML results"""
    
    @staticmethod
    def parse_junit_xml(file_path: str) -> List[TestResult]:
        """Parse JUnit XML file and extract test results"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            results = []
            
            # Find all testcase elements
            for testcase in root.findall('.//testcase'):
                class_name = testcase.get('classname', '')
                test_name = testcase.get('name', '')
                time = float(testcase.get('time', '0'))
                
                # Determine status
                status = 'passed'
                error_message = None
                failure_message = None
                
                # Check for failure
                failure = testcase.find('failure')
                if failure is not None:
                    status = 'failed'
                    failure_message = failure.text
                
                # Check for error
                error = testcase.find('error')
                if error is not None:
                    status = 'failed'
                    error_message = error.text
                
                # Check for skipped
                skipped = testcase.find('skipped')
                if skipped is not None:
                    status = 'skipped'
                
                result = TestResult(
                    class_name=class_name,
                    test_name=test_name,
                    status=status,
                    time=time,
                    error_message=error_message,
                    failure_message=failure_message
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing JUnit XML file {file_path}: {e}")
            return []
    
    @staticmethod
    def extract_class_name(full_class_name: str) -> str:
        """Extract class name from full classname (e.g., tests.test_models.TestModelsEndpoint -> TestModelsEndpoint)"""
        return full_class_name.split('.')[-1]
    
    @staticmethod
    def remove_test_prefix(name: str) -> str:
        """Remove test prefix from class/method names"""
        if name.startswith('Test'):
            return name[4:]
        elif name.startswith('test_'):
            return name[5:]
        return name
    
    @staticmethod
    def split_camel_case(name: str) -> str:
        """Split camelCase words with spaces"""
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return result

def export_test_results():
    """Main export function"""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment variables
    testrail_url = os.getenv('TESTRAIL_URL')
    username = os.getenv('TESTRAIL_USERNAME')
    password = os.getenv('TESTRAIL_PASSWORD')
    project_id = int(os.getenv('TESTRAIL_PROJECT_ID')) if os.getenv('TESTRAIL_PROJECT_ID') else None
    suite_id = int(os.getenv('TESTRAIL_SUITE_ID')) if os.getenv('TESTRAIL_SUITE_ID') else None
    junit_file = os.getenv('TESTRAIL_JUNIT_FILE', 'test-results.xml')
    
    # Validate required parameters
    if not all([testrail_url, username, password, project_id]):
        logger.error("Missing required environment variables!")
        logger.error("Required: TESTRAIL_URL, TESTRAIL_USERNAME, TESTRAIL_PASSWORD, TESTRAIL_PROJECT_ID")
        return False
    
    # Check if JUnit XML file exists
    if not os.path.exists(junit_file):
        logger.error(f"JUnit XML file not found: {junit_file}")
        return False
    
    logger.info(f"Exporting test results from {junit_file} to TestRail")
    
    # Initialize API client
    api = TestRailAPI(testrail_url, username, password)
    
    # Verify project exists
    project = api.get_project(project_id)
    if not project:
        logger.error(f"Project {project_id} not found")
        return False
    
    logger.info(f"Exporting results for project: {project['name']}")
    
    # Get or determine suite_id
    if not suite_id:
        suites = api.get_suites(project_id)
        if not suites:
            logger.error(f"No suites found in project {project_id}")
            return False
        suite_id = suites[0]['id']
        logger.info(f"Using first available suite: {suites[0]['name']} (ID: {suite_id})")
    else:
        logger.info(f"Using configured suite ID: {suite_id}")
    
    # Parse test results
    parser = ResultParser()
    test_results = parser.parse_junit_xml(junit_file)
    if not test_results:
        logger.error("No test results found in JUnit XML file")
        return False
    
    logger.info(f"Found {len(test_results)} test results")
    
    # Get existing cases
    all_cases = api.get_cases(project_id, suite_id)
    case_map = {}
    for case in all_cases:
        case_map[case['title']] = case
    
    # Create test run
    run_name = f"Test Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    test_run = api.create_test_run(project_id, suite_id, run_name, "Automated test run from pytest")
    
    if not test_run:
        logger.error("Failed to create test run")
        return False
    
    logger.info(f"Created test run: {run_name} (ID: {test_run['id']})")
    
    # Map results to TestRail and add results
    success_count = 0
    failed_count = 0
    
    for result in test_results:
        # Extract and transform names
        case_name = parser.remove_test_prefix(result.test_name)
        
        # Find matching case
        if case_name not in case_map:
            logger.warning(f"Test case not found in TestRail: {case_name}")
            continue
        
        case = case_map[case_name]
        
        # Map status to TestRail status IDs
        status_id = 1  # Passed
        comment = f"Test executed in {result.time:.2f}s"
        
        if result.status == 'failed':
            status_id = 5  # Failed
            comment = f"Test failed in {result.time:.2f}s"
            if result.failure_message:
                comment += f"\n\nFailure: {result.failure_message}"
            if result.error_message:
                comment += f"\n\nError: {result.error_message}"
        elif result.status == 'skipped':
            status_id = 2  # Blocked/Skipped
            comment = f"Test skipped in {result.time:.2f}s"
        
        # Add result to TestRail
        elapsed = f"{int(result.time)}s" if result.time >= 1 else "1s"
        added_result = api.add_result(test_run['id'], case['id'], status_id, comment, elapsed)
        
        if added_result:
            logger.info(f"Added result for {case_name}: {result.status}")
            success_count += 1
        else:
            logger.error(f"Failed to add result for {case_name}")
            failed_count += 1
    
    logger.info(f"Export completed! Successfully added {success_count} results, {failed_count} failed")
    logger.info(f"TestRail run URL: {testrail_url}/index.php?/runs/view/{test_run['id']}")
    
    return True

if __name__ == '__main__':
    success = export_test_results()
    exit(0 if success else 1)