from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import configparser


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        db_url = config.get('Database', 'db_url')

        self.engine = create_engine(db_url, pool_pre_ping=True, pool_size=10)
        self.Session = sessionmaker(bind=self.engine)
        self._initialized = True

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def initialize_database(self, Base):
        """データベーススキーマの初期化"""
        Base.metadata.create_all(self.engine)
