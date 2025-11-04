from datetime import datetime

from database import get_session_factory
from models import MainDisease
from services.patient_service import load_main_diseases, load_sheet_names
from utils.date_utils import calculate_issue_date_age
from utils.file_utils import format_date

Session = get_session_factory()


class FormOperationsMixin:
    """フォーム操作を提供するMixin"""

    def _populate_form_from_patient_info(self, patient_info, session):
        """患者情報から登録フォームを設定"""
        fields = self.fields

        fields['patient_id'].value = patient_info.patient_id
        fields['issue_date_value'].value = patient_info.issue_date.strftime(
            "%Y/%m/%d") if patient_info.issue_date else ""

        # 主病名の更新
        fields['main_diagnosis'].options = load_main_diseases()
        fields['main_diagnosis'].value = patient_info.main_diagnosis

        # シート名の更新
        main_disease = session.query(MainDisease).filter_by(name=patient_info.main_diagnosis).first()
        if main_disease:
            fields['sheet_name_dropdown'].options = load_sheet_names(main_disease.id)
        else:
            fields['sheet_name_dropdown'].options = load_sheet_names()
        fields['sheet_name_dropdown'].value = patient_info.sheet_name

        # 各フィールドの更新
        fields['creation_count'].value = patient_info.creation_count
        fields['target_weight'].value = patient_info.target_weight
        fields['target_bp'].value = patient_info.target_bp
        fields['target_hba1c'].value = patient_info.target_hba1c
        fields['goal1'].value = patient_info.goal1
        fields['goal2'].value = patient_info.goal2
        fields['target_achievement'].value = patient_info.target_achievement
        fields['diet1'].value = patient_info.diet1
        fields['diet2'].value = patient_info.diet2
        fields['diet3'].value = patient_info.diet3
        fields['diet4'].value = patient_info.diet4
        fields['diet_comment'].value = patient_info.diet_comment
        fields['exercise_prescription'].value = patient_info.exercise_prescription
        fields['exercise_time'].value = patient_info.exercise_time
        fields['exercise_frequency'].value = patient_info.exercise_frequency
        fields['exercise_intensity'].value = patient_info.exercise_intensity
        fields['daily_activity'].value = patient_info.daily_activity
        fields['exercise_comment'].value = patient_info.exercise_comment
        fields['nonsmoker'].value = patient_info.nonsmoker
        fields['smoking_cessation'].value = patient_info.smoking_cessation
        fields['other1'].value = patient_info.other1
        fields['other2'].value = patient_info.other2
        fields['ophthalmology'].value = patient_info.ophthalmology
        fields['dental'].value = patient_info.dental
        fields['cancer_screening'].value = patient_info.cancer_screening

    def _update_patient_info_from_form(self, patient_info, include_basic_info=False):
        """登録フォームから患者情報を更新"""
        fields = self.fields

        if include_basic_info:
            patient_info.patient_id = int(fields['patient_id'].value)
            patient_info.patient_name = fields['name_value'].value
            patient_info.kana = fields['kana_value'].value
            patient_info.gender = fields['gender_value'].value
            patient_info.birthdate = datetime.strptime(fields['birthdate_value'].value, "%Y/%m/%d").date()
            patient_info.doctor_id = int(fields['doctor_id_value'].value)
            patient_info.doctor_name = fields['doctor_name_value'].value
            patient_info.department = fields['department_value'].value
            patient_info.department_id = int(fields['department_id_value'].value)

        patient_info.main_diagnosis = fields['main_diagnosis'].value
        patient_info.sheet_name = fields['sheet_name_dropdown'].value
        patient_info.creation_count = int(fields['creation_count'].value)
        patient_info.issue_date = datetime.strptime(fields['issue_date_value'].value, "%Y/%m/%d").date()
        patient_info.issue_date_age = calculate_issue_date_age(patient_info.birthdate, patient_info.issue_date)
        patient_info.target_weight = float(fields['target_weight'].value) if fields['target_weight'].value else None
        patient_info.target_bp = fields['target_bp'].value
        patient_info.target_hba1c = fields['target_hba1c'].value
        patient_info.goal1 = fields['goal1'].value
        patient_info.goal2 = fields['goal2'].value
        patient_info.target_achievement = fields['target_achievement'].value
        patient_info.diet1 = fields['diet1'].value
        patient_info.diet2 = fields['diet2'].value
        patient_info.diet3 = fields['diet3'].value
        patient_info.diet4 = fields['diet4'].value
        patient_info.diet_comment = fields['diet_comment'].value
        patient_info.exercise_prescription = fields['exercise_prescription'].value
        patient_info.exercise_time = fields['exercise_time'].value
        patient_info.exercise_frequency = fields['exercise_frequency'].value
        patient_info.exercise_intensity = fields['exercise_intensity'].value
        patient_info.daily_activity = fields['daily_activity'].value
        patient_info.exercise_comment = fields['exercise_comment'].value
        patient_info.nonsmoker = fields['nonsmoker'].value
        patient_info.smoking_cessation = fields['smoking_cessation'].value
        patient_info.other1 = fields['other1'].value
        patient_info.other2 = fields['other2'].value
        patient_info.ophthalmology = fields['ophthalmology'].value
        patient_info.dental = fields['dental'].value
        patient_info.cancer_screening = fields['cancer_screening'].value

    def load_patient_info(self, patient_id_arg):
        """患者情報を読み込む"""
        fields = self.fields
        patient_info = self.df_patients[self.df_patients.iloc[:, 2] == patient_id_arg]

        if not patient_info.empty:
            patient_info = patient_info.iloc[0]
            fields['patient_id'].value = str(patient_id_arg)
            fields['issue_date_value'].value = datetime.now().date().strftime("%Y/%m/%d")
            fields['name_value'].value = patient_info.iloc[3]
            fields['kana_value'].value = patient_info.iloc[4]
            fields['gender_value'].value = "男性" if patient_info.iloc[5] == 1 else "女性"
            birthdate = patient_info.iloc[6]
            fields['birthdate_value'].value = format_date(birthdate)
            fields['doctor_id_value'].value = str(patient_info.iloc[9])
            fields['doctor_name_value'].value = patient_info.iloc[10]
            fields['department_value'].value = patient_info.iloc[14]
            fields['department_id_value'].value = str(patient_info.iloc[13])
        else:
            # patient_infoが空の場合は空文字列を設定
            fields['issue_date_value'].value = ""
            fields['name_value'].value = ""
            fields['kana_value'].value = ""
            fields['gender_value'].value = ""
            fields['birthdate_value'].value = ""
            fields['doctor_id_value'].value = ""
            fields['doctor_name_value'].value = ""
            fields['department_value'].value = ""

        self.page.update()
