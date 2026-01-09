import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chat_with_mock_data():
    """Test chat functionality with pre-loaded data"""
    print("🧪 Testing Chatbot with Pre-loaded Data")
    print("=" * 60)
    
    # First, upload a meeting with mock summary
    print("\n1. Uploading meeting with mock data...")
    
    meeting_data = {
        "meeting_id": "TEST-MOCK-001",
        "title": "Mock Team Meeting",
        "participants": ["alice@test.com", "bob@test.com", "charlie@test.com"],
        "date": "2024-01-15T10:00:00",
        "duration_minutes": 60,
        "transcript": "This is a mock transcript for testing. The team discussed project progress, timelines, and next steps.",
        "summary": "Mock summary: The team discussed Q4 goals, assigned tasks, and set deadlines. Frontend work will be completed by Friday, backend by next Wednesday.",
        "key_points": ["Q4 Planning", "Task Assignment", "Deadline Setting"],
        "action_items": [
            {"task": "Complete frontend", "assignee": "Alice", "due_date": "2024-01-19"},
            {"task": "Fix backend bugs", "assignee": "Bob", "due_date": "2024-01-17"}
        ],
        "decisions": ["Use React", "Deploy to AWS", "Weekly meetings on Monday"],
        "tags": ["mock", "planning", "team"],
        "created_at": "2024-01-15T10:00:00",
        "updated_at": "2024-01-15T10:00:00"
    }
    
    # Insert directly into MongoDB (bypass API)
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["meeting_chatbot"]
        collection = db["meeting_summaries"]
        
        # Delete if exists
        collection.delete_one({"meeting_id": "TEST-MOCK-001"})
        
        # Insert mock data
        result = collection.insert_one(meeting_data)
        print(f"✅ Mock meeting inserted: {result.inserted_id}")
        
        # Now test chat with this meeting
        print("\n2. Testing chat with mock meeting...")
        
        test_questions = [
            "What are the action items?",
            "Who are the participants?",
            "What was discussed?",
            "What decisions were made?"
        ]
        
        for question in test_questions:
            print(f"\n   Q: {question}")
            
            chat_data = {
                "question": question,
                "meeting_id": "TEST-MOCK-001",
                "ai_provider": "openai"
            }
            
            response = requests.post(f"{BASE_URL}/chat/ask", json=chat_data)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', 'No answer')
                confidence = result.get('confidence', 0)
                
                # Truncate long answers
                if len(answer) > 150:
                    answer = answer[:150] + "..."
                
                print(f"   A: {answer}")
                print(f"   Confidence: {confidence:.2f}")
                
                # Check if answer contains useful info
                if confidence > 0.3:
                    print(f"   ✅ Good response")
                else:
                    print(f"   ⚠️  Low confidence response")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
        
        # Test without meeting ID (general question)
        print("\n3. Testing general chat...")
        chat_data = {
            "question": "What meetings do you have?",
            "ai_provider": "openai"
        }
        
        response = requests.post(f"{BASE_URL}/chat/ask", json=chat_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result.get('answer', 'No answer')[:100]}...")
        
        # Clean up
        collection.delete_one({"meeting_id": "TEST-MOCK-001"})
        print("\n✅ Mock data cleaned up")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_api_without_ai():
    """Test API functionality without AI dependencies"""
    print("\n🔧 Testing API Core Functions")
    print("=" * 60)
    
    endpoints = [
        ("GET", "/", "Root"),
        ("GET", "/health", "Health"),
        ("GET", "/chat/providers", "AI Providers"),
        ("GET", "/meetings?limit=1", "List Meetings"),
        ("GET", "/search?q=team", "Search"),
        ("GET", "/test", "Test")
    ]
    
    for method, endpoint, name in endpoints:
        print(f"\nTesting {name} ({method} {endpoint})...")
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code}")
                data = response.json()
                
                # Show relevant info
                if endpoint == "/health":
                    print(f"   📊 Database: {data.get('database', 'unknown')}")
                    print(f"   🤖 AI Providers: {data.get('ai_providers', [])}")
                elif endpoint == "/meetings":
                    meetings = data if isinstance(data, list) else []
                    print(f"   📋 Meetings found: {len(meetings)}")
                elif endpoint == "/search":
                    results = data.get('results', [])
                    print(f"   🔍 Search results: {len(results)}")
                else:
                    # Truncate long responses
                    response_str = str(data)[:100]
                    if len(str(data)) > 100:
                        response_str += "..."
                    print(f"   📦 Response: {response_str}")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                print(f"   📝 Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")

if __name__ == "__main__":
    print("🤖 Meeting Chatbot System Test")
    print("=" * 60)
    
    # Wait for server
    print("⏳ Checking server availability...")
    time.sleep(1)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            
            # Test core API
            test_api_without_ai()
            
            # Test with mock data
            test_chat_with_mock_data()
            
            print("\n" + "=" * 60)
            print("🎉 All tests completed!")
            print("\n📋 Next steps:")
            print("1. Add OpenAI API key to .env file for real AI responses")
            print("2. Add Gemini API key for alternative AI provider")
            print("3. Upload real meeting transcripts")
            print("4. Use the web interface at frontend.html")
            
        else:
            print(f"❌ Server returned status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running with: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {e}")