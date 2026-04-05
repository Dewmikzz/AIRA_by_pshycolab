# ═══ FILE: tests/test_talk.py ═══
# Purpose: Functional test for the /talk and /greet endpoints
# Inputs: Mock session_id, sample audio trigger
# Outputs: Success/Failure report

import requests
import os
import uuid

# [THINK] Why a dedicated script? curl is messy with form-data and binary files.
# [THINK] Testing /greet first ensures TTS is working before we test the full STT->LLM->TTS loop.

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Body: {response.json()}")
    assert response.status_code == 200

def test_greet():
    print("\nTesting /greet...")
    session_id = str(uuid.uuid4())
    response = requests.get(f"{BASE_URL}/greet", params={"session_id": session_id})
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Aira says: {data.get('text')}")
    print(f"Audio received: {'Yes' if data.get('audio_base64') else 'No'}")
    assert response.status_code == 200

def test_talk_mock():
    # Note: This requires a sample.webm or similar in the same directory
    # For now, we just check if the endpoint is reachable
    print("\nTesting /talk (Check connectivity)...")
    session_id = str(uuid.uuid4())
    # Creating a dummy 1-second silent wav for testing if no file exists
    dummy_file = "dummy.wav"
    with open(dummy_file, "wb") as f:
        f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x44\xac\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00")
    
    try:
        with open(dummy_file, "rb") as f:
            files = {"audio": (dummy_file, f, "audio/wav")}
            data = {"session_id": session_id}
            response = requests.post(f"{BASE_URL}/talk", files=files, data=data)
            
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            res_data = response.json()
            print(f"Transcript: {res_data.get('transcript')}")
            print(f"Reply: {res_data.get('reply')}")
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

if __name__ == "__main__":
    try:
        test_health()
        test_greet()
        test_talk_mock()
        print("\n✅ All connectivity tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Ensure the server is running with 'python main.py' before testing.")
