# from fastapi import APIRouter, HTTPException, Depends
# from db.Schema import UserCreate, UserResponse
# from .Service import create_user
# from api.Auth.okta_auth import verify_token

# router = APIRouter()

# @router.get("/auth/me", response_model=UserResponse)
# def get_authenticated_user(user = Depends(verify_token)):
#     return user

# @router.post("/users/create", response_model=UserResponse)
# def create_new_user(user: UserCreate):
#     try:
#         new_user, status = create_user(user)
#         if status == "existing":
#             raise HTTPException(status_code=400, detail="User already exists")
#         return new_user
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))