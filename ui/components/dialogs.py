import os
import flet as ft
from ...services.csv_service import CSVService
from ...services.version_manager import get_version_info


class DialogManager:
    """
    アプリケーションで使用されるダイアログやメッセージを管理するクラス
    """

    def __init__(self, page: ft.Page):
        """
        ダイアログマネージャーの初期化

        Args:
            page (ft.Page): ダイアログを表示するページオブジェクト
        """
        self.page = page
        self.csv_service = CSVService()
        self.version, self.last_updated = get_version_info()

        # ファイル選択ダイアログの初期化
        self.file_picker = ft.FilePicker()
        self.page.overlay.append(self.file_picker)

    def show_settings_dialog(self, export_callback=None, import_callback=None):
        """
        設定ダイアログを表示する

        Args:
            export_callback (callable, optional): CSV出力ボタンのコールバック
            import_callback (callable, optional): CSV取込ボタンのコールバック
        """

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        def csv_export(e):
            if export_callback:
                export_callback(e)
            close_dialog(e)

        def on_import_click(e):
            if import_callback:
                self.file_picker.pick_files(
                    allowed_extensions=["csv"],
                    allow_multiple=False,
                    on_result=import_callback
                )
            close_dialog(e)

        # ダイアログコンテンツの作成
        content = ft.Container(
            content=ft.Column([
                ft.Text(f"LDTPapp\nバージョン: {self.version}\n最終更新日: {self.last_updated}"),
                ft.ElevatedButton("CSV出力", on_click=csv_export),
                ft.ElevatedButton("CSV取込", on_click=on_import_click),
            ]),
            height=self.page.window.height * 0.3,
        )

        # ダイアログの作成
        dialog = ft.AlertDialog(
            title=ft.Text("設定"),
            content=content,
            actions=[
                ft.TextButton("閉じる", on_click=close_dialog)
            ]
        )

        # ダイアログの表示
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_confirm_dialog(self, title, content, on_confirm=None, on_cancel=None):
        """
        確認ダイアログを表示する

        Args:
            title (str): ダイアログのタイトル
            content (str): ダイアログの内容
            on_confirm (callable, optional): 確認ボタンのコールバック
            on_cancel (callable, optional): キャンセルボタンのコールバック
        """

        def on_confirm_click(e):
            dialog.open = False
            self.page.update()
            if on_confirm:
                on_confirm(e)

        def on_cancel_click(e):
            dialog.open = False
            self.page.update()
            if on_cancel:
                on_cancel(e)

        # ダイアログの作成
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.TextButton("キャンセル", on_click=on_cancel_click),
                ft.TextButton("確認", on_click=on_confirm_click),
            ]
        )

        # ダイアログの表示
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_message(self, message, duration=1000):
        """
        メッセージをスナックバーとして表示する

        Args:
            message (str): 表示するメッセージ
            duration (int, optional): 表示時間（ミリ秒）。デフォルトは1000ms
        """
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=duration
        )
        snack_bar.open = True
        self.page.overlay.append(snack_bar)
        self.page.update()

    def show_error(self, error_message, duration=3000):
        """
        エラーメッセージをスナックバーとして表示する

        Args:
            error_message (str): 表示するエラーメッセージ
            duration (int, optional): 表示時間（ミリ秒）。デフォルトは3000ms
        """
        self.show_message(error_message, duration)

    def open_pdf_manual(self, manual_path):
        """
        PDFマニュアルを開く

        Args:
            manual_path (str): PDFファイルのパス

        Returns:
            bool: 開くことができた場合はTrue、それ以外はFalse
        """
        if manual_path and os.path.exists(manual_path):
            try:
                os.startfile(manual_path)
                return True
            except Exception as e:
                self.show_error(f"PDFを開けませんでした: {str(e)}")
                return False
        else:
            self.show_error("操作マニュアルのパスを確認してください")
            return False
