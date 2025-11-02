import os

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from utils import config_manager

config = config_manager.load_config()
csv_file_path = config.get('FilePaths', 'patient_data')


class MyHandler(FileSystemEventHandler):
    def __init__(self, page):
        self.page = page

    def on_deleted(self, event):
        if event.src_path == csv_file_path:
            self.page.window.close()


def start_file_monitoring(page):
    """ファイル監視開始"""
    event_handler = MyHandler(page)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(csv_file_path), recursive=False)
    observer.start()
    return observer


def check_file_exists(page):
    """ファイル存在確認"""
    if not os.path.exists(csv_file_path):
        page.window.close()
