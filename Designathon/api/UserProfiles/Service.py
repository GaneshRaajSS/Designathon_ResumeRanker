# from sqlalchemy.orm import Session
# from db.Model import User
# from db.Schema import UserCreate
# from sqlalchemy.exc import IntegrityError
# import uuid

# def get_user_by_email(db: Session, email: str):
#     return db.query(User).filter(User.email == email).first()

# def get_user_by_okta_id(db: Session, okta_id: str):
#     return db.query(User).filter(User.okta_id == okta_id).first()

# def create_user_if_not_exists(db: Session, payload: dict, admin_emails: list[str]):
#     email = payload.get("email")
#     name = payload.get("name", email.split("@")[0])
#     okta_id = payload.get("sub")

#     # First check by okta_id, then by email
#     user = get_user_by_okta_id(db, okta_id) if okta_id else None
#     if not user:
#         user = get_user_by_email(db, email)
    
#     if user:
#         # Update okta_id if it's missing
#         if not user.okta_id and okta_id:
#             user.okta_id = okta_id
#             db.commit()
#             db.refresh(user)
#         return user

#     role = "admin" if email in admin_emails else "user"
#     new_user = User(
#         user_id=str(uuid.uuid4()),
#         name=name,
#         email=email,
#         role=role,
#         okta_id=okta_id,
#     )
#     db.add(new_user)
#     try:
#         db.commit()
#     except IntegrityError:
#         db.rollback()
#         return get_user_by_email(db, email)
#     db.refresh(new_user)
#     return new_user

# def create_user(user_data: UserCreate):
#     # This function can be used for manual user creation if needed
#     from JDdb import SessionLocal
#     db = SessionLocal()
#     try:
#         existing_user = get_user_by_email(db, user_data.email)
#         if existing_user:
#             return existing_user, "existing"
        
#         new_user = User(
#             user_id=str(uuid.uuid4()),
#             name=user_data.name,
#             email=user_data.email,
#             role=user_data.role,
#             okta_id=user_data.okta_id,
#         )
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#         return new_user, "created"
#     finally:
#         db.close()