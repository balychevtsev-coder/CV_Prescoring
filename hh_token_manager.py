import os
import json
import time
import requests
from pathlib import Path

TOKEN_FILE = Path("token_store.json")
HH_TOKEN_URL = "https://hh.ru/oauth/token"


class HHTokenManager:
    def __init__(self):
        self.client_id = os.getenv("HH_CLIENT_ID")
        self.client_secret = os.getenv("HH_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise RuntimeError("HH_CLIENT_ID / HH_CLIENT_SECRET не заданы")

    # -------------------------
    # PUBLIC
    # -------------------------
    def get_access_token(self) -> str:
        token_data = self._load_token()

        if not token_data:
            raise RuntimeError("OAuth токен не инициализирован")

        if self._is_expired(token_data):
            token_data = self._refresh_token(token_data["refresh_token"])
            self._save_token(token_data)

        return token_data["access_token"]

    # -------------------------
    # PRIVATE
    # -------------------------
    def _is_expired(self, token_data: dict) -> bool:
        return time.time() >= token_data["expires_at"] - 60

    def _refresh_token(self, refresh_token: str) -> dict:
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post(HH_TOKEN_URL, data=payload, timeout=10)

        if response.status_code != 200:
            raise RuntimeError(
                f"Ошибка обновления OAuth токена: {response.text}"
            )

        data = response.json()
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": time.time() + data["expires_in"]
        }

    def _load_token(self) -> dict | None:
        if not TOKEN_FILE.exists():
            return None
        return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))

    def _save_token(self, token_data: dict):
        TOKEN_FILE.write_text(
            json.dumps(token_data, indent=2),
            encoding="utf-8"
        )