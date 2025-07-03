#!/usr/bin/env python3
"""
TestRail Test Case Synchronization Script

This script syncs test cases from pytest test files to TestRail.
Configuration is loaded from .env file only.
"""

import os
import ast
import requests
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urljoin
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Represents a test case"""
    name: str
    original_name: str
    class_name: str
    file_path: str

@dataclass
class TestSection:
    """Represents a test section"""
    name: str
    original_name: str
    test_cases: List[TestCase]

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
        # Handle both list and dict responses
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'sections' in result:
            return result['sections']
        else:
            logger.warning(f"Unexpected response format for get_sections: {type(result)}")
            return []
    
    def create_section(self, project_id: int, suite_id: int, name: str, description: str = "") -> Optional[Dict]:
        """Create a new section"""
        data = {
            'name': name,
            'description': description,
            'suite_id': suite_id
        }
        return self._make_request('POST', f'add_section/{project_id}', data)
    
    def get_cases(self, project_id: int, suite_id: int, section_id: Optional[int] = None) -> List[Dict]:
        """Get all cases for a suite or section"""
        endpoint = f'get_cases/{project_id}&suite_id={suite_id}'
        if section_id:
            endpoint += f'&section_id={section_id}'
        result = self._make_request('GET', endpoint)
        if result is None:
            return []
        # Handle both list and dict responses
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'cases' in result:
            return result['cases']
        else:
            logger.warning(f"Unexpected response format for get_cases: {type(result)}")
            return []
    
    def create_case(self, section_id: int, title: str, description: str = "") -> Optional[Dict]:
        """Create a new test case"""
        data = {
            'title': title,
            'template_id': 1,  # Test Case (Text)
            'type_id': 1,      # Automated
            'priority_id': 2,  # Medium
            'estimate': '1m',
            'custom_automation_type': 0,  # None
            'custom_preconds': description
        }
        return self._make_request('POST', f'add_case/{section_id}', data)

class TestParser:
    """Parser for Python test files"""
    
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
        import re
        # Insert space before uppercase letters that follow lowercase letters
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return result
    
    @staticmethod
    def parse_test_file(file_path: str) -> List[TestSection]:
        """Parse a Python test file and extract test classes and methods"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            sections = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                    test_cases = []
                    
                    for class_node in node.body:
                        if isinstance(class_node, ast.FunctionDef) and class_node.name.startswith('test_'):
                            test_case = TestCase(
                                name=TestParser.remove_test_prefix(class_node.name),
                                original_name=class_node.name,
                                class_name=node.name,
                                file_path=file_path
                            )
                            test_cases.append(test_case)
                    
                    if test_cases:
                        section_name = TestParser.remove_test_prefix(node.name)
                        section_name = TestParser.split_camel_case(section_name)
                        section = TestSection(
                            name=section_name,
                            original_name=node.name,
                            test_cases=test_cases
                        )
                        sections.append(section)
            
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return []
    
    @staticmethod
    def find_test_files(directory: str) -> List[str]:
        """Find all test files in a directory"""
        test_files = []
        test_dir = Path(directory)
        
        if not test_dir.exists():
            logger.error(f"Directory {directory} does not exist")
            return test_files
        
        for file_path in test_dir.rglob('test_*.py'):
            test_files.append(str(file_path))
        
        return sorted(test_files)

def sync_tests():
    """Main sync function"""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment variables
    testrail_url = os.getenv('TESTRAIL_URL')
    username = os.getenv('TESTRAIL_USERNAME')
    password = os.getenv('TESTRAIL_PASSWORD')
    project_id = int(os.getenv('TESTRAIL_PROJECT_ID')) if os.getenv('TESTRAIL_PROJECT_ID') else None
    suite_id = int(os.getenv('TESTRAIL_SUITE_ID')) if os.getenv('TESTRAIL_SUITE_ID') else None
    test_dir = os.getenv('TESTRAIL_TEST_DIR', 'tests')
    
    # Validate required parameters
    if not all([testrail_url, username, password, project_id]):
        logger.error("Missing required environment variables!")
        logger.error("Required: TESTRAIL_URL, TESTRAIL_USERNAME, TESTRAIL_PASSWORD, TESTRAIL_PROJECT_ID")
        logger.error("Optional: TESTRAIL_SUITE_ID (if not provided, will use first available suite)")
        return False
    
    logger.info(f"Starting TestRail sync for project {project_id}, suite {suite_id}")
    
    # Initialize API client
    api = TestRailAPI(testrail_url, username, password)
    
    # Verify project exists
    project = api.get_project(project_id)
    if not project:
        logger.error(f"Project {project_id} not found")
        return False
    
    logger.info(f"Syncing tests for project: {project['name']}")
    
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
    
    # Find and parse test files
    parser = TestParser()
    test_files = parser.find_test_files(test_dir)
    if not test_files:
        logger.warning(f"No test files found in {test_dir}")
        return False
    
    logger.info(f"Found {len(test_files)} test files")
    
    # Get existing sections
    existing_sections = api.get_sections(project_id, suite_id)
    logger.info(f"Found {len(existing_sections)} existing sections")
    section_map = {section['name']: section for section in existing_sections}
    
    success_count = 0
    
    for test_file in test_files:
        logger.info(f"Processing file: {test_file}")
        sections = parser.parse_test_file(test_file)
        
        for section in sections:
            logger.info(f"Processing section: {section.name} ({len(section.test_cases)} test cases)")
            
            # Create or get section
            if section.name in section_map:
                testrail_section = section_map[section.name]
                logger.info(f"Section '{section.name}' already exists")
            else:
                testrail_section = api.create_section(
                    project_id, 
                    suite_id, 
                    section.name,
                    f"Test section for {section.original_name} class"
                )
                if not testrail_section:
                    logger.error(f"Failed to create section: {section.name}")
                    continue
                logger.info(f"Created section: {section.name}")
                section_map[section.name] = testrail_section
            
            # Get existing cases in section
            existing_cases = api.get_cases(project_id, suite_id, testrail_section['id'])
            existing_case_titles = {case['title'] for case in existing_cases}
            
            # Create test cases
            for test_case in section.test_cases:
                if test_case.name in existing_case_titles:
                    logger.info(f"Test case '{test_case.name}' already exists")
                    continue
                
                description = f"Automated test case from {test_case.original_name} in {test_case.class_name}"
                created_case = api.create_case(
                    testrail_section['id'],
                    test_case.name,
                    description
                )
                if created_case:
                    logger.info(f"Created test case: {test_case.name}")
                    success_count += 1
                else:
                    logger.error(f"Failed to create test case: {test_case.name}")
    
    logger.info(f"Sync completed successfully! Created {success_count} test cases")
    return True

if __name__ == '__main__':
    success = sync_tests()
    exit(0 if success else 1)