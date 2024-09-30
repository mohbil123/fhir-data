import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Retrieve database URL from environment variables, with a default for local development
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://fhiruser:fhirpassword@localhost:3306/fhir_data")

def get_db_engine():
    try:
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        print(f"Error creating engine: {e}")
        raise

def get_session(engine):
    try:
        session = sessionmaker(bind=engine)
        return session()
    except Exception as e:
        print(f"Error creating session: {e}")
        raise

def get_metadata():
    return MetaData()
