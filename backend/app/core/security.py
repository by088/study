from datetime import datetime
import hashlib
from typing import Optional


def hash_password(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def verify_password(raw: str, hashed: str) -> bool:
    return hash_password(raw) == hashed


def issue_token(user_id: str) -> str:
    # lightweight token for lab use: user_id + timestamp hash
    stamp = datetime.utcnow().isoformat()
    digest = hashlib.md5(f"{user_id}:{stamp}".encode("utf-8")).hexdigest()[:8]
    return f"token-{user_id}-{digest}"


def parse_token(token: str) -> Optional[str]:
    if not token.startswith("token-"):
        return None
    parts = token.split("-")
    if len(parts) < 3:
        return None
    return parts[1]
