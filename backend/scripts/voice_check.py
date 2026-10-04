import uuid, requests, os
API = os.environ.get("TAXSHIELD_TEST_API", "http://127.0.0.1:8000") + "/api"
def reg(p):
    e = f"{p}-{uuid.uuid4().hex[:6]}@example.com"
    r = requests.post(API + "/register", json={"email": e, "name": p, "password": "Pass1234!"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
H = reg("voice")
print("transcribe ->", requests.post(API + "/chat/voice/transcribe", json={"transcript": "hello tax", "lang": "en-IN"}, headers=H).status_code)
print("synthesize ->", requests.post(API + "/chat/voice/synthesize", json={"text": "namaste"}, headers=H).status_code)
print("empty transcript ->", requests.post(API + "/chat/voice/transcribe", json={"transcript": ""}, headers=H).status_code)
