from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'local_data'
USERS_FILE = DATA_DIR / 'users.json'


class LocalAuthStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = path or USERS_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(
                {
                    'users': {
                        'demo': {
                            'password': 'demo',
                            'bankroll': 1000.0,
                        }
                    }
                }
            )

    def _read(self) -> Dict:
        try:
            with self.path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'users': {}}

    def _write(self, payload: Dict) -> None:
        with self.path.open('w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)

    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        data = self._read()
        user = data.get('users', {}).get(username)
        if not user or user.get('password') != password:
            return None
        return {
            'username': username,
            'bankroll': float(user.get('bankroll', 1000.0)),
        }

    def register_user(self, username: str, password: str, starting_bankroll: float = 1000.0) -> Dict:
        username = username.strip()
        if not username:
            raise ValueError('Username is required.')
        if len(password) < 3:
            raise ValueError('Password must be at least 3 characters.')

        data = self._read()
        users = data.setdefault('users', {})
        if username in users:
            raise ValueError('That username already exists.')

        users[username] = {
            'password': password,
            'bankroll': float(starting_bankroll),
        }
        self._write(data)
        return {
            'username': username,
            'bankroll': float(starting_bankroll),
        }

    def save_bankroll(self, username: str, bankroll: float) -> None:
        data = self._read()
        user = data.setdefault('users', {}).setdefault(username, {})
        user['bankroll'] = float(bankroll)
        self._write(data)
