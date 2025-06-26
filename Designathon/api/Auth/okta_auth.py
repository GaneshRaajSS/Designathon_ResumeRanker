from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError
import os

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_role(roles: list[str]):
    def checker(user=Depends(get_current_user)):
        print("User from token:", user)              # Debug
        print("Allowed roles:", roles)               # Debug
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return checker
