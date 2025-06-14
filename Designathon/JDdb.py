from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# DATABASE_URL = "mysql+pymysql://root:Hexaware%40123@localhost:3306/JD"
DATABASE_URL = os.getenv("DATABASE_URL")
print("loaded", os.getenv("DATABASE_URL"))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
