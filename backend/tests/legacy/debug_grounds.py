#!/usr/bin/env python3
"""
Debug the grounds endpoint response
"""

import requests
import json

# Configuration
BASE_URL = "https://criminal-appeals-au-2.preview.emergentagent.com/api"
TEST_EMAIL = "djkingy79@gmail.com"
import os
TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "change-me-local-only")
CASE_ID = "case_76056187ad4f"

def debug_grounds():
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Backend-Debug/1.0'
    })
    
    # Login first
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = session.post(f"{BASE_URL}/auth/login", json=login_data, timeout=15)
    if response.status_code == 200:
        data = response.json()
        if 'session_token' in data:
            auth_token = data['session_token']
            session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
            print("✅ Authenticated successfully")
        else:
            print("❌ No session token")
            return
    else:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    # Test grounds endpoint
    print(f"\nTesting: {BASE_URL}/cases/{CASE_ID}/grounds")
    response = session.get(f"{BASE_URL}/cases/{CASE_ID}/grounds", timeout=15)
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response Type: {type(data)}")
            print(f"Response Content: {json.dumps(data, indent=2)[:500]}...")
            
            if isinstance(data, list):
                print(f"✅ Response is a list with {len(data)} items")
            elif isinstance(data, dict):
                print(f"⚠️ Response is a dict with keys: {list(data.keys())}")
                if 'grounds' in data:
                    grounds = data['grounds']
                    print(f"   - 'grounds' key contains: {type(grounds)} with {len(grounds) if isinstance(grounds, list) else 'N/A'} items")
            else:
                print(f"❌ Response is neither list nor dict: {type(data)}")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Raw response: {response.text[:200]}...")
    else:
        print(f"❌ HTTP Error: {response.text[:200]}...")

if __name__ == "__main__":
    debug_grounds()