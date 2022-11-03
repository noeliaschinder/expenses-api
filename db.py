from sqlmodel import create_engine, Session
from sqlalchemy.sql.expression import func, alias

engine = create_engine(
    "sqlite:///db/expenses.db",
    connect_args={"check_same_thread": False},
    echo=True
)


def get_session():
    with Session(engine) as session:
        yield session


def get_count(session, query):
    aliased_query = alias(query)
    return session.query(func.count('*')).select_from(aliased_query).scalar()

