from sqlmodel import create_engine, Session
from sqlalchemy.sql.expression import func, alias
import os

script_dir = os.path.dirname(__file__)
abs_file_path = os.path.join(script_dir, "db/")

engine = create_engine(
    f"sqlite:///{abs_file_path}/expenses.db",
    connect_args={"check_same_thread": False},
    echo=False
)


def get_session():
    with Session(engine) as session:
        yield session


def get_count(session, query):
    aliased_query = alias(query)
    return session.query(func.count('*')).select_from(aliased_query).scalar()

