import os
from pathlib import Path

import flet as ft

from app import __version__ as VERSION
from app import __date__ as LAST_UPDATED
from services.data_export_service import export_to_csv, import_from_csv


class DialogManager:
    """ダイアログとメッセージ表示を管理するクラス"""

    def __init__(self, page, fields=None, update_history_callback=None):
        """
        初期化

        Args:
            page: Fletのページオブジェクト
            fields: フォームフィールドの辞書
            update_history_callback: 履歴更新のコールバック関数
        """
        self.page = page
        self.fields = fields or {}
        self.update_history_callback = update_history_callback

        # ファイルピッカーの初期化
        self.file_picker = ft.FilePicker(on_result=self._on_file_selected)
        self.page.overlay.append(self.file_picker)

    def show_error_message(self, message):
        """エラーメッセージを表示"""
        snack_bar = ft.SnackBar(content=ft.Text(message), duration=1000)
        snack_bar.open = True
        self.page.overlay.append(snack_bar)
        self.page.update()

    def show_info_message(self, message, duration=1000):
        """情報メッセージを表示"""
        snack_bar = ft.SnackBar(content=ft.Text(message), duration=duration)
        snack_bar.open = True
        self.page.overlay.append(snack_bar)
        self.page.update()

    def check_required_fields(self):
        """必須フィールドのチェック"""
        main_diagnosis = self.fields.get('main_diagnosis')
        sheet_name_dropdown = self.fields.get('sheet_name_dropdown')

        if not main_diagnosis or not main_diagnosis.value:
            self.show_error_message("主病名を選択してください")
            return False
        if not sheet_name_dropdown or not sheet_name_dropdown.value:
            self.show_error_message("シート名を選択してください")
            return False
        return True

    def open_settings_dialog(self, e, export_folder):
        """設定ダイアログを開く"""
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        def csv_export(e):
            self._export_to_csv_ui(e, export_folder)
            close_dialog(e)

        content = ft.Container(
            content=ft.Column([
                ft.Text(f"LDTPapp\nバージョン: {VERSION}\n最終更新日: {LAST_UPDATED}"),
                ft.ElevatedButton("CSV出力", on_click=csv_export),
                ft.ElevatedButton("CSV取込", on_click=lambda _: self.file_picker.pick_files()),
            ]),
            height=self.page.window.height * 0.3,
        )

        dialog = ft.AlertDialog(
            title=ft.Text("設定"),
            content=content,
            actions=[
                ft.TextButton("閉じる", on_click=close_dialog)
            ]
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _on_file_selected(self, e: ft.FilePickerResultEvent):
        """ファイル選択イベントのハンドラ"""
        if e.files:
            file_path = e.files[0].path
            self._import_csv(file_path)

    def _import_csv(self, file_path):
        """CSVファイルからデータをインポート"""
        error = import_from_csv(file_path)
        if error:
            duration = 3000 if "インポート中に" in error else 1000
            self.show_info_message(error, duration=duration)
        else:
            self.show_info_message("CSVファイルからデータがインポートされました")
            if self.update_history_callback:
                patient_id = self.fields.get('patient_id')
                if patient_id and patient_id.value:
                    self.update_history_callback(int(patient_id.value))

    def _export_to_csv_ui(self, e, export_folder):
        """データをCSVファイルにエクスポート"""
        csv_filename, csv_path, error = export_to_csv(export_folder)
        if error:
            self.show_info_message(f"エクスポート中にエラーが発生しました: {error}")
        else:
            self.show_info_message(f"データがCSVファイル '{csv_filename}' にエクスポートされました")
            os.startfile(export_folder)
