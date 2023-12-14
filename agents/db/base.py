from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from server.config import env_settings

# engine = create_engine(env_settings.SQLALCHEMY_DATABASE_URI)

engine = create_engine(env_settings.SQLALCHEMY_DATABASE_URI_LOCAL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
