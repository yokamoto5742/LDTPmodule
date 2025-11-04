from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from database import connection


class TestGetEngine:
    """get_engine関数のテストクラス"""

    def setup_method(self):
        """各テストメソッドの前にグローバル変数をリセット"""
        connection._engine = None
        connection._Session = None
        connection._Base = None

    def test_get_engine_creates_engine(self):
        """正常系: エンジンが作成される"""
        engine = connection.get_engine()
        assert engine is not None
        assert hasattr(engine, 'connect')

    def test_get_engine_singleton_pattern(self):
        """正常系: シングルトンパターン - 同じインスタンスが返される"""
        engine1 = connection.get_engine()
        engine2 = connection.get_engine()
        assert engine1 is engine2

    def test_get_engine_called_multiple_times(self):
        """正常系: 複数回呼び出しても同じエンジンが返される"""
        engines = [connection.get_engine() for _ in range(5)]
        assert all(engine is engines[0] for engine in engines)

    @patch('database.connection.create_engine')
    def test_get_engine_creates_with_pool_settings(self, mock_create_engine):
        """正常系: プールオプション付きでエンジンが作成される"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        connection.get_engine()

        # create_engineが適切なパラメータで呼ばれることを確認
        mock_create_engine.assert_called_once()
        call_kwargs = mock_create_engine.call_args[1]
        assert call_kwargs.get('pool_pre_ping') is True
        assert call_kwargs.get('pool_size') == 10

    def test_get_engine_returns_sqlalchemy_engine(self):
        """正常系: SQLAlchemyエンジンインスタンスが返される"""
        engine = connection.get_engine()
        # SQLAlchemyエンジンの基本的なメソッドが存在することを確認
        assert hasattr(engine, 'connect')
        assert hasattr(engine, 'dispose')
        assert hasattr(engine, 'url')


class TestGetSessionFactory:
    """get_session_factory関数のテストクラス"""

    def setup_method(self):
        """各テストメソッドの前にグローバル変数をリセット"""
        connection._engine = None
        connection._Session = None
        connection._Base = None

    def test_get_session_factory_creates_session_factory(self):
        """正常系: セッションファクトリが作成される"""
        session_factory = connection.get_session_factory()
        assert session_factory is not None
        assert callable(session_factory)

    def test_get_session_factory_singleton_pattern(self):
        """正常系: シングルトンパターン - 同じインスタンスが返される"""
        factory1 = connection.get_session_factory()
        factory2 = connection.get_session_factory()
        assert factory1 is factory2

    def test_get_session_factory_creates_sessions(self):
        """正常系: セッションファクトリからセッションが作成できる"""
        session_factory = connection.get_session_factory()
        session = session_factory()
        assert session is not None
        assert hasattr(session, 'query')
        assert hasattr(session, 'commit')
        assert hasattr(session, 'close')
        session.close()

    def test_get_session_factory_binds_to_engine(self):
        """正常系: セッションファクトリがエンジンにバインドされる"""
        engine = connection.get_engine()
        session_factory = connection.get_session_factory()
        session = session_factory()

        # セッションがエンジンにバインドされていることを確認
        assert session.bind is engine
        session.close()

    def test_get_session_factory_multiple_sessions(self):
        """正常系: 複数のセッションを作成できる"""
        session_factory = connection.get_session_factory()
        session1 = session_factory()
        session2 = session_factory()

        # 異なるセッションインスタンスが作成されることを確認
        assert session1 is not session2

        session1.close()
        session2.close()


class TestGetBase:
    """get_base関数のテストクラス"""

    def setup_method(self):
        """各テストメソッドの前にグローバル変数をリセット"""
        connection._engine = None
        connection._Session = None
        connection._Base = None

    def test_get_base_creates_base(self):
        """正常系: ベースクラスが作成される"""
        base = connection.get_base()
        assert base is not None

    def test_get_base_singleton_pattern(self):
        """正常系: シングルトンパターン - 同じインスタンスが返される"""
        base1 = connection.get_base()
        base2 = connection.get_base()
        assert base1 is base2

    def test_get_base_is_declarative_base(self):
        """正常系: declarative_base型である"""
        base = connection.get_base()
        # declarative_baseの特徴的な属性が存在することを確認
        assert hasattr(base, 'metadata')
        assert hasattr(base, 'registry')


class TestGetSession:
    """get_session関数(コンテキストマネージャ)のテストクラス"""

    def setup_method(self):
        """各テストメソッドの前にグローバル変数をリセット"""
        connection._engine = None
        connection._Session = None
        connection._Base = None

    def test_get_session_context_manager(self):
        """正常系: コンテキストマネージャとして動作する"""
        with connection.get_session() as session:
            assert session is not None
            assert hasattr(session, 'query')
            assert hasattr(session, 'commit')
            assert hasattr(session, 'close')

    def test_get_session_closes_on_exit(self):
        """正常系: コンテキスト終了時にセッションがクローズされる"""
        with patch.object(connection, 'get_session_factory') as mock_factory:
            mock_session = MagicMock()
            mock_factory.return_value = MagicMock(return_value=mock_session)

            with connection.get_session() as session:
                pass

            # セッションがクローズされたことを確認
            mock_session.close.assert_called_once()

    def test_get_session_closes_on_exception(self):
        """正常系: 例外発生時でもセッションがクローズされる"""
        with patch.object(connection, 'get_session_factory') as mock_factory:
            mock_session = MagicMock()
            mock_factory.return_value = MagicMock(return_value=mock_session)

            try:
                with connection.get_session() as session:
                    raise ValueError("Test exception")
            except ValueError:
                pass

            # 例外発生時でもセッションがクローズされたことを確認
            mock_session.close.assert_called_once()

    def test_get_session_yields_session(self):
        """正常系: セッションインスタンスがyieldされる"""
        with connection.get_session() as session:
            assert session is not None
            # セッションの基本的な操作が可能であることを確認
            assert hasattr(session, 'query')
            assert hasattr(session, 'add')
            assert hasattr(session, 'commit')
            assert hasattr(session, 'rollback')

    def test_get_session_multiple_contexts(self):
        """正常系: 複数のコンテキストで異なるセッションが作成される"""
        sessions = []

        for _ in range(3):
            with connection.get_session() as session:
                sessions.append(session)

        # すべて異なるセッションインスタンスであることを確認
        assert len(sessions) == 3
        assert sessions[0] is not sessions[1]
        assert sessions[1] is not sessions[2]

    def test_get_session_nested_contexts(self):
        """正常系: ネストされたコンテキストで異なるセッションが作成される"""
        with connection.get_session() as session1:
            assert session1 is not None
            with connection.get_session() as session2:
                assert session2 is not None
                # 異なるセッションインスタンスであることを確認
                assert session1 is not session2

    def test_get_session_cleanup_guarantee(self):
        """正常系: finallyブロックによるクリーンアップ保証"""
        with patch.object(connection, 'get_session_factory') as mock_factory:
            mock_session = MagicMock()
            mock_factory.return_value = MagicMock(return_value=mock_session)

            # 正常終了時
            with connection.get_session() as session:
                pass
            assert mock_session.close.call_count == 1

            # 例外発生時
            try:
                with connection.get_session() as session:
                    raise RuntimeError("Test error")
            except RuntimeError:
                pass
            assert mock_session.close.call_count == 2


class TestDatabaseIntegration:
    """データベース接続の統合テスト"""

    def setup_method(self):
        """各テストメソッドの前にグローバル変数をリセット"""
        connection._engine = None
        connection._Session = None
        connection._Base = None

    def test_engine_session_base_integration(self):
        """正常系: エンジン、セッション、ベースが連携して動作する"""
        engine = connection.get_engine()
        session_factory = connection.get_session_factory()
        base = connection.get_base()

        # すべてが正常に作成されることを確認
        assert engine is not None
        assert session_factory is not None
        assert base is not None

        # セッションがエンジンにバインドされていることを確認
        with connection.get_session() as session:
            assert session.bind is engine

    def test_global_state_consistency(self):
        """正常系: グローバル状態の一貫性"""
        # 複数回呼び出しても同じインスタンスが保持される
        engine1 = connection.get_engine()
        factory1 = connection.get_session_factory()
        base1 = connection.get_base()

        engine2 = connection.get_engine()
        factory2 = connection.get_session_factory()
        base2 = connection.get_base()

        assert engine1 is engine2
        assert factory1 is factory2
        assert base1 is base2

        # グローバル変数が正しく設定されている
        assert connection._engine is engine1
        assert connection._Session is factory1
        assert connection._Base is base1

    def test_session_lifecycle_management(self):
        """正常系: セッションのライフサイクル管理"""
        with patch.object(connection, 'get_session_factory') as mock_factory:
            mock_session = MagicMock()
            mock_session_instance = mock_session.return_value
            mock_factory.return_value = mock_session

            # コンテキストマネージャ使用
            with connection.get_session() as session:
                # セッションが作成される
                assert mock_session.called
                # セッション内での操作が可能
                assert session is not None

            # コンテキスト終了後、セッションがクローズされる
            mock_session_instance.close.assert_called_once()
