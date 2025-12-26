import os
import time
import json
import requests

TOKEN_URL = "https://hh.ru/oauth/token"

data = {
    "grant_type": "authorization_code",
    "client_id": os.getenv("HH_CLIENT_ID"),
    "client_secret": os.getenv("HH_CLIENT_SECRET"),
    "code": "AUTH_CODE_ИЗ_BROWSER",
    "redirect_uri": "http://localhost:8501"
}

response = requests.post(TOKEN_URL, data=data)
response.raise_for_status()

token = response.json()

token_store = {
    "access_token": token["access_token"],
    "refresh_token": token["refresh_token"],
    "expires_at": time.time() + token["expires_in"]
}

with open("token_store.json", "w", encoding="utf-8") as f:
    json.dump(token_store, f, indent=2)

print("✅ OAuth токен сохранён")