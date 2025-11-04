import configparser
import os
import sys
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

from utils import config_manager


class TestGetConfigPath:
    """get_config_path関数のテストクラス"""

    def test_get_config_path_normal_execution(self):
        """正常系: 通常のPythonスクリプト実行時のパス取得"""
        # sys.frozenが存在しない、またはFalseの場合
        with patch.object(sys, 'frozen', False, create=True):
            result = config_manager.get_config_path()
            expected_base = os.path.dirname(config_manager.__file__)
            expected_path = os.path.join(expected_base, 'config.ini')
            assert result == expected_path

    def test_get_config_path_pyinstaller_execution(self):
        """正常系: PyInstaller実行ファイルでのパス取得"""
        # sys.frozenがTrueの場合
        with patch.object(sys, 'frozen', True, create=True):
            with patch.object(sys, '_MEIPASS', 'C:\\temp\\pyinstaller_path', create=True):
                result = config_manager.get_config_path()
                expected_path = os.path.join('C:\\temp\\pyinstaller_path', 'config.ini')
                assert result == expected_path

    def test_get_config_path_returns_absolute_path(self):
        """正常系: 絶対パスが返される"""
        result = config_manager.get_config_path()
        assert os.path.isabs(result)

    def test_get_config_path_includes_config_ini(self):
        """正常系: パスにconfig.iniが含まれる"""
        result = config_manager.get_config_path()
        assert result.endswith('config.ini')


class TestLoadConfig:
    """load_config関数のテストクラス"""

    @pytest.fixture
    def temp_config_file(self):
        """一時設定ファイルのフィクスチャ"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', encoding='utf-8', delete=False) as f:
            f.write("[Database]\n")
            f.write("db_url = sqlite:///test.db\n")
            f.write("[Paths]\n")
            f.write("template_path = C:\\test\\template.xlsm\n")
            temp_path = f.name

        yield temp_path

        # クリーンアップ
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_load_config_success(self, temp_config_file):
        """正常系: 設定ファイルの読み込みが成功する"""
        with patch.object(config_manager, 'CONFIG_PATH', temp_config_file):
            config = config_manager.load_config()

            assert isinstance(config, configparser.ConfigParser)
            assert config.has_section('Database')
            assert config.has_section('Paths')
            assert config.get('Database', 'db_url') == 'sqlite:///test.db'
            assert config.get('Paths', 'template_path') == 'C:\\test\\template.xlsm'

    def test_load_config_file_not_found(self):
        """異常系: 設定ファイルが存在しない"""
        non_existent_path = 'C:\\nonexistent\\config.ini'

        with patch.object(config_manager, 'CONFIG_PATH', non_existent_path):
            with pytest.raises(FileNotFoundError):
                config_manager.load_config()

    def test_load_config_permission_error(self):
        """異常系: 設定ファイルの読み取り権限がない"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch.object(config_manager, 'CONFIG_PATH', 'dummy_path.ini'):
                with pytest.raises(PermissionError):
                    config_manager.load_config()

    def test_load_config_parse_error(self):
        """異常系: 設定ファイルの解析エラー"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', encoding='utf-8', delete=False) as f:
            # 不正なINIフォーマット
            f.write("[Database\n")  # セクション名が閉じられていない
            f.write("db_url = sqlite:///test.db\n")
            temp_path = f.name

        try:
            with patch.object(config_manager, 'CONFIG_PATH', temp_path):
                with pytest.raises(configparser.Error):
                    config_manager.load_config()
        finally:
            os.unlink(temp_path)

    def test_load_config_empty_file(self):
        """正常系: 空の設定ファイル"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', encoding='utf-8', delete=False) as f:
            # 空のファイル
            temp_path = f.name

        try:
            with patch.object(config_manager, 'CONFIG_PATH', temp_path):
                config = config_manager.load_config()
                assert isinstance(config, configparser.ConfigParser)
                assert len(config.sections()) == 0
        finally:
            os.unlink(temp_path)

    def test_load_config_utf8_encoding(self):
        """正常系: UTF-8エンコーディングで日本語を含む設定ファイル"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', encoding='utf-8', delete=False) as f:
            f.write("[Database]\n")
            f.write("db_url = sqlite:///患者データ.db\n")
            temp_path = f.name

        try:
            with patch.object(config_manager, 'CONFIG_PATH', temp_path):
                config = config_manager.load_config()
                assert config.get('Database', 'db_url') == 'sqlite:///患者データ.db'
        finally:
            os.unlink(temp_path)

    def test_load_config_multiple_sections(self):
        """正常系: 複数セクションを持つ設定ファイル"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', encoding='utf-8', delete=False) as f:
            f.write("[Database]\n")
            f.write("db_url = sqlite:///test.db\n")
            f.write("[Paths]\n")
            f.write("template_path = C:\\test\\template.xlsm\n")
            f.write("output_path = C:\\test\\output\n")
            f.write("[Settings]\n")
            f.write("window_width = 1200\n")
            f.write("window_height = 900\n")
            temp_path = f.name

        try:
            with patch.object(config_manager, 'CONFIG_PATH', temp_path):
                config = config_manager.load_config()
                assert config.has_section('Database')
                assert config.has_section('Paths')
                assert config.has_section('Settings')
                assert config.get('Settings', 'window_width') == '1200'
        finally:
            os.unlink(temp_path)


