import os
from datetime import datetime

import flet as ft
from flet import View


class RouteManager:
    """ルーティングを管理するクラス"""

    def __init__(self, page, fields, ui_elements, event_handlers, manual_pdf_path):
        """
        初期化

        Args:
            page: Fletのページオブジェクト
            fields: フォームフィールドの辞書
            ui_elements: UI要素の辞書（buttons, guidance_items等）
            event_handlers: EventHandlersインスタンス
            manual_pdf_path: 操作マニュアルのパス
        """
        self.page = page
        self.fields = fields
        self.ui_elements = ui_elements
        self.event_handlers = event_handlers
        self.manual_pdf_path = manual_pdf_path

    def route_change(self, e):
        """ルート変更処理"""
        self.page.views.clear()
        self._build_home_view()

        if self.page.route == "/create":
            self._build_create_view()

        if self.page.route == "/edit":
            self._build_edit_view()

        if self.page.route == "/template":
            self._build_template_view()

        self.page.update()

    def _build_home_view(self):
        """ホームビューを構築"""
        fields = self.fields
        ui = self.ui_elements

        self.page.views.append(
            View(
                "/",
                [
                    ft.Row(
                        controls=[
                            fields['patient_id'],
                            fields['name_value'],
                            fields['kana_value'],
                            fields['gender_value'],
                            fields['birthdate_value'],
                        ]
                    ),
                    ft.Row(
                        controls=[
                            fields['doctor_id_value'],
                            fields['doctor_name_value'],
                            fields['department_id_value'],
                            fields['department_value'],
                            ui['settings_button'],
                            ui['manual_button'],
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ui['buttons'],
                            ft.Text("(SOAP画面を閉じるとアプリは終了します)", size=12)
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("計画書一覧", size=16),
                            ft.Text("計画書をクリックすると編集画面が開きます", size=14),
                        ]
                    ),
                    ft.Divider(),
                    ui['history_scrollable'],
                ],
            )
        )

    def _build_create_view(self):
        """新規作成ビューを構築"""
        fields = self.fields
        ui = self.ui_elements

        self.page.views.append(
            View(
                "/create",
                [
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text("新規作成", size=16, weight=ft.FontWeight.BOLD),
                                border=ft.border.all(3, ft.colors.BLUE),  # type: ignore[attr-defined]
                                padding=5,
                                border_radius=5,
                            ),
                            fields['main_diagnosis'],
                            fields['sheet_name_dropdown'],
                            fields['creation_count'],
                            ft.Text("回目", size=14),
                            ui['issue_date_row'],
                        ]
                    ),
                    fields['goal1'],
                    fields['goal2'],
                    ui['guidance_items'],
                    ui['create_buttons'],
                ],
            )
        )

    def _build_edit_view(self):
        """編集ビューを構築"""
        fields = self.fields
        ui = self.ui_elements

        self.page.views.append(
            View(
                "/edit",
                [
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text("編集", size=16, weight=ft.FontWeight.BOLD),
                                border=ft.border.all(3, ft.colors.BLUE),  # type: ignore[attr-defined]
                                padding=5,
                                border_radius=5,
                            ),
                            fields['main_diagnosis'],
                            fields['sheet_name_dropdown'],
                            fields['creation_count'],
                            ft.Text("回目", size=14),
                            ui['issue_date_row'],
                        ]
                    ),
                    ft.Row(
                        controls=[
                            fields['goal1'],
                        ]
                    ),
                    fields['goal2'],
                    ui['guidance_items'],
                    ui['edit_buttons'],
                ],
            )
        )

    def _build_template_view(self):
        """テンプレートビューを構築"""
        fields = self.fields
        ui = self.ui_elements

        self.page.views.append(
            View(
                "/template",
                [
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text("テンプレート", size=16, weight=ft.FontWeight.BOLD),
                                border=ft.border.all(3, ft.colors.BLUE),  # type: ignore[attr-defined]
                                padding=5,
                                border_radius=5,
                            ),
                            fields['main_diagnosis'],
                            fields['sheet_name_dropdown'],
                        ]
                    ),
                    ft.Row(
                        controls=[
                            fields['goal1'],
                        ]
                    ),
                    fields['goal2'],
                    ui['guidance_items_template'],
                    ui['template_buttons'],
                ],
            )
        )

    def view_pop(self, e):
        """ビューを戻る"""
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def open_create(self, e):
        """新規作成画面を開く"""
        self.page.go("/create")

    def open_edit(self, e):
        """編集画面を開く"""
        self.page.go("/edit")

    def open_template(self, e):
        """テンプレート画面を開く"""
        self.page.go("/template")
        self.event_handlers.apply_template(e)

    def open_route(self, e):
        """ホーム画面を開く（フィールドをリセット）"""
        fields = self.fields
        issue_date_picker = self.ui_elements.get('issue_date_picker')

        # フィールドをクリア
        clear_fields = [
            'target_weight', 'target_bp', 'target_hba1c', 'goal1', 'goal2',
            'target_achievement', 'diet1', 'diet2', 'diet3', 'diet4',
            'diet_comment', 'exercise_prescription', 'exercise_time',
            'exercise_frequency', 'exercise_intensity', 'daily_activity',
            'exercise_comment', 'other1', 'other2', 'issue_date_value'
        ]

        for field_name in clear_fields:
            if field_name in fields:
                fields[field_name].value = ""

        fields['main_diagnosis'].value = ""
        fields['sheet_name_dropdown'].value = ""
        fields['creation_count'].value = 1
        fields['nonsmoker'].value = False
        fields['smoking_cessation'].value = False
        fields['ophthalmology'].value = False
        fields['dental'].value = False
        fields['cancer_screening'].value = False

        # 発行日を現在の日付で初期化
        current_date = datetime.now().date()
        fields['issue_date_value'].value = current_date.strftime("%Y/%m/%d")
        if issue_date_picker:
            issue_date_picker.value = current_date

        self.page.go("/")
        patient_id = fields.get('patient_id')
        if patient_id and patient_id.value:
            self.event_handlers.update_history(int(patient_id.value))
        self.page.update()

    def open_manual_pdf(self, e):
        """操作マニュアルPDFを開く"""
        if self.manual_pdf_path and os.path.exists(self.manual_pdf_path):
            try:
                os.startfile(self.manual_pdf_path)
            except Exception as ex:
                error_message = f"PDFを開けませんでした: {str(ex)}"
                error_snack_bar = ft.SnackBar(content=ft.Text(error_message), duration=1000)
                error_snack_bar.open = True
                self.page.overlay.append(error_snack_bar)
                self.page.update()
        else:
            error_message = "操作マニュアルのパスを確認してください"
            error_snack_bar = ft.SnackBar(content=ft.Text(error_message), duration=1000)
            error_snack_bar.open = True
            self.page.overlay.append(error_snack_bar)
            self.page.update()

    def on_close(self, e):
        """ウィンドウを閉じる"""
        self.page.window.close()
