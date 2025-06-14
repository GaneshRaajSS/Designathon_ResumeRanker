# # api/job_descriptions/model.py
# from sqlalchemy import Column, String, Text
# from JDdb import Base

# class JobDescription(Base):
#     __tablename__ = "job_descriptions"

#     id = Column(String(36), primary_key=True, index=True)
#     title = Column(String(100), nullable=False)
#     description = Column(Text, nullable=False)
#     skills = Column(Text, nullable=False)
#     experience = Column(String(50), nullable=False)
