#!/usr/bin/env python3
"""
Test script for the comprehensive agentic automation system
"""

import requests
import json

# Test the agentic command endpoint
def test_agentic_command(command, expected_tools=None):
    url = "http://localhost:5000/api/agentic-command"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"  # This will be ignored for testing
    }
    
    data = {"command": command}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        
        print(f"\n🔍 Testing: '{command}'")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if expected_tools:
            actual_tools = [r.get('tool') for r in result.get('results', [])]
            print(f"Expected tools: {expected_tools}")
            print(f"Actual tools: {actual_tools}")
            
        return result
    except Exception as e:
        print(f"❌ Error testing '{command}': {e}")
        return None

def main():
    print("🚀 Testing Comprehensive Agentic Automation System")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "command": "help",
            "expected_tools": ["help"]
        },
        {
            "command": "sign up with random details and search for article 370",
            "expected_tools": ["signup_with_random", "search"]
        },
        {
            "command": "change my theme to dark and update my bio to 'Legal expert'",
            "expected_tools": ["update_theme", "update_profile_field"]
        },
        {
            "command": "open profile and change my name to John Doe",
            "expected_tools": ["open_profile", "update_profile_field"]
        },
        {
            "command": "view my query history",
            "expected_tools": ["view_query_history"]
        },
        {
            "command": "search for section 498A of IPC",
            "expected_tools": ["search"]
        }
    ]
    
    for test_case in test_cases:
        test_agentic_command(test_case["command"], test_case["expected_tools"])
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
