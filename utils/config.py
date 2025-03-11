import os
import configparser
from typing import Dict, Any, Optional, Union, List
import sys


class ConfigManager:
    """設定ファイルを管理するクラス"""

    def __init__(self, config_file: str = 'config.ini'):
        """
        ConfigManagerクラスの初期化

        Args:
            config_file: 設定ファイルのパス
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()

        # 実行ファイルかどうかを確認し本番環境の場合はディレクトリを変更
        if getattr(sys, 'frozen', False):
            app_directory = r"C:\Shinseikai\LDTPapp"
            os.chdir(app_directory)

        # 設定ファイルを読み込む
        try:
            self.config.read(config_file, encoding='utf-8')
        except Exception as e:
            print(f"設定ファイルの読み込みに失敗しました: {str(e)}")
            # 最低限のデフォルト設定を作成
            self._create_default_config()

    def _create_default_config(self):
        """デフォルトの設定を作成する"""
        # 基本的なセクションと設定を追加
        self.config['Database'] = {
            'db_url': 'sqlite:///ldtp_app.db'
        }
        self.config['settings'] = {
            'window_width': '1200',
            'window_height': '900'
        }
        self.config['UI'] = {
            'input_height': '60',
            'text_height': '40'
        }
        self.config['DataTable'] = {
            'width': '1200'
        }
        self.config['Paths'] = {
            'template_path': 'C:\\Shinseikai\\LDTPapp\\LDTPform.xlsm',
            'output_path': 'C:\\Shinseikai\\LDTPapp\\temp'
        }
        self.config['FilePaths'] = {
            'patient_data': 'C:\\InnoKarte\\pat.csv',
            'export_folder': 'C:\\Shinseikai\\LDTPapp\\export_data',
            'manual_pdf': 'C:\\Shinseikai\\LDTPapp\\LDTPapp_manual.pdf'
        }
        self.config['Barcode'] = {
            'write_text': 'false',
            'module_height': '15',
            'module_width': '0.25',
            'quiet_zone': '1',
            'image_width': '200',
            'image_height': '30',
            'image_position': 'B2'
        }
        self.config['Document'] = {
            'document_number': '39221'
        }

        # デフォルト設定をファイルに保存
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"デフォルト設定の保存に失敗しました: {str(e)}")

    def get_database_url(self) -> str:
        """
        データベースURLを取得

        Returns:
            str: データベースURL
        """
        return self.config.get('Database', 'db_url', fallback='sqlite:///ldtp_app.db')

    def get_window_settings(self) -> Dict[str, int]:
        """
        ウィンドウ設定を取得

        Returns:
            Dict[str, int]: ウィンドウ幅と高さ
        """
        return {
            'width': self.config.getint('settings', 'window_width', fallback=1200),
            'height': self.config.getint('settings', 'window_height', fallback=900)
        }

    def get_ui_settings(self) -> Dict[str, int]:
        """
        UI設定を取得

        Returns:
            Dict[str, int]: 入力フィールドの高さなど
        """
        return {
            'input_height': self.config.getint('UI', 'input_height', fallback=60),
            'text_height': self.config.getint('UI', 'text_height', fallback=40)
        }

    def get_datatable_width(self) -> int:
        """
        データテーブルの幅を取得

        Returns:
            int: データテーブルの幅
        """
        return self.config.getint('DataTable', 'width', fallback=1200)

    def get_paths(self) -> Dict[str, str]:
        """
        パス設定を取得

        Returns:
            Dict[str, str]: テンプレートパスと出力パス
        """
        return {
            'template_path': self.config.get('Paths', 'template_path',
                                             fallback='C:\\Shinseikai\\LDTPapp\\LDTPform.xlsm'),
            'output_path': self.config.get('Paths', 'output_path',
                                           fallback='C:\\Shinseikai\\LDTPapp\\temp')
        }

    def get_file_paths(self) -> Dict[str, str]:
        """
        ファイルパス設定を取得

        Returns:
            Dict[str, str]: 患者データCSVパス、エクスポートフォルダ、マニュアルPDFパス
        """
        return {
            'patient_data': self.config.get('FilePaths', 'patient_data',
                                            fallback='C:\\InnoKarte\\pat.csv'),
            'export_folder': self.config.get('FilePaths', 'export_folder',
                                             fallback='C:\\Shinseikai\\LDTPapp\\export_data'),
            'manual_pdf': self.config.get('FilePaths', 'manual_pdf',
                                          fallback='C:\\Shinseikai\\LDTPapp\\LDTPapp_manual.pdf')
        }

    def get_document_number(self) -> str:
        """
        ドキュメント番号を取得

        Returns:
            str: ドキュメント番号
        """
        return self.config.get('Document', 'document_number', fallback='39221')

    def get_barcode_config(self) -> Dict[str, Any]:
        """
        バーコード設定を取得

        Returns:
            Dict[str, Any]: バーコード設定
        """
        barcode_section = self.config['Barcode'] if 'Barcode' in self.config else {}

        return {
            'write_text': self.config.getboolean('Barcode', 'write_text', fallback=False),
            'module_height': self.config.getfloat('Barcode', 'module_height', fallback=15),
            'module_width': self.config.getfloat('Barcode', 'module_width', fallback=0.25),
            'quiet_zone': self.config.getint('Barcode', 'quiet_zone', fallback=1),
            'image_width': self.config.getint('Barcode', 'image_width', fallback=200),
            'image_height': self.config.getint('Barcode', 'image_height', fallback=30),
            'image_position': self.config.get('Barcode', 'image_position', fallback='B2')
        }

    def get_barcode_options(self) -> Dict[str, Any]:
        """
        バーコード生成オプションを取得

        Returns:
            Dict[str, Any]: バーコード生成オプション
        """
        return {
            'write_text': self.config.getboolean('Barcode', 'write_text', fallback=False),
            'module_height': self.config.getfloat('Barcode', 'module_height', fallback=15),
            'module_width': self.config.getfloat('Barcode', 'module_width', fallback=0.25),
            'quiet_zone': self.config.getint('Barcode', 'quiet_zone', fallback=1),
        }

    def get_value(self, section: str, option: str, fallback: Any = None) -> Any:
        """
        任意の設定値を取得

        Args:
            section: セクション名
            option: オプション名
            fallback: デフォルト値

        Returns:
            Any: 設定値
        """
        if not self.config.has_section(section):
            return fallback

        if not self.config.has_option(section, option):
            return fallback

        return self.config.get(section, option, fallback=fallback)

    def get_int(self, section: str, option: str, fallback: int = 0) -> int:
        """
        整数の設定値を取得

        Args:
            section: セクション名
            option: オプション名
            fallback: デフォルト値

        Returns:
            int: 整数の設定値
        """
        return self.config.getint(section, option, fallback=fallback)

    def get_float(self, section: str, option: str, fallback: float = 0.0) -> float:
        """
        浮動小数点の設定値を取得

        Args:
            section: セクション名
            option: オプション名
            fallback: デフォルト値

        Returns:
            float: 浮動小数点の設定値
        """
        return self.config.getfloat(section, option, fallback=fallback)

    def get_boolean(self, section: str, option: str, fallback: bool = False) -> bool:
        """
        真偽値の設定値を取得

        Args:
            section: セクション名
            option: オプション名
            fallback: デフォルト値

        Returns:
            bool: 真偽値の設定値
        """
        return self.config.getboolean(section, option, fallback=fallback)

    def update_value(self, section: str, option: str, value: Any) -> bool:
        """
        設定値を更新

        Args:
            section: セクション名
            option: オプション名
            value: 新しい値

        Returns:
            bool: 更新に成功したかどうか
        """
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)

            self.config.set(section, option, str(value))

            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)

            return True
        except Exception as e:
            print(f"設定の更新に失敗しました: {str(e)}")
            return False

    def get_all_settings(self) -> Dict[str, Dict[str, str]]:
        """
        すべての設定を取得

        Returns:
            Dict[str, Dict[str, str]]: すべての設定
        """
        settings = {}
        for section in self.config.sections():
            settings[section] = {}
            for option in self.config[section]:
                settings[section][option] = self.config[section][option]

        return settings


# シングルトンインスタンスの作成
config_manager = ConfigManager()
