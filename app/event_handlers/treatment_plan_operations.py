from datetime import datetime

from database import get_session_factory
from models import PatientInfo
from services.treatment_plan_service import TreatmentPlanGenerator
from utils.date_utils import calculate_issue_date_age

Session = get_session_factory()


class TreatmentPlanOperationsMixin:
    """計画書操作を提供するMixin"""

    def create_new_plan_and_print(self, e):
        """新規登録して印刷ハンドラ"""
        if not self.dialog_manager.check_required_fields():
            return

        fields = self.fields
        p_id = fields['patient_id'].value
        doctor_id = fields['doctor_id_value'].value
        doctor_name = fields['doctor_name_value'].value
        department_id = fields['department_id_value'].value
        department = fields['department_value'].value

        self.create_treatment_plan(int(p_id), int(doctor_id), doctor_name,
                                  department, int(department_id), self.df_patients)

        if self.route_manager:
            self.route_manager.open_route(e)

    def save_new_plan(self, e):
        """新規登録ハンドラ"""
        if not self.dialog_manager.check_required_fields():
            return

        fields = self.fields
        p_id = fields['patient_id'].value
        doctor_id = fields['doctor_id_value'].value
        doctor_name = fields['doctor_name_value'].value
        department_id = fields['department_id_value'].value
        department = fields['department_value'].value

        self.save_treatment_plan(int(p_id), int(doctor_id), doctor_name,
                                department, int(department_id), self.df_patients)

        if self.route_manager:
            self.route_manager.open_route(e)

    def create_treatment_plan_object(self, p_id, doctor_id, doctor_name, department, department_id, patients_df):
        """生活習慣病計画書オブジェクトを作成"""
        patient_info_csv = patients_df.loc[patients_df.iloc[:, 2] == p_id]
        if patient_info_csv.empty:
            raise ValueError(f"患者ID {p_id} が見つかりません。")

        patient_info = patient_info_csv.iloc[0]
        birthdate = patient_info.iloc[6]
        issue_date = datetime.strptime(self.fields['issue_date_value'].value, "%Y/%m/%d").date()
        issue_date_age = calculate_issue_date_age(birthdate, issue_date)

        fields = self.fields
        return PatientInfo(
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
            main_diagnosis=fields['main_diagnosis'].value,
            sheet_name=fields['sheet_name_dropdown'].value,
            creation_count=int(fields['creation_count'].value),
            target_weight=float(fields['target_weight'].value) if fields['target_weight'].value else None,
            target_bp=fields['target_bp'].value,
            target_hba1c=fields['target_hba1c'].value,
            goal1=fields['goal1'].value,
            goal2=fields['goal2'].value,
            target_achievement=fields['target_achievement'].value,
            diet1=fields['diet1'].value,
            diet2=fields['diet2'].value,
            diet3=fields['diet3'].value,
            diet4=fields['diet4'].value,
            diet_comment=fields['diet_comment'].value,
            exercise_prescription=fields['exercise_prescription'].value,
            exercise_time=fields['exercise_time'].value,
            exercise_frequency=fields['exercise_frequency'].value,
            exercise_intensity=fields['exercise_intensity'].value,
            daily_activity=fields['daily_activity'].value,
            exercise_comment=fields['exercise_comment'].value,
            nonsmoker=fields['nonsmoker'].value,
            smoking_cessation=fields['smoking_cessation'].value,
            other1=fields['other1'].value,
            other2=fields['other2'].value,
            ophthalmology=fields['ophthalmology'].value,
            dental=fields['dental'].value,
            cancer_screening=fields['cancer_screening'].value
        )

    def create_treatment_plan(self, p_id, doctor_id, doctor_name, department, department_id, patients_df):
        """計画書を作成"""
        try:
            patient_info = self.create_treatment_plan_object(
                p_id, doctor_id, doctor_name, department, department_id, patients_df)
            TreatmentPlanGenerator.generate_plan(patient_info, "LDTPform")
        except ValueError as ve:
            self.dialog_manager.show_error_message(str(ve))

    def save_treatment_plan(self, p_id, doctor_id, doctor_name, department, department_id, patients_df):
        """計画書を保存"""
        try:
            patient_info = self.create_treatment_plan_object(
                p_id, doctor_id, doctor_name, department, department_id, patients_df)

            # データベースに保存
            session = Session()
            session.add(patient_info)
            session.commit()
            session.close()

            self.dialog_manager.show_info_message("データが保存されました")
            self.update_history(p_id)
        except ValueError as ve:
            self.dialog_manager.show_error_message(str(ve))
