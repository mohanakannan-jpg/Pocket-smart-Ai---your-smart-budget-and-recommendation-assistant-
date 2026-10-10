import base64, hashlib, hmac, json, os, secrets, time
from fastapi import HTTPException, status

SECRET = os.getenv("JWT_SECRET", "development-only-change-me")
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return base64.b64encode(salt+digest).decode()
def verify_password(password: str, stored: str) -> bool:
    raw = base64.b64decode(stored); salt, digest = raw[:16], raw[16:]
    candidate = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return hmac.compare_digest(digest, candidate)
def issue_token(user_id: int) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"sub":user_id,"exp":int(time.time())+60*60*24}).encode()).rstrip(b"=")
    sig = hmac.new(SECRET.encode(), payload, hashlib.sha256).digest()
    return (payload+b"."+base64.urlsafe_b64encode(sig).rstrip(b"=")).decode()
def verify_token(token: str) -> int:
    try:
        raw, signature = token.encode().split(b".")
        expected = hmac.new(SECRET.encode(), raw, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, base64.urlsafe_b64decode(signature+b"="*((4-len(signature)%4)%4))): raise ValueError()
        data = json.loads(base64.urlsafe_b64decode(raw+b"="*((4-len(raw)%4)%4)))
        if data["exp"] < time.time(): raise ValueError()
        return int(data["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
