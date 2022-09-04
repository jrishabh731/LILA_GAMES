import os
import logging
import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD", "root")
database = os.getenv("POSTGRES_DB", "test_db")
port = os.getenv("DB_PORT", 5432)
db_host = os.getenv("DB_HOST", "localhost")
log = logging.getLogger("API_LOG")


def initialize_engine(database="postgres"):
    while True:
        try:
            return create_engine(
                f"postgresql://{db_user}:{db_password}@{db_host}:{port}/{database}"
            )

        except Exception as err:
            log.error(f"Exception occured while connecting to db: {err}")
        time.sleep(10)


def create_database():
    """
    Creating database if the given database doesn't exist.
    :return:
    """
    default_engine = initialize_engine()
    conn = default_engine.connect()
    conn.execute("commit")
    try:
        conn.execute(f"create database {database}")
    except Exception as err:
        print(err)
    conn.close()


create_database()

engine = initialize_engine(database)

Base = declarative_base()

