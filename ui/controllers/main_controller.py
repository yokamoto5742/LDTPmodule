import os
import sys
import flet as ft
from datetime import datetime
import threading
import configparser
import pandas as pd

from models.patient import PatientInfo
from database.connection import get_session, initialize_database
from ui.views.main_view import create_ui
from services.csv_service import load_patient_data

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
    threading.Thread(target=initialize_database).start()

    # pat.csvの読み込み
    error_message, df_patients = load_patient_data()
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
