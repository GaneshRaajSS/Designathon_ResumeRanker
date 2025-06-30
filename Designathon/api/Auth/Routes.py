# auth/routes.py
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from jose import jwt, JWTError
from urllib.parse import urlencode
from db.Model import User
from JDdb import SessionLocal
from .okta_auth import get_current_user
import os, httpx, secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv
from enums import UserRoleStatus
load_dotenv()


router = APIRouter()

CLIENT_ID = os.getenv("OKTA_CLIENT_ID")
CLIENT_SECRET = os.getenv("OKTA_CLIENT_SECRET")
ISSUER = os.getenv("OKTA_ISSUER")
REDIRECT_URI = os.getenv("OKTA_REDIRECT_URI")
AUTH_ENDPOINT = f"{ISSUER}/v1/authorize"
TOKEN_ENDPOINT = f"{ISSUER}/v1/token"
JWKS_URI = f"{ISSUER}/v1/keys"
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")

STATE_STORE = {}

@router.get("/login")
def login():
    state = secrets.token_urlsafe(16)
    STATE_STORE[state] = True
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "openid profile email",
        "redirect_uri": REDIRECT_URI,
        "state": state,
    }
    return RedirectResponse(url=f"{AUTH_ENDPOINT}?{urlencode(params)}")

@router.get("/logout")
def logout():
    response = RedirectResponse("/")
    response.delete_cookie("access_token")
    return response

@router.get("/callback")
async def callback(code: str, state: str):
    if state not in STATE_STORE:
        raise HTTPException(status_code=400, detail="Invalid state")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            TOKEN_ENDPOINT,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        token_data = token_response.json()
        if "id_token" not in token_data:
            raise HTTPException(status_code=400, detail="Token exchange failed")

        id_token = token_data["id_token"]
        jwks_response = await client.get(JWKS_URI)
        jwks_data = jwks_response.json()
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        key = next((k for k in jwks_data["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Key not found in JWKS")

        try:
            payload = jwt.decode(
                id_token,
                key,
                algorithms=["RS256"],
                audience=CLIENT_ID,
                issuer=ISSUER,
                options={"verify_at_hash": False},
            )
        except JWTError as e:
            print("JWT verification failed:", str(e))
            raise HTTPException(status_code=401, detail="Invalid token")

        email = payload.get("email")
        name = payload.get("name", "Unknown")

        # 🔑 Pull role from token claim (mapped from Okta's userRole)
        role_str = payload.get("userRole", "User")
        role = UserRoleStatus(role_str)
        print("role",role)
        try:
            role = UserRoleStatus(role_str)
        except ValueError:
            role = UserRoleStatus.User

        db = SessionLocal()
        user = db.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email, name=name, role=role)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Optional: sync role from Okta
            if user.role != role:
                user.role = role
                db.commit()

        token_payload = {
            "sub": email,
            "role": str(user.role),
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        print("Token payload:", token_payload)
        access_token = jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

        redirect_path = {
            UserRoleStatus.ARRequestor: "/arrequestor",
            UserRoleStatus.Recruiter: "/recruiter",
            UserRoleStatus.User: "/dashboard"
        }.get(user.role, "/dashboard")

        response = RedirectResponse(f"{frontend_url}{redirect_path}")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=3600
        )
        return response

@router.get("/docs", include_in_schema=False)
async def protected_docs(request: Request):
    try:
        await get_current_user(request)
        return get_swagger_ui_html(openapi_url="/openapi.json", title="AI Recruitment Matching System")
    except HTTPException:
        return RedirectResponse("/login")

@router.get("/redoc", include_in_schema=False)
async def protected_redoc(request: Request):
    try:
        await get_current_user(request)
        return get_redoc_html(openapi_url="/openapi.json", title="Redoc")
    except HTTPException:
        return RedirectResponse("/login")


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    db = SessionLocal()
    db_user = db.query(User).filter_by(email=user["sub"]).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "email": db_user.email,
        "role": db_user.role,
        "name": db_user.name
    }

