"""Quick API test script - run after server is up."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_upload(csv_path: str):
    """Test file upload."""
    print("\n2. Testing upload endpoint...")
    with open(csv_path, 'rb') as f:
        files = {'file': (csv_path, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        return data['session_id']
    return None

def test_explore(session_id: str):
    """Test exploration endpoint."""
    print(f"\n3. Testing explore endpoint for session {session_id}...")
    response = requests.post(f"{BASE_URL}/api/explore/{session_id}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Data DNA generated with {len(data['data_dna']['columns'])} columns")
    print(f"Suggested queries: {data['data_dna']['suggested_queries']}")
    return response.status_code == 200

def test_get_session(session_id: str):
    """Test get session endpoint."""
    print(f"\n4. Testing get session endpoint...")
    response = requests.get(f"{BASE_URL}/api/session/{session_id}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Session status: {data['status']}")
    print(f"Row count: {data['row_count']}")
    return response.status_code == 200

def test_create_chat(session_id: str):
    """Test create chat endpoint."""
    print(f"\n5. Testing create chat endpoint...")
    payload = {
        "session_id": session_id,
        "title": "Test Chat"
    }
    response = requests.post(f"{BASE_URL}/api/chats", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Chat created: {data['id']}")
    
    if response.status_code == 200:
        return data['id']
    return None

def test_create_message(chat_id: str):
    """Test create message endpoint."""
    print(f"\n6. Testing create message endpoint...")
    payload = {
        "chat_id": chat_id,
        "role": "user",
        "content": "What are the key insights?"
    }
    response = requests.post(f"{BASE_URL}/api/messages", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Message created: {data['id']}")
    return response.status_code == 200

def test_chat_stream(chat_id: str, session_id: str):
    """Test chat stream endpoint."""
    print(f"\n7. Testing chat stream endpoint...")
    payload = {
        "chat_id": chat_id,
        "session_id": session_id,
        "message": "Show me the top 5 rows",
        "history": []
    }
    response = requests.post(f"{BASE_URL}/api/chat/stream", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Assistant response: {data['content']}")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("InsightX Backend API Test")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed. Is the server running?")
        exit(1)
    
    print("\n✅ Health check passed!")
    print("\nTo test upload, run:")
    print("  python test_api.py <path-to-csv-file>")
    print("\nExample:")
    print("  python test_api.py sample_data.csv")
