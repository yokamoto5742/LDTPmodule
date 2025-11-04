from datetime import datetime

from database import get_session_factory
from models import PatientInfo
from services.patient_service import load_patient_data
from services.treatment_plan_service import TreatmentPlanGenerator
from utils.date_utils import calculate_issue_date_age

Session = get_session_factory()


class DataOperationsMixin:
    """データ操作を提供するMixin"""

    def save_data(self, e):
        """データ保存ハンドラ"""
        session = Session()

        if self.selected_row is not None and 'id' in self.selected_row:
            patient_info = session.query(PatientInfo).filter(
                PatientInfo.id == self.selected_row['id']).first()

            if patient_info:
                if not self.dialog_manager.check_required_fields():
                    return

                self._update_patient_info_from_form(patient_info, include_basic_info=True)
                session.commit()

                self.dialog_manager.show_info_message("データが保存されました")

        session.close()
        self.page.update()

    def copy_data(self, e):
        """データコピーハンドラ"""
        patient_id = self.fields['patient_id']
        session = Session()
        patient_info = session.query(PatientInfo). \
            filter(PatientInfo.patient_id == patient_id.value). \
            order_by(PatientInfo.id.desc()).first()

        if patient_info:
            error_message, df_patients = load_patient_data()
            if error_message or df_patients is None:
                session.close()
                return

            patient_csv_info = df_patients[df_patients.iloc[:, 2] == int(patient_id.value)]
            if patient_csv_info.empty:
                session.close()
                return

            patient_csv_info = patient_csv_info.iloc[0]

            patient_info_copy = PatientInfo(
                patient_id=patient_info.patient_id,
                patient_name=patient_info.patient_name,
                kana=patient_info.kana,
                gender=patient_info.gender,
                birthdate=patient_info.birthdate,
                issue_date=datetime.now().date(),
                issue_date_age=calculate_issue_date_age(patient_info.birthdate, datetime.now().date()),
                doctor_id=int(patient_csv_info.iloc[9]),
                doctor_name=patient_csv_info.iloc[10],
                department=patient_csv_info.iloc[14],
                department_id=int(patient_csv_info.iloc[13]),
                main_diagnosis=patient_info.main_diagnosis,
                sheet_name=patient_info.sheet_name,
                creation_count=patient_info.creation_count + 1,
                target_weight=patient_info.target_weight,
                target_bp=patient_info.target_bp,
                target_hba1c=patient_info.target_hba1c,
                goal1=patient_info.goal1,
                goal2=patient_info.goal2,
                target_achievement=patient_info.target_achievement,
                diet1=patient_info.diet1,
                diet2=patient_info.diet2,
                diet3=patient_info.diet3,
                diet4=patient_info.diet4,
                diet_comment=patient_info.diet_comment,
                exercise_prescription=patient_info.exercise_prescription,
                exercise_time=patient_info.exercise_time,
                exercise_frequency=patient_info.exercise_frequency,
                exercise_intensity=patient_info.exercise_intensity,
                daily_activity=patient_info.daily_activity,
                exercise_comment=patient_info.exercise_comment,
                nonsmoker=patient_info.nonsmoker,
                smoking_cessation=patient_info.smoking_cessation,
                other1=patient_info.other1,
                other2=patient_info.other2,
                ophthalmology=patient_info.ophthalmology,
                dental=patient_info.dental,
                cancer_screening=patient_info.cancer_screening
            )
            session.add(patient_info_copy)
            session.commit()

            self.dialog_manager.show_info_message("データがコピーされました")
            self.select_copied_data(patient_info_copy.id)

        session.close()

    def select_copied_data(self, copied_id):
        """コピーしたデータを選択"""
        session = Session()
        patient_info = session.query(PatientInfo).filter(PatientInfo.id == copied_id).first()

        if patient_info:
            self.selected_row = {'id': patient_info.id}
            self._populate_form_from_patient_info(patient_info, session)
            self.update_history(patient_info.patient_id)

        session.close()
        self.page.update()

    def delete_data(self, e):
        """データ削除ハンドラ"""
        if self.selected_row is None:
            self.dialog_manager.show_error_message("削除するデータが選択されていません")
            return

        session = Session()
        patient_info = session.query(PatientInfo).filter(
            PatientInfo.id == self.selected_row['id']).first()

        if patient_info:
            patient_id_val = patient_info.patient_id
            session.delete(patient_info)
            session.commit()
            self.selected_row = None
            self.update_history(patient_id_val)

        session.close()
        self.page.go("/")

    def print_plan(self, e):
        """印刷ハンドラ"""
        session = Session()
        if self.selected_row is not None:
            patient_info = session.query(PatientInfo).filter(
                PatientInfo.id == self.selected_row['id']).first()

            if patient_info:
                self._update_patient_info_from_form(patient_info)
                session.commit()
                TreatmentPlanGenerator.generate_plan(patient_info, "LDTPform")

        session.close()
