from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#SQL_ALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip_address/hostname>/<database_name>'
# you have to distinguish psycopg(3) as below otherwise for sqlalchemy psycopg2 is the default.
SQL_ALCHEMY_DATABASE_URL = 'postgresql+psycopg://postgres:Com1par@localhost/fastapi'

engine = create_engine(SQL_ALCHEMY_DATABASE_URL, echo=True )

SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
