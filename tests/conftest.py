import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


@pytest.fixture(scope='function')
def test_db():
    """テスト用のインメモリSQLiteデータベース"""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope='function')
def test_engine():
    """テスト用のエンジン"""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope='function')
def test_session_factory(test_engine):
    """テスト用のセッションファクトリ"""
    return sessionmaker(bind=test_engine)
