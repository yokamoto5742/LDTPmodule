from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from utils import config_manager


# 設定の読み込み
config = config_manager.load_config()
db_url = config.get('Database', 'db_url')

# SQLAlchemyの設定
_engine = None
_Session = None
_Base = None


def get_engine():
    """データベースエンジンを取得"""
    global _engine
    if _engine is None:
        _engine = create_engine(db_url, pool_pre_ping=True, pool_size=10)
    return _engine


def get_session_factory():
    """セッションファクトリを取得"""
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine())
    return _Session


def get_base():
    """ベースクラスを取得"""
    global _Base
    if _Base is None:
        _Base = declarative_base()
    return _Base


@contextmanager
def get_session():
    """セッション管理コンテキストマネージャ"""
    Session = get_session_factory()
    session = Session()
    try:
        yield session
    finally:
        session.close()
