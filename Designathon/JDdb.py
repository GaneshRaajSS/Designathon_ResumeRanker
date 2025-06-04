from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# DATABASE_URL = "mysql+pymysql://root:Hexaware123@localhost:3306/JD"
DATABASE_URL = "mysql+pymysql://root:Hexaware%40123@localhost:3306/JD"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
