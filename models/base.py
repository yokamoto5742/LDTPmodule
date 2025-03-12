from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import configparser
import os
import sys

# 設定ファイルの読み込み
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# 実行ファイルかどうかを確認し本番環境（実行形式ファイル）の場合はディレクトリを変更
if getattr(sys, 'frozen', False):
    app_directory = r"C:\Shinseikai\LDTPapp"
    os.chdir(app_directory)

# データベース接続設定
db_url = config.get('Database', 'db_url')
engine = create_engine(db_url, pool_pre_ping=True, pool_size=10)
Session = sessionmaker(bind=engine)

# SQLAlchemyのベースクラス
Base = declarative_base()

@contextmanager
def get_session():
    """データベースセッションを提供するコンテキストマネージャー"""
    session = Session()
    try:
        yield session
    finally:
        session.close()

def init_database():
    """データベーステーブルの初期化"""
    Base.metadata.create_all(engine)
