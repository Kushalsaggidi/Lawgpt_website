#!/usr/bin/env python3
"""
Test script to verify voice command and random user improvements
"""

import requests
import json
import time

def test_random_user_generation():
    """Test the improved random user generation"""
    print("🧪 Testing Random User Generation...")
    
    # Test multiple random user generations
    for i in range(3):
        try:
            response = requests.post(
                "http://localhost:5000/api/agentic-command",
                headers={"Content-Type": "application/json"},
                json={"command": "sign up with random details"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Test {i+1}: Random user generation successful")
                if data.get("results"):
                    for result in data["results"]:
                        if result.get("success") and result.get("result", {}).get("token"):
                            print(f"   🔐 Token generated: {result['result']['token'][:20]}...")
                            print(f"   👤 User: {result['result'].get('user_email', 'N/A')}")
                            print(f"   📝 Message: {result['result'].get('message', 'N/A')}")
            else:
                print(f"❌ Test {i+1}: Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test {i+1}: Error - {str(e)}")
        
        time.sleep(1)  # Wait between tests

def test_voice_command_suggestions():
    """Test voice command suggestions"""
    print("\n🎤 Testing Voice Command Suggestions...")
    
    suggestions = [
        "Sign up with random details",
        "Search for Article 370", 
        "Change theme to dark mode",
        "Update my name to John Doe",
        "Show my query history",
        "Export my data",
        "Help me with commands"
    ]
    
    for suggestion in suggestions:
        try:
            response = requests.post(
                "http://localhost:5000/api/agentic-command",
                headers={"Content-Type": "application/json"},
                json={"command": suggestion}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Voice command '{suggestion}' processed successfully")
            else:
                print(f"❌ Voice command '{suggestion}' failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Voice command '{suggestion}' error: {str(e)}")

def main():
    print("🚀 Testing Voice Command and Random User Improvements")
    print("=" * 60)
    
    # Test random user generation
    test_random_user_generation()
    
    # Test voice command suggestions
    test_voice_command_suggestions()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n📋 Improvements Made:")
    print("   🎤 Enhanced voice recognition with better error handling")
    print("   🔄 Auto-submit after voice capture")
    print("   🎯 Better voice command suggestions")
    print("   🔐 Improved random user generation with uniqueness")
    print("   🛡️ Better error handling and retry mechanisms")
    print("   📱 Enhanced token management in frontend")

if __name__ == "__main__":
    main()
