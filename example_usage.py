import asyncio
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_api():
    # 1. Upload a meeting
    print("1. Uploading meeting transcript...")
    
    transcript = """
    Meeting: Project Kickoff
    Date: 2023-12-01
    Participants: John, Jane, Bob, Alice
    
    John: Welcome everyone to our project kickoff. Today we'll discuss the scope and timeline.
    Jane: I've prepared the requirements document. The main features are A, B, and C.
    Bob: For timeline, I think we need 3 months for development and 1 month for testing.
    Alice: We should also consider the budget constraints.
    John: Agreed. Let's set milestones for each month.
    Decision: Project will start on Jan 1, 2024 with monthly milestones.
    Action Items:
    - Jane to finalize requirements by Dec 15
    - Bob to prepare project plan by Dec 20
    """
    
    response = requests.post(
        f"{BASE_URL}/meetings/upload",
        data={
            "transcript": transcript,
            "title": "Project Kickoff Meeting",
            "participants": json.dumps(["john@company.com", "jane@company.com", "bob@company.com", "alice@company.com"]),
            "duration_minutes": "60",
            "ai_provider": "openai"
        }
    )
    
    if response.status_code == 200:
        meeting_data = response.json()
        meeting_id = meeting_data["data"]["meeting_id"]
        print(f"Meeting uploaded successfully. ID: {meeting_id}")
    else:
        print(f"Upload failed: {response.text}")
        return
    
    # 2. Ask questions about the meeting
    print("\n2. Asking questions about the meeting...")
    
    questions = [
        "What was decided in the meeting?",
        "What are the action items?",
        "Who are the participants?",
        "What is the project timeline?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        
        query_data = {
            "question": question,
            "meeting_id": meeting_id,
            "ai_provider": "openai"
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/ask",
            json=query_data
        )
        
        if response.status_code == 200:
            answer_data = response.json()
            print(f"Answer: {answer_data['answer']}")
            print(f"Confidence: {answer_data['confidence']}")
        else:
            print(f"Error: {response.text}")
    
    # 3. Test with Gemini
    print("\n3. Testing with Gemini...")
    
    query_data = {
        "question": "What are the key points discussed?",
        "meeting_id": meeting_id,
        "ai_provider": "gemini"
    }
    
    response = requests.post(
        f"{BASE_URL}/chat/ask",
        json=query_data
    )
    
    if response.status_code == 200:
        answer_data = response.json()
        print(f"Answer (Gemini): {answer_data['answer']}")
        print(f"AI Provider used: {answer_data['ai_provider']}")
    else:
        print(f"Gemini test failed: {response.text}")

if __name__ == "__main__":
    test_api()