import flet as ft

from app.main_ui import create_ui
from database.initializer import initialize_database, seed_initial_data
from services.file_monitor_service import start_file_monitoring, check_file_exists


def main(page: ft.Page):
    """メインエントリーポイント"""
    # データベース初期化
    initialize_database()
    seed_initial_data()

    # ファイル監視開始
    start_file_monitoring(page)
    check_file_exists(page)

    # UIを作成
    create_ui(page)


if __name__ == "__main__":
    ft.app(target=main)
