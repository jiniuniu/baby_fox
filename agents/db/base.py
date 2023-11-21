from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from server.config import env_settings

SQLALCHEMY_DATABASE_URI = f"sqlite:///{env_settings.AGENT_DB_ROOT}/agent_config.db"


engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
