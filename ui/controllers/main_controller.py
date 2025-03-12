import os
import sys
import flet as ft
from datetime import datetime
import threading
import configparser
import pandas as pd

from models.patient import PatientInfo
from database.connection import get_session, init_database
from ui.views.main_view import create_ui
from services.csv_service import CSVService


csv_service = CSVService()

# バージョン情報
VERSION = "1.1.4"
LAST_UPDATED = "2024/09/28"

# 実行ファイルかどうかを確認し本番環境（実行形式ファイル）の場合はディレクトリを変更
if getattr(sys, 'frozen', False):
    app_directory = r"C:\Shinseikai\LDTPapp"
    os.chdir(app_directory)

# config.iniファイルの読み込み
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
csv_file_path = config.get('FilePaths', 'patient_data')

import os
import sys
import flet as ft
from datetime import datetime
import threading
import configparser
import pandas as pd

from models.patient import PatientInfo
from database.connection import get_session
from services.csv_service import CSVService
from utils.file_utils import check_file_exists, create_file_monitor


class MainController:
    """アプリケーションのメインコントローラクラス"""

    def __init__(self, page, main_view, template_editor, form_controller,
                 patient_repo, template_repo, csv_service, config, version, last_updated):
        """
        MainControllerクラスの初期化

        Args:
            page: Fletページオブジェクト
            main_view: メインビューオブジェクト
            template_editor: テンプレートエディターオブジェクト
            form_controller: フォームコントローラオブジェクト
            patient_repo: 患者リポジトリ
            template_repo: テンプレートリポジトリ
            csv_service: CSVサービス
            config: 設定マネージャー
            version: アプリケーションバージョン
            last_updated: 最終更新日
        """
        self.page = page
        self.main_view = main_view
        self.template_editor = template_editor
        self.form_controller = form_controller
        self.patient_repo = patient_repo
        self.template_repo = template_repo
        self.csv_service = csv_service
        self.config = config
        self.version = version
        self.last_updated = last_updated
        self.selected_row = None

        # ファイルパス設定の取得
        self.csv_file_path = self.config.get_value('FilePaths', 'patient_data')
        self.export_folder = self.config.get_value('FilePaths', 'export_folder')
        self.manual_pdf_path = self.config.get_value('FilePaths', 'manual_pdf')

        # ファイル選択ダイアログの初期化
        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.page.overlay.append(self.file_picker)

    def load_patient_info(self, patient_id):
        """
        患者情報を読み込む

        Args:
            patient_id: 患者ID
        """
        error_message, df_patients = self.csv_service.load_patient_data()
        if df_patients is not None and not df_patients.empty:
            self.main_view.load_patient_info(patient_id, df_patients)

    def update_history(self, patient_id=None):
        """
        履歴を更新する

        Args:
            patient_id: 患者ID（オプション）
        """
        self.main_view.update_history(patient_id)

    def route_change(self, e):
        """
        ルート変更時の処理

        Args:
            e: イベントオブジェクト
        """
        # ルート変更の処理を実装
        pass

    def view_pop(self, e):
        """
        ビューポップ時の処理

        Args:
            e: イベントオブジェクト
        """
        # ビューポップの処理を実装
        pass

    def on_startup(self):
        """スタートアップ時の処理"""
        # 初期化処理を実装
        check_file_exists(self.page)

    def on_file_selected(self, e):
        """
        ファイル選択時の処理

        Args:
            e: ファイル選択イベント
        """
        if e.files:
            file_path = e.files[0].path
            self.import_csv(file_path)

    def import_csv(self, file_path):
        """
        CSVファイルをインポートする

        Args:
            file_path: CSVファイルのパス
        """
        success, message = self.csv_service.import_csv(file_path)
        self.show_message(message)
        self.update_history()

    def export_to_csv(self):
        """CSVファイルをエクスポートする"""
        success, message, file_path = self.csv_service.export_to_csv()
        self.show_message(message)
        if success and file_path:
            os.startfile(os.path.dirname(file_path))

    def show_message(self, message, duration=1000):
        """
        メッセージを表示する

        Args:
            message: 表示するメッセージ
            duration: 表示時間（ミリ秒）
        """
        snack_bar = ft.SnackBar(content=ft.Text(message), duration=duration)
        snack_bar.open = True
        self.page.overlay.append(snack_bar)
        self.page.update()

    def show_error(self, error_message, duration=3000):
        """
        エラーメッセージを表示する

        Args:
            error_message: エラーメッセージ
            duration: 表示時間（ミリ秒）
        """
        self.show_message(error_message, duration)

    def open_settings_dialog(self):
        """設定ダイアログを表示する"""
        # 設定ダイアログの表示処理を実装
        pass

    def open_pdf_manual(self):
        """PDFマニュアルを開く"""
        if self.manual_pdf_path and os.path.exists(self.manual_pdf_path):
            try:
                os.startfile(self.manual_pdf_path)
            except Exception as e:
                self.show_error(f"PDFを開けませんでした: {str(e)}")

    def create_new_patient(self):
        """新しい患者情報を作成する"""
        # 新規作成処理を実装
        pass

    def copy_latest_plan(self, patient_id):
        """
        最新の計画をコピーする

        Args:
            patient_id: 患者ID
        """
        error_message, df_patients = self.csv_service.load_patient_data()
        if error_message:
            self.show_error(error_message)
            return

        success, new_id = self.patient_repo.copy_latest_plan(int(patient_id), df_patients)
        if success:
            self.show_message("前回の計画内容をコピーしました")
            self.update_history(patient_id)
        else:
            self.show_error("コピーする計画が見つかりませんでした")


class MyHandler:
    def __init__(self, page):
        self.page = page

    def on_deleted(self, event):
        if event.src_path == csv_file_path:
            self.page.window.close()


def start_file_monitoring(page):
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class EventHandler(FileSystemEventHandler, MyHandler):
        def __init__(self, page):
            MyHandler.__init__(self, page)

    event_handler = EventHandler(page)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(csv_file_path), recursive=False)
    observer.start()
    return observer


def check_file_exists(page):
    if not os.path.exists(csv_file_path):
        page.window.close()


def main(page: ft.Page):
    # データベースの初期化処理をバックグラウンドで実行
    threading.Thread(target=init_database).start()

    # pat.csvの読み込み
    error_message, df_patients = csv_service.load_patient_data()
    initial_patient_id = ""

    if error_message:
        print(error_message)
    else:
        if df_patients is not None and not df_patients.empty:
            initial_patient_id = int(df_patients.iloc[0, 2])

    # ファイル監視の開始
    start_file_monitoring(page)
    check_file_exists(page)

    # UI作成
    create_ui(page, initial_patient_id, df_patients, VERSION, LAST_UPDATED)


if __name__ == "__main__":
    ft.app(target=main)
