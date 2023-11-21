if __name__ == "__main__":
    from agents.db.base import Base, engine
    from agents.db.data_model import *

    Base.metadata.create_all(bind=engine)
