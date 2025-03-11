import flet as ft
from typing import Callable, Dict, Any, Optional


class TemplateEditor:
    """テンプレートの編集画面を管理するクラス"""

    def __init__(self, page: ft.Page, patient_form, button_style: Dict[str, Any] = None):
        """
        TemplateEditorクラスの初期化

        Args:
            page: Fletページオブジェクト
            patient_form: 患者情報フォームオブジェクト
            button_style: ボタンのスタイル設定
        """
        self.page = page
        self.patient_form = patient_form
        self.button_style = button_style or {}

        # テンプレート編集画面のボタンの作成
        self.template_buttons = self._create_template_buttons()

    def _create_template_buttons(self):
        """テンプレート編集画面のボタンを作成"""
        return ft.Row([
            ft.ElevatedButton("保存", on_click=None, **self.button_style),
            ft.ElevatedButton("戻る", on_click=None, **self.button_style),
        ])

    def setup_button_handlers(self, save_handler: Callable, back_handler: Callable):
        """
        ボタンのイベントハンドラを設定

        Args:
            save_handler: 保存ボタンのイベントハンドラ
            back_handler: 戻るボタンのイベントハンドラ
        """
        self.template_buttons.controls[0].on_click = save_handler
        self.template_buttons.controls[1].on_click = back_handler
        self.page.update()

    def create_view(self) -> ft.View:
        """
        テンプレート編集画面のビューを作成

        Returns:
            ft.View: テンプレート編集画面のビュー
        """
        return ft.View(
            "/template",
            [
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text("テンプレート", size=16, weight=ft.FontWeight.BOLD),
                            border=ft.border.all(3, ft.colors.BLUE),
                            padding=5,
                            border_radius=5,
                        ),
                        self.patient_form.main_diagnosis,
                        self.patient_form.sheet_name_dropdown,
                    ]
                ),
                ft.Row(
                    controls=[
                        self.patient_form.goal1,
                    ]
                ),
                self.patient_form.goal2,
                self.patient_form.guidance_items_template,
                self.template_buttons,
            ]
        )

    def save_template(self, session, Template):
        """
        テンプレートを保存する

        Args:
            session: DBセッション
            Template: テンプレートモデルクラス

        Returns:
            bool: 保存が成功したかどうか
            str: メッセージ
        """
        # 入力チェック
        valid, error_message = self.patient_form.check_required_fields()
        if not valid:
            return False, error_message

        # フォームから値を取得
        form_data = self.patient_form.get_patient_data()

        # テンプレートの検索
        template = session.query(Template).filter(
            Template.main_disease == form_data['main_diagnosis'],
            Template.sheet_name == form_data['sheet_name']
        ).first()

        # 既存テンプレートの更新または新規作成
        if template:
            template.goal1 = form_data['goal1']
            template.goal2 = form_data['goal2']
            template.target_bp = form_data['target_bp']
            template.target_hba1c = form_data['target_hba1c']
            template.diet1 = form_data['diet1']
            template.diet2 = form_data['diet2']
            template.diet3 = form_data['diet3']
            template.diet4 = form_data['diet4']
            template.exercise_prescription = form_data['exercise_prescription']
            template.exercise_time = form_data['exercise_time']
            template.exercise_frequency = form_data['exercise_frequency']
            template.exercise_intensity = form_data['exercise_intensity']
            template.daily_activity = form_data['daily_activity']
            template.other1 = form_data['other1']
            template.other2 = form_data['other2']
        else:
            # 新規テンプレートの作成
            template = Template(
                main_disease=form_data['main_diagnosis'],
                sheet_name=form_data['sheet_name'],
                goal1=form_data['goal1'],
                goal2=form_data['goal2'],
                target_bp=form_data['target_bp'],
                target_hba1c=form_data['target_hba1c'],
                diet1=form_data['diet1'],
                diet2=form_data['diet2'],
                diet3=form_data['diet3'],
                diet4=form_data['diet4'],
                exercise_prescription=form_data['exercise_prescription'],
                exercise_time=form_data['exercise_time'],
                exercise_frequency=form_data['exercise_frequency'],
                exercise_intensity=form_data['exercise_intensity'],
                daily_activity=form_data['daily_activity'],
                other1=form_data['other1'],
                other2=form_data['other2']
            )
            session.add(template)

        try:
            session.commit()
            return True, "テンプレートが保存されました"
        except Exception as e:
            session.rollback()
            return False, f"テンプレートの保存に失敗しました: {str(e)}"

    def apply_template(self, session, Template):
        """
        選択された主病名とシート名に基づいてテンプレートを適用する

        Args:
            session: DBセッション
            Template: テンプレートモデルクラス

        Returns:
            bool: テンプレートが適用されたかどうか
        """
        form_data = self.patient_form.get_patient_data()

        try:
            template = session.query(Template).filter(
                Template.main_disease == form_data['main_diagnosis'],
                Template.sheet_name == form_data['sheet_name']
            ).first()

            if template:
                self.patient_form.apply_template(template)
                return True
            return False
        except Exception:
            return False

    def show_snack_bar(self, message: str, duration: int = 1000):
        """
        スナックバーメッセージを表示

        Args:
            message: 表示するメッセージ
            duration: 表示時間（ミリ秒）
        """
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=duration
        )
        snack_bar.open = True
        self.page.overlay.append(snack_bar)
        self.page.update()
