import configparser
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

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


@contextmanager
def get_session():
    """
    データベースセッションを提供するコンテキストマネージャー

    使用例:
    ```
    with get_session() as session:
        # セッションを使った操作
        results = session.query(SomeModel).all()
    # ここでセッションは自動的にクローズされる
    ```

    Returns:
        SQLAlchemy Session: アクティブなデータベースセッション
    """
    session = Session()
    try:
        yield session
    finally:
        session.close()


def initialize_database():
    """
    データベースの初期化を行う

    注意: このメソッドを呼び出す前に必ずBase.metadata.create_all(engine)が
    別の場所で呼び出されていることを確認してください。
    """
    # テーブル作成はmodels/base.pyのBase.metadata.create_all(engine)で行われるため、
    # 必要に応じてここに追加の初期化ロジックを実装
    pass


def check_connection():
    """
    データベース接続が利用可能かをチェックする

    Returns:
        bool: 接続が成功した場合はTrue、失敗した場合はFalse
    """
    try:
        with get_session() as session:
            session.execute("SELECT 1")
        return True
    except Exception:
        return False
