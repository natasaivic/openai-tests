#!/usr/bin/env python3

import requests
import json
from urllib.parse import urljoin
import sys
import os
from dotenv import load_dotenv

class TestRailConnectivityTest:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def test_connection(self):
        """Test basic connectivity to TestRail"""
        try:
            url = urljoin(self.base_url, '/index.php?/api/v2/get_projects')
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                print("✓ Successfully connected to TestRail")
                projects = response.json()
                print(f"✓ Found {len(projects)} projects")
                return True
            elif response.status_code == 401:
                print("✗ Authentication failed - check username/password")
                return False
            else:
                print(f"✗ Connection failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("✗ Connection error - check TestRail URL")
            return False
        except requests.exceptions.Timeout:
            print("✗ Connection timeout")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {str(e)}")
            return False

    def get_user_info(self):
        """Get current user information"""
        try:
            url = urljoin(self.base_url, '/index.php?/api/v2/get_user_by_email')
            params = {'email': self.username}
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✓ Authenticated as: {user_info.get('name', 'Unknown')}")
                return True
            else:
                print(f"✗ Could not retrieve user info: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error getting user info: {str(e)}")
            return False

def main():
    """Main function to run connectivity tests"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get TestRail credentials from environment variables
    base_url = os.getenv('TESTRAIL_URL')
    username = os.getenv('TESTRAIL_USERNAME') 
    password = os.getenv('TESTRAIL_PASSWORD')
    
    if not all([base_url, username, password]):
        print("Please set the following environment variables:")
        print("- TESTRAIL_URL (e.g., https://yourcompany.testrail.io)")
        print("- TESTRAIL_USERNAME")
        print("- TESTRAIL_PASSWORD")
        sys.exit(1)
    
    print("Testing TestRail connectivity...")
    print(f"URL: {base_url}")
    print(f"Username: {username}")
    print("-" * 50)
    
    tester = TestRailConnectivityTest(base_url, username, password)
    
    # Run connectivity tests
    connection_ok = tester.test_connection()
    if connection_ok:
        tester.get_user_info()
        print("\n✓ All connectivity tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Connectivity tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()