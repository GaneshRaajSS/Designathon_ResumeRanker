# import os
# import json
# from fastapi import Depends, HTTPException
# from fastapi.security import OAuth2AuthorizationCodeBearer
# from jose import jwt, JWTError, jwk
# from urllib.request import urlopen
# from sqlalchemy.orm import Session
# from dotenv import load_dotenv

# from JDdb import get_db  # Your DB Session provider
# from api.UserProfiles.Service import create_user_if_not_exists

# load_dotenv()

# OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
# OKTA_CLIENT_ID = os.getenv("OKTA_CLIENT_ID")
# OKTA_ISSUER = os.getenv("OKTA_ISSUER")
# JWKS_URL = f"{OKTA_ISSUER}/v1/keys"
# ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "").split(",")

# oauth2_scheme = OAuth2AuthorizationCodeBearer(
#     authorizationUrl=f"{OKTA_ISSUER}/v1/authorize",
#     tokenUrl=f"{OKTA_ISSUER}/v1/token"
# )

# with urlopen(JWKS_URL) as resp:
#     jwks = json.loads(resp.read())

# def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     try:
#         unverified_header = jwt.get_unverified_header(token)
#         kid = unverified_header.get("kid")
#         if not kid:
#             raise HTTPException(status_code=401, detail="Missing kid")

#         raw_key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
#         if not raw_key:
#             raise HTTPException(status_code=401, detail="Key not found in JWKS")

#         key = jwk.construct(raw_key)
#         payload = jwt.decode(
#             token,
#             key,
#             algorithms=["RS256"],
#             audience=OKTA_CLIENT_ID,
#             issuer=OKTA_ISSUER,
#         )

#         user = create_user_if_not_exists(db, payload, admin_emails=ADMIN_EMAILS)
#         return user
#     except JWTError as e:
#         raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
