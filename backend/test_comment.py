"""Тестовый скрипт для проверки эндпоинта комментариев"""
import requests
import json

ticket_id = "e95faa1f-2487-40c4-ae11-0f46d21ad619"
url = f"http://localhost:8002/tickets/{ticket_id}/comments"
data = {
    "comment_text": "Test comment from Python script",
    "is_auto_reply": False
}

print(f"Testing POST {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("\n✅ SUCCESS! Comment endpoint works!")
    else:
        print(f"\n❌ FAILED with status {response.status_code}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")



