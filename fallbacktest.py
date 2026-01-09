import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_with_fallback_ai():
    """Test the system with fallback mock AI"""
    print("🤖 Testing System with Intelligent Fallback")
    print("=" * 60)
    
    # Check system status
    print("\n1. Checking system status...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"   ✅ Status: {health['status']}")
        print(f"   📊 Database: {health['database']}")
        print(f"   🤖 Available AI Providers: {health['ai_providers']}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
        return
    
    # Upload a meeting
    print("\n2. Uploading a meeting (will use mock AI if APIs unavailable)...")
    
    sample_transcript = """
    Project Kickoff Meeting
    Date: January 15, 2024
    Participants: Alice (Project Manager), Bob (Lead Developer), Charlie (UX Designer), Diana (QA Lead)
    
    Alice: Welcome everyone to our project kickoff. Let's start with objectives.
    Bob: Our main goal is to build a customer portal with user authentication and dashboard.
    Charlie: I've prepared wireframes for the main interface. We need feedback on the user flow.
    Diana: We should establish testing protocols early. I recommend unit tests for all modules.
    
    Decisions:
    1. Use React for frontend with TypeScript
    2. Node.js backend with Express
    3. MongoDB for database
    4. Deploy on AWS
    
    Action Items:
    - Charlie: Finalize designs by Wednesday
    - Bob: Set up project repository and CI/CD pipeline
    - Diana: Create test plan document
    - Alice: Schedule client demo for next Friday
    
    Timeline: 6 weeks for MVP
    """
    
    upload_data = {
        "transcript": sample_transcript,
        "title": "Project Kickoff - Customer Portal",
        "participants": ["alice@company.com", "bob@company.com", "charlie@company.com", "diana@company.com"],
        "duration_minutes": 60,
        "ai_provider": "openai"  # Will automatically fallback to mock if unavailable
    }
    
    response = requests.post(f"{BASE_URL}/meetings/upload", json=upload_data)
    if response.status_code == 200:
        meeting_info = response.json()
        meeting_id = meeting_info["meeting_id"]
        print(f"   ✅ Meeting uploaded successfully!")
        print(f"   📝 Meeting ID: {meeting_id}")
        print(f"   📋 Title: {meeting_info['data']['title']}")
        print(f"   📊 Summary: {meeting_info['data']['summary'][:100]}...")
    else:
        print(f"   ❌ Upload failed: {response.text}")
        return
    
    # Test chat with different providers
    print("\n3. Testing chat with different AI providers...")
    
    questions = [
        ("What are the action items?", "openai"),
        ("Who are the participants?", "gemini"),
        ("What technology stack was decided?", "mock"),
        ("What is the project timeline?", "openai")
    ]
    
    for question, provider in questions:
        print(f"\n   🤔 Q: {question}")
        print(f"   🛠️  Provider: {provider}")
        
        chat_data = {
            "question": question,
            "meeting_id": meeting_id,
            "ai_provider": provider
        }
        
        response = requests.post(f"{BASE_URL}/chat/ask", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            confidence = result.get('confidence', 0)
            used_provider = result.get('ai_provider', 'unknown')
            
            # Truncate long answers
            if len(answer) > 120:
                display_answer = answer[:120] + "..."
            else:
                display_answer = answer
            
            print(f"   💬 A: {display_answer}")
            print(f"   📊 Confidence: {confidence:.2f}")
            print(f"   ⚙️  Used Provider: {used_provider}")
            
            # Check answer quality
            if confidence > 0.5:
                print(f"   ✅ Good quality response")
            elif confidence > 0.2:
                print(f"   ⚠️  Moderate confidence")
            else:
                print(f"   ❌ Low confidence")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    # Test without meeting ID
    print("\n4. Testing general knowledge question...")
    chat_data = {
        "question": "What meetings do you have in the system?",
        "ai_provider": "mock"
    }
    
    response = requests.post(f"{BASE_URL}/chat/ask", json=chat_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   💬 Response: {result.get('answer', 'No answer')[:150]}...")
    
    # List meetings
    print("\n5. Listing all meetings...")
    response = requests.get(f"{BASE_URL}/meetings?limit=5")
    if response.status_code == 200:
        meetings = response.json()
        print(f"   📋 Total meetings in system: {len(meetings)}")
        for i, meeting in enumerate(meetings[-3:], 1):  # Show last 3
            print(f"   {i}. {meeting.get('title')} (ID: {meeting.get('meeting_id')})")
    
    print("\n" + "=" * 60)
    print("🎉 Test Completed Successfully!")
    print("\n💡 System is working with intelligent fallback:")
    print("   • If API keys are configured → Uses real AI")
    print("   • If APIs fail → Automatically uses mock AI")
    print("   • Always provides useful responses")

def check_ai_providers():
    """Check which AI providers are actually working"""
    print("\n🔍 Checking AI Provider Status")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/chat/providers")
    if response.status_code == 200:
        providers = response.json().get('available_providers', [])
        print(f"Available providers: {providers}")
        
        if 'openai' in providers or 'gemini' in providers:
            print("✅ Real AI providers available")
            print("💡 Add valid API keys to .env for better responses")
        else:
            print("⚠️  Only mock AI available")
            print("💡 Configure API keys in .env file:")
            print("   - Get OpenAI key: https://platform.openai.com/api-keys")
            print("   - Get Gemini key: https://makersuite.google.com/app/apikey")
    
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Meeting Chatbot System Test")
    print("=" * 60)
    
    # Wait for server
    print("⏳ Checking server...")
    time.sleep(1)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            check_ai_providers()
            test_with_fallback_ai()
        else:
            print(f"❌ Server error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Run: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {e}")