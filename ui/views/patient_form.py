import flet as ft
from datetime import datetime
from typing import Callable, Dict, Any, Optional


class PatientForm:
    """患者情報フォームを管理するクラス"""

    def __init__(self, page: ft.Page, input_height: int, text_height: int, dropdown_items):
        """
        PatientFormクラスの初期化

        Args:
            page: Fletページオブジェクト
            input_height: 入力フィールドの高さ
            text_height: テキストの高さ
            dropdown_items: ドロップダウンアイテムの管理クラス
        """
        self.page = page
        self.input_height = input_height
        self.text_height = text_height
        self.dropdown_items = dropdown_items

        # UI部品の初期化 - 正しい順序で呼び出す
        self._init_basic_info_fields()
        self._init_diagnosis_fields()
        self._init_goal_fields()
        self._init_diet_exercise_fields()  # ここからself._setup_focus_handlers()の呼び出しを削除
        self._init_other_fields()
        self._init_date_picker()

        # 全てのフィールドが初期化された後にfocus handlersをセットアップ
        self._setup_focus_handlers()

        # フォームレイアウトの作成
        self.guidance_items = self._create_guidance_items()
        self.guidance_items_template = self._create_guidance_items_template()

    def _init_basic_info_fields(self):
        """基本情報フィールドの初期化"""
        self.patient_id = ft.TextField(label="患者ID", width=150, height=self.input_height)
        self.issue_date_value = ft.TextField(label="発行日", width=150, read_only=True, height=self.input_height)
        self.name_value = ft.TextField(label="氏名", read_only=True, width=150, height=self.input_height)
        self.kana_value = ft.TextField(label="カナ", read_only=True, width=150, height=self.input_height)
        self.gender_value = ft.TextField(label="性別", read_only=True, width=150, height=self.input_height)
        self.birthdate_value = ft.TextField(label="生年月日", read_only=True, width=150, height=self.input_height)
        self.doctor_id_value = ft.TextField(label="医師ID", read_only=True, width=150, height=self.input_height)
        self.doctor_name_value = ft.TextField(label="医師名", read_only=True, width=150, height=self.input_height)
        self.department_id_value = ft.TextField(label="診療科ID", read_only=True, width=150, height=self.input_height)
        self.department_value = ft.TextField(label="診療科", read_only=True, width=150, height=self.input_height)

    def _init_diagnosis_fields(self):
        """診断関連フィールドの初期化"""
        self.main_diagnosis = ft.Dropdown(
            label="主病名",
            width=200,
            text_size=13,
            autofocus=True,
            height=self.input_height
        )

        self.sheet_name_dropdown = ft.Dropdown(
            label="シート名",
            width=300,
            text_size=13,
            height=self.input_height
        )

        self.creation_count = ft.TextField(
            label="作成回数",
            width=100,
            value="1",
            text_size=13,
            height=self.input_height
        )

    def _init_goal_fields(self):
        """目標関連フィールドの初期化"""
        self.target_weight = ft.TextField(label="目標体重", width=150, value="", text_size=13, height=self.input_height)
        self.target_bp = ft.TextField(label="目標血圧", width=150, text_size=13, height=self.input_height)
        self.target_hba1c = ft.TextField(label="目標HbA1c", width=150, text_size=13, height=self.input_height)

        self.goal1 = ft.TextField(
            label="①達成目標：患者と相談した目標",
            width=800,
            value="主病名とシート名を選択してください",
            text_size=13,
            height=self.text_height
        )

        self.goal2 = ft.TextField(
            label="②行動目標：患者と相談した目標",
            width=800,
            text_size=13,
            height=self.text_height
        )

    def _init_diet_exercise_fields(self):
        """食事と運動関連フィールドの初期化"""
        # ドロップダウンフィールドの初期化
        self.target_achievement = self.dropdown_items.create_dropdown('target_achievement', "目標達成状況(2回目以降)",
                                                                      400)
        self.diet1 = self.dropdown_items.create_dropdown('diet', "食事1", 400)
        self.diet2 = self.dropdown_items.create_dropdown('diet', "食事2", 400)
        self.diet3 = self.dropdown_items.create_dropdown('diet', "食事3", 400)
        self.diet4 = self.dropdown_items.create_dropdown('diet', "食事4", 400)
        self.exercise_prescription = self.dropdown_items.create_dropdown('exercise_prescription', "運動処方", 200)
        self.exercise_time = self.dropdown_items.create_dropdown('exercise_time', "時間", 200)
        self.exercise_frequency = self.dropdown_items.create_dropdown('exercise_frequency', "頻度", 200)
        self.exercise_intensity = self.dropdown_items.create_dropdown('exercise_intensity', "強度", 200)
        self.daily_activity = self.dropdown_items.create_dropdown('daily_activity', "日常生活の活動量", 300)

        # 高さの設定
        for dropdown in [self.target_achievement, self.diet1, self.diet2, self.diet3, self.diet4,
                         self.exercise_prescription, self.exercise_time, self.exercise_frequency,
                         self.exercise_intensity, self.daily_activity]:
            dropdown.height = self.input_height

        # コメントフィールド
        import flet as ft
        self.diet_comment = ft.TextField(
            label="食事フリーコメント",
            width=800,
            text_style=ft.TextStyle(size=13),
            height=self.text_height
        )

        self.exercise_comment = ft.TextField(
            label="運動フリーコメント",
            width=800,
            text_style=ft.TextStyle(size=13),
            height=self.text_height
        )

    def _init_other_fields(self):
        """その他のフィールドの初期化"""
        self.nonsmoker = ft.Checkbox(label="非喫煙者である", on_change=self._on_tobacco_checkbox_change,
                                     height=self.text_height)
        self.smoking_cessation = ft.Checkbox(
            label="禁煙の実施方法等を指示",
            on_change=self._on_tobacco_checkbox_change,
            height=self.text_height
        )

        self.other1 = ft.TextField(
            label="その他1",
            value="",
            width=400,
            text_size=13,
            height=self.text_height
        )

        self.other2 = ft.TextField(label="その他2", value="", width=400, text_size=13, height=self.text_height)

        self.ophthalmology = ft.Checkbox(label="眼科", height=self.text_height)
        self.dental = ft.Checkbox(label="歯科", height=self.text_height)
        self.cancer_screening = ft.Checkbox(label="がん検診", height=self.text_height)

    def _init_date_picker(self):
        """日付選択ピッカーの初期化"""
        self.issue_date_picker = ft.DatePicker(
            on_change=self._on_issue_date_change,
            on_dismiss=self._on_date_picker_dismiss
        )

        self.issue_date_button = ft.ElevatedButton(
            "日付選択",
            icon=ft.icons.CALENDAR_TODAY,
            on_click=self._open_date_picker,
        )

        self.issue_date_row = ft.Row([self.issue_date_value, self.issue_date_button])

    def _setup_focus_handlers(self):
        """フォーカス移動のハンドラを設定"""

        def create_focus_handler(next_field):
            return lambda _: next_field.focus()

        self.target_achievement.on_change = create_focus_handler(self.diet1)
        self.diet1.on_change = create_focus_handler(self.diet2)
        self.diet2.on_change = create_focus_handler(self.diet3)
        self.diet3.on_change = create_focus_handler(self.diet4)
        self.diet4.on_change = create_focus_handler(self.exercise_prescription)
        self.exercise_prescription.on_change = create_focus_handler(self.exercise_time)
        self.exercise_time.on_change = create_focus_handler(self.exercise_frequency)
        self.exercise_frequency.on_change = create_focus_handler(self.exercise_intensity)
        self.exercise_intensity.on_change = create_focus_handler(self.daily_activity)

        # submit ハンドラーも設定
        self.creation_count.on_submit = lambda _: self.goal1.focus()
        self.goal1.on_submit = lambda _: self.target_weight.focus()
        self.goal2.on_submit = lambda _: self.exercise_frequency.focus()
        self.diet_comment.on_submit = lambda _: self.exercise_comment.focus()
        self.exercise_comment.on_submit = lambda _: self.other1.focus()
        self.other1.on_submit = lambda _: self.other2.focus()

    def _create_guidance_items(self):
        """ガイダンス項目のレイアウトを作成"""
        return ft.Column([
            ft.Row([self.target_achievement,
                    self.target_weight, ft.Text("kg", size=13),
                    self.target_bp, ft.Text("mmHg", size=13),
                    self.target_hba1c, ft.Text("%", size=13), ]),
            ft.Row([self.diet1, self.diet2]),
            ft.Row([self.diet3, self.diet4]),
            ft.Row([self.diet_comment]),
            ft.Row([self.exercise_prescription, self.exercise_time, self.exercise_frequency,
                    self.exercise_intensity, self.daily_activity, ]),
            ft.Row([self.exercise_comment]),
            ft.Row([ft.Text("たばこ", size=14), self.nonsmoker, self.smoking_cessation,
                    ft.Text("    (チェックボックスを2回選ぶと解除できます)", size=12)]),
            ft.Row([self.other1, self.other2]),
            ft.Row([ft.Text("受診勧奨", size=14), self.ophthalmology, self.dental, self.cancer_screening]),
        ])

    def _create_guidance_items_template(self):
        """テンプレート用のガイダンス項目レイアウトを作成"""
        return ft.Column([
            ft.Row([self.target_bp, ft.Text("mmHg", size=13),
                    self.target_hba1c, ft.Text("%", size=13), ]),
            ft.Row([self.diet1, self.diet2]),
            ft.Row([self.diet3, self.diet4]),
            ft.Row([self.exercise_prescription, self.exercise_time, self.exercise_frequency,
                    self.exercise_intensity, self.daily_activity]),
            ft.Row([self.other1, self.other2]),
        ])

    def _on_tobacco_checkbox_change(self, e):
        """喫煙関連チェックボックスの変更ハンドラ"""
        if e.control == self.nonsmoker and self.nonsmoker.value:
            self.smoking_cessation.value = False
            self.smoking_cessation.update()
        elif e.control == self.smoking_cessation and self.smoking_cessation.value:
            self.nonsmoker.value = False
            self.nonsmoker.update()

    def _on_issue_date_change(self, e):
        """発行日の変更ハンドラ"""
        if self.issue_date_picker.value:
            self.issue_date_value.value = self.issue_date_picker.value.strftime("%Y/%m/%d")
            self.page.update()

    def _on_date_picker_dismiss(self, e):
        """日付ピッカーの閉じるハンドラ"""
        if self.issue_date_picker.value:
            self.issue_date_value.value = self.issue_date_picker.value.strftime("%Y/%m/%d")
        self.page.overlay.remove(self.issue_date_picker)
        self.page.update()

    def _open_date_picker(self, e):
        """日付ピッカーを開くハンドラ"""
        if self.issue_date_picker not in self.page.overlay:
            self.page.overlay.append(self.issue_date_picker)
        self.issue_date_picker.open = True
        self.page.update()

    def load_patient_info(self, patient_id_arg, df_patients, format_date_func):
        """
        患者情報を読み込む

        Args:
            patient_id_arg: 患者ID
            df_patients: 患者情報データフレーム
            format_date_func: 日付フォーマット関数
        """
        patient_info = df_patients[df_patients.iloc[:, 2] == patient_id_arg]
        if not patient_info.empty:
            patient_info = patient_info.iloc[0]
            self.patient_id.value = str(patient_id_arg)
            self.issue_date_value.value = datetime.now().date().strftime("%Y/%m/%d")
            self.name_value.value = patient_info.iloc[3]
            self.kana_value.value = patient_info.iloc[4]
            self.gender_value.value = "男性" if patient_info.iloc[5] == 1 else "女性"
            birthdate = patient_info.iloc[6]
            self.birthdate_value.value = format_date_func(birthdate)
            self.doctor_id_value.value = str(patient_info.iloc[9])
            self.doctor_name_value.value = patient_info.iloc[10]
            self.department_value.value = patient_info.iloc[14]
            self.department_id_value.value = str(patient_info.iloc[13])
        else:
            # patient_infoが空の場合は空文字列を設定
            self.issue_date_value.value = ""
            self.name_value.value = ""
            self.kana_value.value = ""
            self.gender_value.value = ""
            self.birthdate_value.value = ""
            self.doctor_id_value.value = ""
            self.doctor_name_value.value = ""
            self.department_value.value = ""
        self.page.update()

    def update_form_with_selected_data(self, patient_info):
        """
        選択された患者情報でフォームを更新する

        Args:
            patient_info: 患者情報オブジェクト
        """
        self.patient_id.value = str(patient_info.patient_id)
        self.issue_date_value.value = patient_info.issue_date.strftime("%Y/%m/%d") if patient_info.issue_date else ""
        self.name_value.value = patient_info.patient_name
        self.kana_value.value = patient_info.kana
        self.gender_value.value = patient_info.gender
        self.birthdate_value.value = patient_info.birthdate.strftime("%Y/%m/%d") if patient_info.birthdate else ""
        self.doctor_id_value.value = str(patient_info.doctor_id)
        self.doctor_name_value.value = patient_info.doctor_name
        self.department_value.value = patient_info.department
        self.department_id_value.value = str(patient_info.department_id)
        self.main_diagnosis.value = patient_info.main_diagnosis
        self.sheet_name_dropdown.value = patient_info.sheet_name
        self.creation_count.value = str(patient_info.creation_count)
        self.target_weight.value = str(patient_info.target_weight) if patient_info.target_weight else ""
        self.target_bp.value = patient_info.target_bp
        self.target_hba1c.value = patient_info.target_hba1c
        self.goal1.value = patient_info.goal1
        self.goal2.value = patient_info.goal2
        self.target_achievement.value = patient_info.target_achievement
        self.diet1.value = patient_info.diet1
        self.diet2.value = patient_info.diet2
        self.diet3.value = patient_info.diet3
        self.diet4.value = patient_info.diet4
        self.diet_comment.value = patient_info.diet_comment
        self.exercise_prescription.value = patient_info.exercise_prescription
        self.exercise_time.value = patient_info.exercise_time
        self.exercise_frequency.value = patient_info.exercise_frequency
        self.exercise_intensity.value = patient_info.exercise_intensity
        self.daily_activity.value = patient_info.daily_activity
        self.exercise_comment.value = patient_info.exercise_comment
        self.nonsmoker.value = patient_info.nonsmoker
        self.smoking_cessation.value = patient_info.smoking_cessation
        self.other1.value = patient_info.other1
        self.other2.value = patient_info.other2
        self.ophthalmology.value = patient_info.ophthalmology
        self.dental.value = patient_info.dental
        self.cancer_screening.value = patient_info.cancer_screening
        self.page.update()

    def clear_form(self):
        """フォームをクリアする"""
        for field in [self.target_weight, self.target_bp, self.target_hba1c, self.goal1, self.goal2,
                      self.target_achievement, self.diet1, self.diet2, self.diet3, self.diet4,
                      self.diet_comment, self.exercise_prescription, self.exercise_time,
                      self.exercise_frequency, self.exercise_intensity, self.daily_activity,
                      self.exercise_comment, self.other1, self.other2, self.issue_date_value]:
            field.value = ""

        self.main_diagnosis.value = ""
        self.sheet_name_dropdown.value = ""
        self.creation_count.value = "1"
        self.nonsmoker.value = False
        self.smoking_cessation.value = False
        self.ophthalmology.value = False
        self.dental.value = False
        self.cancer_screening.value = False

        # 発行日を現在の日付で初期化
        current_date = datetime.now().date()
        self.issue_date_value.value = current_date.strftime("%Y/%m/%d")
        self.issue_date_picker.value = current_date

        self.page.update()

    def apply_template(self, template):
        """
        テンプレートの内容をフォームに適用する

        Args:
            template: 適用するテンプレートオブジェクト
        """
        if template:
            self.goal1.value = template.goal1
            self.goal2.value = template.goal2
            self.target_bp.value = template.target_bp
            self.target_hba1c.value = template.target_hba1c
            self.diet1.value = template.diet1
            self.diet2.value = template.diet2
            self.diet3.value = template.diet3
            self.diet4.value = template.diet4
            self.exercise_prescription.value = template.exercise_prescription
            self.exercise_time.value = template.exercise_time
            self.exercise_frequency.value = template.exercise_frequency
            self.exercise_intensity.value = template.exercise_intensity
            self.daily_activity.value = template.daily_activity
            self.other1.value = template.other1
            self.other2.value = template.other2
        self.page.update()

    def get_patient_data(self):
        """
        フォームから患者データを取得する

        Returns:
            dict: 患者データの辞書
        """
        return {
            'patient_id': self.patient_id.value,
            'patient_name': self.name_value.value,
            'kana': self.kana_value.value,
            'gender': self.gender_value.value,
            'birthdate': self.birthdate_value.value,
            'issue_date': self.issue_date_value.value,
            'doctor_id': self.doctor_id_value.value,
            'doctor_name': self.doctor_name_value.value,
            'department': self.department_value.value,
            'department_id': self.department_id_value.value,
            'main_diagnosis': self.main_diagnosis.value,
            'sheet_name': self.sheet_name_dropdown.value,
            'creation_count': self.creation_count.value,
            'target_weight': self.target_weight.value,
            'target_bp': self.target_bp.value,
            'target_hba1c': self.target_hba1c.value,
            'goal1': self.goal1.value,
            'goal2': self.goal2.value,
            'target_achievement': self.target_achievement.value,
            'diet1': self.diet1.value,
            'diet2': self.diet2.value,
            'diet3': self.diet3.value,
            'diet4': self.diet4.value,
            'diet_comment': self.diet_comment.value,
            'exercise_prescription': self.exercise_prescription.value,
            'exercise_time': self.exercise_time.value,
            'exercise_frequency': self.exercise_frequency.value,
            'exercise_intensity': self.exercise_intensity.value,
            'daily_activity': self.daily_activity.value,
            'exercise_comment': self.exercise_comment.value,
            'nonsmoker': self.nonsmoker.value,
            'smoking_cessation': self.smoking_cessation.value,
            'other1': self.other1.value,
            'other2': self.other2.value,
            'ophthalmology': self.ophthalmology.value,
            'dental': self.dental.value,
            'cancer_screening': self.cancer_screening.value,
        }

    def setup_patient_id_change_handler(self, handler):
        """患者ID変更ハンドラの設定"""
        self.patient_id.on_change = handler

    def setup_main_diagnosis_change_handler(self, handler):
        """主病名変更ハンドラの設定"""
        self.main_diagnosis.on_change = handler

    def setup_sheet_name_change_handler(self, handler):
        """シート名変更ハンドラの設定"""
        self.sheet_name_dropdown.on_change = handler

    def update_main_diagnosis_options(self, options):
        """主病名オプションの更新"""
        self.main_diagnosis.options = options
        self.page.update()

    def update_sheet_name_options(self, options):
        """シート名オプションの更新"""
        self.sheet_name_dropdown.options = options
        self.page.update()

    def check_required_fields(self) -> tuple[bool, Optional[str]]:
        """
        必須フィールドが入力されているかチェックする

        Returns:
            bool: 全ての必須フィールドが入力されているか
            str: エラーメッセージ (問題がなければNone)
        """
        if not self.main_diagnosis.value:
            return False, "主病名を選択してください"
        if not self.sheet_name_dropdown.value:
            return False, "シート名を選択してください"
        return True, None
