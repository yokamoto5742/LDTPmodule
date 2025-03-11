from datetime import datetime
import flet as ft
from models.patient import PatientInfo
from models.template import MainDisease
from database.repositories.patient_repo import PatientRepository
from database.repositories.template_repo import TemplateRepository
from database.connection import get_session
from ui.components.dialogs import DialogManager

class FormController:
    """
    フォーム入力の制御を担当するコントローラクラス
    """

    def __init__(self, page: ft.Page):
        """
        フォームコントローラの初期化

        Args:
            page (ft.Page): Fletページオブジェクト
        """
        self.page = page
        self.dialog_manager = DialogManager(page)
        self.patient_repo = PatientRepository()
        self.template_repo = TemplateRepository()
        self.selected_row = None

    def validate_required_fields(self, fields_dict):
        """
        必須フィールドの入力チェックを行う

        Args:
            fields_dict (dict): フィールド名とフィールドオブジェクトの辞書

        Returns:
            bool: すべての必須フィールドが入力されている場合はTrue
        """
        # 必須フィールドのリスト
        required_fields = ['main_diagnosis', 'sheet_name']

        # 必須フィールドのチェック
        for field_name in required_fields:
            if field_name in fields_dict and not fields_dict[field_name].value:
                error_message = f"{field_name.replace('_', ' ').title()}を選択してください"
                self.dialog_manager.show_error(error_message)
                return False

        return True

    def apply_template(self, fields_dict):
        """
        選択された主病名とシート名に基づいてテンプレートをフォームに適用する

        Args:
            fields_dict (dict): フィールド名とフィールドオブジェクトの辞書

        Returns:
            bool: テンプレートが適用された場合はTrue
        """
        main_diagnosis = fields_dict.get('main_diagnosis')
        sheet_name = fields_dict.get('sheet_name')

        if not main_diagnosis or not main_diagnosis.value:
            return False

        if not sheet_name or not sheet_name.value:
            return False

        with get_session() as session:
            template = session.query(TemplateRepository().get_template(
                main_diagnosis.value,
                sheet_name.value
            ))

            if not template:
                return False

            # テンプレート値の適用
            field_mappings = [
                ('goal1', 'goal1'),
                ('goal2', 'goal2'),
                ('target_bp', 'target_bp'),
                ('target_hba1c', 'target_hba1c'),
                ('diet1', 'diet1'),
                ('diet2', 'diet2'),
                ('diet3', 'diet3'),
                ('diet4', 'diet4'),
                ('exercise_prescription', 'exercise_prescription'),
                ('exercise_time', 'exercise_time'),
                ('exercise_frequency', 'exercise_frequency'),
                ('exercise_intensity', 'exercise_intensity'),
                ('daily_activity', 'daily_activity'),
                ('other1', 'other1'),
                ('other2', 'other2')
            ]

            for form_field, template_field in field_mappings:
                if form_field in fields_dict and hasattr(template, template_field):
                    fields_dict[form_field].value = getattr(template, template_field)

            return True

    def save_template(self, fields_dict):
        """
        現在のフォーム値をテンプレートとして保存する

        Args:
            fields_dict (dict): フィールド名とフィールドオブジェクトの辞書

        Returns:
            bool: 保存が成功した場合はTrue
        """
        if not self.validate_required_fields(fields_dict):
            return False

        template_data = {
            'main_disease': fields_dict['main_diagnosis'].value,
            'sheet_name': fields_dict['sheet_name'].value,
            'goal1': fields_dict.get('goal1', '').value,
            'goal2': fields_dict.get('goal2', '').value,
            'target_bp': fields_dict.get('target_bp', '').value,
            'target_hba1c': fields_dict.get('target_hba1c', '').value,
            'diet1': fields_dict.get('diet1', '').value,
            'diet2': fields_dict.get('diet2', '').value,
            'diet3': fields_dict.get('diet3', '').value,
            'diet4': fields_dict.get('diet4', '').value,
            'exercise_prescription': fields_dict.get('exercise_prescription', '').value,
            'exercise_time': fields_dict.get('exercise_time', '').value,
            'exercise_frequency': fields_dict.get('exercise_frequency', '').value,
            'exercise_intensity': fields_dict.get('exercise_intensity', '').value,
            'daily_activity': fields_dict.get('daily_activity', '').value,
            'other1': fields_dict.get('other1', '').value,
            'other2': fields_dict.get('other2', '').value
        }

        try:
            template = self.template_repo.save_template(template_data)
            self.dialog_manager.show_message("テンプレートが保存されました")
            return True
        except Exception as e:
            self.dialog_manager.show_error(f"テンプレート保存中にエラーが発生しました: {str(e)}")
            return False

    def save_patient_data(self, fields_dict):
        """
        患者情報を保存する

        Args:
            fields_dict (dict): フィールド名とフィールドオブジェクトの辞書

        Returns:
            bool: 保存が成功した場合はTrue
        """
        if not self.validate_required_fields(fields_dict):
            return False

        if not self.selected_row or 'id' not in self.selected_row:
            return False

        try:
            patient_data = {}

            # 基本情報
            for field_name in ['patient_id', 'patient_name', 'kana', 'gender', 'birthdate',
                               'issue_date', 'doctor_id', 'doctor_name', 'department', 'department_id']:
                if field_name in fields_dict:
                    field_value = fields_dict[field_name].value

                    # 数値フィールドの変換
                    if field_name in ['patient_id', 'doctor_id', 'department_id']:
                        field_value = int(field_value)

                    # 日付フィールドの変換
                    if field_name in ['birthdate', 'issue_date'] and isinstance(field_value, str):
                        field_value = datetime.strptime(field_value, "%Y/%m/%d").date()

                    patient_data[field_name] = field_value

            # 発行日時点の年齢を計算
            if 'birthdate' in patient_data and 'issue_date' in patient_data:
                patient_data['issue_date_age'] = self.patient_repo.calculate_issue_date_age(
                    patient_data['birthdate'], patient_data['issue_date']
                )

            # 診断・計画情報
            for field_name in ['main_diagnosis', 'sheet_name', 'creation_count']:
                if field_name in fields_dict:
                    field_value = fields_dict[field_name].value

                    # 数値フィールドの変換
                    if field_name == 'creation_count':
                        field_value = int(field_value)

                    patient_data[field_name] = field_value

            # 目標情報
            for field_name in ['target_weight', 'target_bp', 'target_hba1c', 'goal1', 'goal2', 'target_achievement']:
                if field_name in fields_dict:
                    field_value = fields_dict[field_name].value

                    # 数値フィールドの変換
                    if field_name == 'target_weight' and field_value:
                        field_value = float(field_value)

                    patient_data[field_name] = field_value

            # 食事・運動情報
            for field_name in ['diet1', 'diet2', 'diet3', 'diet4', 'diet_comment',
                               'exercise_prescription', 'exercise_time', 'exercise_frequency',
                               'exercise_intensity', 'daily_activity', 'exercise_comment']:
                if field_name in fields_dict:
                    patient_data[field_name] = fields_dict[field_name].value

            # チェックボックス情報
            for field_name in ['nonsmoker', 'smoking_cessation', 'ophthalmology', 'dental', 'cancer_screening']:
                if field_name in fields_dict:
                    patient_data[field_name] = fields_dict[field_name].value

            # その他の情報
            for field_name in ['other1', 'other2']:
                if field_name in fields_dict:
                    patient_data[field_name] = fields_dict[field_name].value

            # データを更新
            self.patient_repo.update(self.selected_row['id'], patient_data)

            self.dialog_manager.show_message("データが保存されました")
            return True

        except Exception as e:
            self.dialog_manager.show_error(f"データ保存中にエラーが発生しました: {str(e)}")
            return False

    def create_patient_data(self, fields_dict, df_patients=None):
        """
        新しい患者情報を作成する

        Args:
            fields_dict (dict): フィールド名とフィールドオブジェクトの辞書
            df_patients (pandas.DataFrame, optional): 患者基本情報のDataFrame

        Returns:
            tuple: (成功フラグ, 患者情報オブジェクト)
        """
        if not self.validate_required_fields(fields_dict):
            return False, None

        if not df_patients is not None:
            self.dialog_manager.show_error("患者データが読み込まれていません")
            return False, None

        try:
            p_id = int(fields_dict['patient_id'].value)
            doctor_id = int(fields_dict['doctor_id'].value)
            doctor_name = fields_dict['doctor_name'].value
            department_id = int(fields_dict['department_id'].value)
            department = fields_dict['department'].value

            # 患者基本情報の取得
            patient_info_csv = df_patients.loc[df_patients.iloc[:, 2] == p_id]
            if patient_info_csv.empty:
                self.dialog_manager.show_error(f"患者ID {p_id} が見つかりません。")
                return False, None

            patient_info = patient_info_csv.iloc[0]
            birthdate = patient_info.iloc[6]

            # 発行日の設定
            issue_date = datetime.strptime(fields_dict['issue_date'].value, "%Y/%m/%d").date()

            # 発行日時点の年齢を計算
            issue_date_age = self.patient_repo.calculate_issue_date_age(birthdate, issue_date)

            # PatientInfoオブジェクトの作成
            patient_data = PatientInfo(
                patient_id=p_id,
                patient_name=patient_info.iloc[3],
                kana=patient_info.iloc[4],
                gender="男性" if patient_info.iloc[5] == 1 else "女性",
                birthdate=birthdate,
                issue_date=issue_date,
                issue_date_age=issue_date_age,
                doctor_id=doctor_id,
                doctor_name=doctor_name,
                department=department,
                department_id=department_id,
                main_diagnosis=fields_dict['main_diagnosis'].value,
                sheet_name=fields_dict['sheet_name'].value,
                creation_count=int(fields_dict['creation_count'].value),
                target_weight=float(fields_dict['target_weight'].value) if fields_dict['target_weight'].value else None,
                target_bp=fields_dict['target_bp'].value,
                target_hba1c=fields_dict['target_hba1c'].value,
                goal1=fields_dict['goal1'].value,
                goal2=fields_dict['goal2'].value,
                target_achievement=fields_dict['target_achievement'].value,
                diet1=fields_dict['diet1'].value,
                diet2=fields_dict['diet2'].value,
                diet3=fields_dict['diet3'].value,
                diet4=fields_dict['diet4'].value,
                diet_comment=fields_dict['diet_comment'].value,
                exercise_prescription=fields_dict['exercise_prescription'].value,
                exercise_time=fields_dict['exercise_time'].value,
                exercise_frequency=fields_dict['exercise_frequency'].value,
                exercise_intensity=fields_dict['exercise_intensity'].value,
                daily_activity=fields_dict['daily_activity'].value,
                exercise_comment=fields_dict['exercise_comment'].value,
                nonsmoker=fields_dict['nonsmoker'].value,
                smoking_cessation=fields_dict['smoking_cessation'].value,
                other1=fields_dict['other1'].value,
                other2=fields_dict['other2'].value,
                ophthalmology=fields_dict['ophthalmology'].value,
                dental=fields_dict['dental'].value,
                cancer_screening=fields_dict['cancer_screening'].value
            )

            return True, patient_data

        except Exception as e:
            self.dialog_manager.show_error(f"データ作成中にエラーが発生しました: {str(e)}")
            return False, None

    def copy_latest_plan(self, patient_id, df_patients):
        """
        最新の治療計画をコピーして新しい計画を作成する

        Args:
            patient_id (int): 患者ID
            df_patients (pandas.DataFrame): 患者基本情報のDataFrame

        Returns:
            tuple: (成功フラグ, 新しい患者情報ID)
        """
        try:
            # 患者基本情報の取得
            patient_csv_info = df_patients[df_patients.iloc[:, 2] == int(patient_id)]
            if patient_csv_info.empty:
                self.dialog_manager.show_error(f"患者ID {patient_id} が見つかりません。")
                return False, None

            patient_csv_info = patient_csv_info.iloc[0]

            # 最新の計画をコピー
            new_patient_info = self.patient_repo.copy_latest_plan(int(patient_id), patient_csv_info)

            if new_patient_info:
                self.dialog_manager.show_message("前回の計画内容をコピーしました")
                return True, new_patient_info.id
            else:
                self.dialog_manager.show_error("コピーする計画が見つかりませんでした")
                return False, None

        except Exception as e:
            self.dialog_manager.show_error(f"計画コピー中にエラーが発生しました: {str(e)}")
            return False, None

    def load_form_data(self, fields_dict):
        """
        選択された行のデータをフォームに読み込む

        Args:
            fields_dict (dict): フィールド名とフィールドオブジェクトの辞書

        Returns:
            bool: 読み込みが成功した場合はTrue
        """
        if not self.selected_row or 'id' not in self.selected_row:
            return False

        try:
            with get_session() as session:
                patient_info = session.query(PatientInfo).filter(PatientInfo.id == self.selected_row['id']).first()

                if not patient_info:
                    return False

                # 基本情報
                if 'patient_id' in fields_dict:
                    fields_dict['patient_id'].value = str(patient_info.patient_id)

                if 'issue_date' in fields_dict:
                    fields_dict['issue_date'].value = patient_info.issue_date.strftime(
                        "%Y/%m/%d") if patient_info.issue_date else ""

                if 'patient_name' in fields_dict:
                    fields_dict['patient_name'].value = patient_info.patient_name

                if 'kana' in fields_dict:
                    fields_dict['kana'].value = patient_info.kana

                if 'gender' in fields_dict:
                    fields_dict['gender'].value = patient_info.gender

                if 'birthdate' in fields_dict:
                    fields_dict['birthdate'].value = patient_info.birthdate.strftime(
                        "%Y/%m/%d") if patient_info.birthdate else ""

                if 'doctor_id' in fields_dict:
                    fields_dict['doctor_id'].value = str(patient_info.doctor_id)

                if 'doctor_name' in fields_dict:
                    fields_dict['doctor_name'].value = patient_info.doctor_name

                if 'department' in fields_dict:
                    fields_dict['department'].value = patient_info.department

                if 'department_id' in fields_dict:
                    fields_dict['department_id'].value = str(patient_info.department_id)

                # 主病名とシート名
                if 'main_diagnosis' in fields_dict:
                    fields_dict['main_diagnosis'].value = patient_info.main_diagnosis

                    # 主病名に応じたシート名オプションを更新
                    if 'sheet_name' in fields_dict and patient_info.main_diagnosis:
                        main_disease = session.query(MainDisease).filter_by(name=patient_info.main_diagnosis).first()
                        if main_disease:
                            fields_dict['sheet_name'].options = self.template_repo.get_dropdown_options_for_sheet_names(
                                main_disease.id)
                        else:
                            fields_dict[
                                'sheet_name'].options = self.template_repo.get_dropdown_options_for_sheet_names()

                if 'sheet_name' in fields_dict:
                    fields_dict['sheet_name'].value = patient_info.sheet_name

                if 'creation_count' in fields_dict:
                    fields_dict['creation_count'].value = str(patient_info.creation_count)

                # 目標情報
                if 'target_weight' in fields_dict:
                    fields_dict['target_weight'].value = str(
                        patient_info.target_weight) if patient_info.target_weight else ""

                if 'target_bp' in fields_dict:
                    fields_dict['target_bp'].value = patient_info.target_bp

                if 'target_hba1c' in fields_dict:
                    fields_dict['target_hba1c'].value = patient_info.target_hba1c

                if 'goal1' in fields_dict:
                    fields_dict['goal1'].value = patient_info.goal1

                if 'goal2' in fields_dict:
                    fields_dict['goal2'].value = patient_info.goal2

                if 'target_achievement' in fields_dict:
                    fields_dict['target_achievement'].value = patient_info.target_achievement

                # 食事・運動情報
                for field_name in ['diet1', 'diet2', 'diet3', 'diet4', 'diet_comment',
                                   'exercise_prescription', 'exercise_time', 'exercise_frequency',
                                   'exercise_intensity', 'daily_activity', 'exercise_comment']:
                    if field_name in fields_dict:
                        fields_dict[field_name].value = getattr(patient_info, field_name)

                # チェックボックス情報
                for field_name in ['nonsmoker', 'smoking_cessation', 'ophthalmology', 'dental', 'cancer_screening']:
                    if field_name in fields_dict:
                        fields_dict[field_name].value = getattr(patient_info, field_name)

                # その他の情報
                if 'other1' in fields_dict:
                    fields_dict['other1'].value = patient_info.other1

                if 'other2' in fields_dict:
                    fields_dict['other2'].value = patient_info.other2

                return True

        except Exception as e:
            self.dialog_manager.show_error(f"データ読み込み中にエラーが発生しました: {str(e)}")
            return False

    def clear_form(self, fields_dict):
        """
        フォームの値をクリアする

        Args:
            fields_dict (dict): フィールド名とフィールドオブジェクトの辞書
        """
        # テキストフィールドのクリア
        text_fields = [
            'target_weight', 'target_bp', 'target_hba1c', 'goal1', 'goal2',
            'diet_comment', 'exercise_comment', 'other1', 'other2'
        ]

        for field_name in text_fields:
            if field_name in fields_dict:
                fields_dict[field_name].value = ""

        # ドロップダウンのクリア
        dropdown_fields = [
            'target_achievement', 'diet1', 'diet2', 'diet3', 'diet4',
            'exercise_prescription', 'exercise_time', 'exercise_frequency',
            'exercise_intensity', 'daily_activity', 'main_diagnosis', 'sheet_name'
        ]

        for field_name in dropdown_fields:
            if field_name in fields_dict:
                fields_dict[field_name].value = ""

        # チェックボックスのクリア
        checkbox_fields = [
            'nonsmoker', 'smoking_cessation', 'ophthalmology', 'dental', 'cancer_screening'
        ]

        for field_name in checkbox_fields:
            if field_name in fields_dict:
                fields_dict[field_name].value = False

        # 作成回数を1に初期化
        if 'creation_count' in fields_dict:
            fields_dict['creation_count'].value = "1"

        # 発行日を現在の日付で初期化
        if 'issue_date' in fields_dict:
            fields_dict['issue_date'].value = datetime.now().date().strftime("%Y/%m/%d")
