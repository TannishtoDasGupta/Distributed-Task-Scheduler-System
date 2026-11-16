"""PostgreSQL integration test; CI supplies a disposable database service."""
import uuid
import pytest
from sqlalchemy.orm import sessionmaker
from app.database import Base, engine
from app.models import Task

@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

def test_task_can_be_persisted_and_read_back(db_session):
    task_id = str(uuid.uuid4())
    db_session.add(Task(task_id=task_id, type="echo", status="PENDING", payload='{"message": "integration"}'))
    db_session.flush()
    stored = db_session.query(Task).filter(Task.task_id == task_id).one()
    assert stored.type == "echo"
    assert stored.status == "PENDING"
    assert stored.payload == '{"message": "integration"}'