class TestSaveConfig:
    """save_config関数のテストクラス"""

    @pytest.fixture
    def temp_config_file(self):
        """一時設定ファイルのフィクスチャ"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', encoding='utf-8', delete=False) as f:
            temp_path = f.name

        yield temp_path

        # クリーンアップ
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_save_config_success(self, temp_config_file):
        """正常系: 設定ファイルの保存が成功する"""
        config = configparser.ConfigParser()
        config.add_section('Database')
        config.set('Database', 'db_url', 'sqlite:///test.db')
        config.add_section('Paths')
        config.set('Paths', 'template_path', 'C:\\test\\template.xlsm')

        with patch.object(config_manager, 'CONFIG_PATH', temp_config_file):
            config_manager.save_config(config)

        # 保存されたファイルを読み込んで検証
        saved_config = configparser.ConfigParser()
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            saved_config.read_file(f)

        assert saved_config.has_section('Database')
        assert saved_config.get('Database', 'db_url') == 'sqlite:///test.db'
        assert saved_config.get('Paths', 'template_path') == 'C:\\test\\template.xlsm'

    def test_save_config_permission_error(self):
        """異常系: 設定ファイルの書き込み権限がない"""
        config = configparser.ConfigParser()
        config.add_section('Database')
        config.set('Database', 'db_url', 'sqlite:///test.db')

        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch.object(config_manager, 'CONFIG_PATH', 'dummy_path.ini'):
                with pytest.raises(PermissionError):
                    config_manager.save_config(config)

    def test_save_config_io_error(self):
        """異常系: ファイルI/Oエラー"""
        config = configparser.ConfigParser()
        config.add_section('Database')
        config.set('Database', 'db_url', 'sqlite:///test.db')

        with patch('builtins.open', side_effect=IOError("I/O error")):
            with patch.object(config_manager, 'CONFIG_PATH', 'dummy_path.ini'):
                with pytest.raises(IOError):
                    config_manager.save_config(config)

    def test_save_config_overwrites_existing_file(self, temp_config_file):
        """正常系: 既存ファイルを上書きする"""
        # 初期設定を書き込み
        initial_config = configparser.ConfigParser()
        initial_config.add_section('Database')
        initial_config.set('Database', 'db_url', 'sqlite:///initial.db')

        with patch.object(config_manager, 'CONFIG_PATH', temp_config_file):
            config_manager.save_config(initial_config)

        # 新しい設定で上書き
        new_config = configparser.ConfigParser()
        new_config.add_section('Database')
        new_config.set('Database', 'db_url', 'sqlite:///updated.db')

        with patch.object(config_manager, 'CONFIG_PATH', temp_config_file):
            config_manager.save_config(new_config)

        # 上書きされたファイルを読み込んで検証
        saved_config = configparser.ConfigParser()
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            saved_config.read_file(f)

        assert saved_config.get('Database', 'db_url') == 'sqlite:///updated.db'

    def test_save_config_empty_config(self, temp_config_file):
        """正常系: 空の設定を保存する"""
        config = configparser.ConfigParser()

        with patch.object(config_manager, 'CONFIG_PATH', temp_config_file):
            config_manager.save_config(config)

        # 保存されたファイルを読み込んで検証
        saved_config = configparser.ConfigParser()
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            saved_config.read_file(f)

        assert len(saved_config.sections()) == 0

    def test_save_config_utf8_encoding(self, temp_config_file):
        """正常系: UTF-8エンコーディングで日本語を含む設定を保存"""
        config = configparser.ConfigParser()
        config.add_section('Database')
        config.set('Database', 'db_url', 'sqlite:///患者データ.db')

        with patch.object(config_manager, 'CONFIG_PATH', temp_config_file):
            config_manager.save_config(config)

        # 保存されたファイルを読み込んで検証
        saved_config = configparser.ConfigParser()
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            saved_config.read_file(f)

        assert saved_config.get('Database', 'db_url') == 'sqlite:///患者データ.db'

    def test_save_config_directory_not_exists(self):
        """異常系: 保存先ディレクトリが存在しない"""
        config = configparser.ConfigParser()
        config.add_section('Database')
        config.set('Database', 'db_url', 'sqlite:///test.db')

        non_existent_dir = 'C:\\nonexistent_directory\\config.ini'

        with patch.object(config_manager, 'CONFIG_PATH', non_existent_dir):
            with pytest.raises((IOError, FileNotFoundError)):
                config_manager.save_config(config)


class TestConfigPathIntegration:
    """CONFIG_PATH定数の統合テスト"""

    def test_config_path_is_set(self):
        """正常系: CONFIG_PATH定数が設定されている"""
        assert hasattr(config_manager, 'CONFIG_PATH')
        assert config_manager.CONFIG_PATH is not None

    def test_config_path_is_string(self):
        """正常系: CONFIG_PATHが文字列である"""
        assert isinstance(config_manager.CONFIG_PATH, str)

    def test_config_path_ends_with_config_ini(self):
        """正常系: CONFIG_PATHがconfig.iniで終わる"""
        assert config_manager.CONFIG_PATH.endswith('config.ini')
