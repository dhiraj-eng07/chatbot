import sys
import time

# Try to import requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("⚠️  'requests' module not found. Installing it now...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests
    REQUESTS_AVAILABLE = True

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test an API endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.headers.get('content-type') == 'application/json' else response.text
        }
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to {url}. Make sure the server is running."}
    except Exception as e:
        return {"error": str(e)}

def test_all_endpoints():
    print("🚀 Testing Meeting Chatbot API")
    print("=" * 60)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    test_results = []
    
    # 1. Test root endpoint
    print("\n1️⃣  Testing root endpoint...")
    result = test_endpoint("/")
    if "error" in result:
        print(f"   ❌ Failed: {result['error']}")
    else:
        print(f"   ✅ Status: {result['status']}")
        print(f"   📦 Response: {result['data']}")
    test_results.append(("Root endpoint", result.get("success", False)))
    
    # 2. Test health endpoint
    print("\n2️⃣  Testing health endpoint...")
    result = test_endpoint("/health")
    if "error" in result:
        print(f"   ❌ Failed: {result['error']}")
    else:
        print(f"   ✅ Status: {result['status']}")
        print(f"   🩺 Health: {result['data']}")
    test_results.append(("Health endpoint", result.get("success", False)))
    
    # 3. Test AI providers
    print("\n3️⃣  Testing AI providers endpoint...")
    result = test_endpoint("/chat/providers")
    if "error" in result:
        print(f"   ❌ Failed: {result['error']}")
    else:
        print(f"   ✅ Status: {result['status']}")
        print(f"   🤖 AI Providers: {result['data']}")
    test_results.append(("AI providers", result.get("success", False)))
    
    # 4. Test chat without any meetings
    print("\n4️⃣  Testing chat endpoint (no meetings)...")
    chat_data = {
        "question": "What meetings do you have?",
        "ai_provider": "openai"
    }
    result = test_endpoint("/chat/ask", "POST", chat_data)
    if "error" in result:
        print(f"   ❌ Failed: {result['error']}")
    else:
        print(f"   ✅ Status: {result['status']}")
        print(f"   💬 Chat Response: {result['data']}")
    test_results.append(("Chat endpoint", result.get("success", False)))
    
    # 5. Upload a sample meeting
    print("\n5️⃣  Uploading a sample meeting...")
    sample_transcript = """
    Team Meeting - January 15, 2024
    Participants: John, Sarah, Mike, Emily
    
    John: Welcome everyone. Let's start with project updates.
    Sarah: The frontend is 80% complete. We're on track for Friday delivery.
    Mike: Backend API is ready. Need to integrate with authentication.
    Emily: Design system is finalized. Assets are ready for development.
    
    Decisions:
    1. Use React for frontend
    2. Deploy to AWS
    3. Weekly standups on Monday 10 AM
    
    Action Items:
    - Sarah: Complete frontend by Friday
    - Mike: Integrate auth by Wednesday
    - Emily: Share design assets by tomorrow
    """
    
    upload_data = {
        "transcript": sample_transcript,
        "title": "Weekly Project Sync",
        "participants": ["john@company.com", "sarah@company.com", "mike@company.com", "emily@company.com"],
        "duration_minutes": 30,
        "ai_provider": "openai"
    }
    
    result = test_endpoint("/meetings/upload", "POST", upload_data)
    if "error" in result:
        print(f"   ❌ Failed: {result['error']}")
        meeting_id = None
    else:
        if result.get("success"):
            meeting_info = result["data"]
            meeting_id = meeting_info.get("meeting_id")
            print(f"   ✅ Meeting uploaded successfully!")
            print(f"   📝 Meeting ID: {meeting_id}")
            print(f"   📋 Title: {meeting_info.get('data', {}).get('title', 'Unknown')}")
        else:
            print(f"   ⚠️  Upload may have issues: {result['data']}")
            meeting_id = "TEST-MEETING-001"  # Fallback for testing
    
    test_results.append(("Meeting upload", result.get("success", False)))
    
    # 6. Test chat with meeting
    if meeting_id:
        print("\n6️⃣  Testing chat with specific meeting...")
        chat_data = {
            "question": "What are the action items?",
            "meeting_id": meeting_id,
            "ai_provider": "openai"
        }
        result = test_endpoint("/chat/ask", "POST", chat_data)
        if "error" in result:
            print(f"   ❌ Failed: {result['error']}")
        else:
            print(f"   ✅ Status: {result['status']}")
            response_data = result["data"]
            if isinstance(response_data, dict):
                print(f"   💬 Answer: {response_data.get('answer', 'No answer')[:100]}...")
                print(f"   📊 Confidence: {response_data.get('confidence', 0)}")
            else:
                print(f"   📦 Response: {response_data}")
        test_results.append(("Chat with meeting", result.get("success", False)))
    
    # 7. List meetings
    print("\n7️⃣  Listing all meetings...")
    result = test_endpoint("/meetings?limit=5")
    if "error" in result:
        print(f"   ❌ Failed: {result['error']}")
    else:
        print(f"   ✅ Status: {result['status']}")
        meetings = result["data"]
        if isinstance(meetings, list):
            print(f"   📊 Found {len(meetings)} meetings")
            for i, meeting in enumerate(meetings[:3], 1):
                if isinstance(meeting, dict):
                    print(f"   {i}. {meeting.get('title', 'Untitled')} (ID: {meeting.get('meeting_id', 'N/A')})")
        else:
            print(f"   📦 Response: {meetings}")
    test_results.append(("List meetings", result.get("success", False)))
    
    # 8. Test search
    print("\n8️⃣  Testing search endpoint...")
    result = test_endpoint("/search?q=team&limit=3")
    if "error" in result:
        print(f"   ❌ Failed: {result['error']}")
    else:
        print(f"   ✅ Status: {result['status']}")
        search_data = result["data"]
        if isinstance(search_data, dict):
            print(f"   🔍 Search results: {len(search_data.get('results', []))} found")
        else:
            print(f"   📦 Response: {search_data}")
    test_results.append(("Search endpoint", result.get("success", False)))
    
    # 9. Test test endpoint
    print("\n9️⃣  Testing test endpoint...")
    result = test_endpoint("/test")
    if "error" in result:
        print(f"   ❌ Failed: {result['error']}")
    else:
        print(f"   ✅ Status: {result['status']}")
        print(f"   🧪 Test: {result['data']}")
    test_results.append(("Test endpoint", result.get("success", False)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Your API is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = test_all_endpoints()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)