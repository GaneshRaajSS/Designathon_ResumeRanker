# from sqlalchemy import Column, String, Text
# from JDdb import Base

# class ConsultantProfile(Base):
#     __tablename__ = "consultant_profiles"

#     id = Column(String(36), primary_key=True, index=True)
#     name = Column(String(100), nullable=False)
#     email = Column(String(100), nullable=False)
#     skills = Column(Text, nullable=False)
#     experience = Column(Text, nullable=False)
#     resume_text = Column(Text, nullable=True)
#     content_hash = Column(String(64), nullable=True)