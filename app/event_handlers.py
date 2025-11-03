from datetime import datetime

from database import get_session_factory
from models import PatientInfo, MainDisease, Template
from services.patient_service import load_patient_data, load_main_diseases, load_sheet_names
from services.treatment_plan_service import TreatmentPlanGenerator
from utils.date_utils import calculate_issue_date_age
from utils.file_utils import format_date

Session = get_session_factory()


class EventHandlers:
    """UIイベントハンドラを管理するクラス"""

    def __init__(self, page, fields, df_patients, dialog_manager):
        """
        初期化

        Args:
            page: Fletのページオブジェクト
            fields: フォームフィールドの辞書
            df_patients: 患者CSVのDataFrame
            dialog_manager: DialogManagerインスタンス
        """
        self.page = page
        self.fields = fields
        self.df_patients = df_patients
        self.dialog_manager = dialog_manager
        self.selected_row = None

    def on_patient_id_change(self, e):
        """患者ID変更時のハンドラ"""
        patient_id = self.fields['patient_id']
        p_id = patient_id.value.strip()
        if p_id:
            self.load_patient_info(int(p_id))
        self.update_history(p_id)

    def on_issue_date_change(self, e, issue_date_picker):
        """発行日変更時のハンドラ"""
        issue_date_value = self.fields['issue_date_value']
        if issue_date_picker.value:
            issue_date_value.value = issue_date_picker.value.strftime("%Y/%m/%d")
            self.page.update()

    def on_date_picker_dismiss(self, e, issue_date_picker):
        """日付ピッカー終了時のハンドラ"""
        issue_date_value = self.fields['issue_date_value']
        if issue_date_picker.value:
            issue_date_value.value = issue_date_picker.value.strftime("%Y/%m/%d")
        self.page.overlay.remove(issue_date_picker)
        self.page.update()

    def on_main_diagnosis_change(self, e):
        """主病名変更時のハンドラ"""
        main_diagnosis = self.fields['main_diagnosis']
        sheet_name_dropdown = self.fields['sheet_name_dropdown']

        selected_main_disease = main_diagnosis.value
        self.apply_template(e)

        with Session() as session:
            if selected_main_disease:
                main_disease = session.query(MainDisease).filter_by(
                    name=selected_main_disease).first()
                sheet_name_options = load_sheet_names(main_disease.id) if main_disease else []
            else:
                sheet_name_options = load_sheet_names()

        sheet_name_dropdown.options = sheet_name_options
        sheet_name_dropdown.value = ""
        self.page.update()

    def on_sheet_name_change(self, e):
        """シート名変更時のハンドラ"""
        self.apply_template(e)
        self.page.update()

    def on_tobacco_checkbox_change(self, e):
        """たばこチェックボックス変更時のハンドラ"""
        nonsmoker = self.fields['nonsmoker']
        smoking_cessation = self.fields['smoking_cessation']

        if e.control == nonsmoker and nonsmoker.value:
            smoking_cessation.value = False
            smoking_cessation.update()
        elif e.control == smoking_cessation and smoking_cessation.value:
            nonsmoker.value = False
            nonsmoker.update()

    def on_row_selected(self, e):
        """行選択時のハンドラ"""
        history = self.fields['history']

        if e.data == "true":
            row_index = history.rows.index(e.control)
            self.selected_row = history.rows[row_index].data
            session = Session()
            patient_info = session.query(PatientInfo).filter(
                PatientInfo.id == self.selected_row['id']).first()

            if patient_info:
                self._populate_form_from_patient_info(patient_info, session)

            session.close()
            self.page.update()
            self.page.go("/edit")

    def _populate_form_from_patient_info(self, patient_info, session):
        """患者情報からフォームを設定"""
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

    def create_new_plan(self, e):
        """新規作成ハンドラ"""
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

    def save_new_plan(self, e):
        """新規保存ハンドラ"""
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

    def _update_patient_info_from_form(self, patient_info, include_basic_info=False):
        """フォームから患者情報を更新"""
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

    def apply_template(self, e):
        """テンプレート適用ハンドラ"""
        fields = self.fields
        main_diagnosis = fields['main_diagnosis']
        sheet_name_dropdown = fields['sheet_name_dropdown']

        selected_main_disease = main_diagnosis.value
        selected_sheet_name = sheet_name_dropdown.value

        if selected_main_disease and selected_sheet_name:
            session = Session()
            template = session.query(Template).filter_by(
                main_disease=selected_main_disease,
                sheet_name=selected_sheet_name
            ).first()

            if template:
                self._apply_template_to_fields(template)
                self.page.update()

            session.close()

    def _apply_template_to_fields(self, template):
        """テンプレートをフィールドに適用"""
        fields = self.fields

        fields['target_bp'].value = template.target_bp
        fields['target_hba1c'].value = template.target_hba1c
        fields['goal1'].value = template.goal1
        fields['goal2'].value = template.goal2
        fields['diet1'].value = template.diet1
        fields['diet2'].value = template.diet2
        fields['diet3'].value = template.diet3
        fields['diet4'].value = template.diet4
        fields['exercise_prescription'].value = template.exercise_prescription
        fields['exercise_time'].value = template.exercise_time
        fields['exercise_frequency'].value = template.exercise_frequency
        fields['exercise_intensity'].value = template.exercise_intensity
        fields['daily_activity'].value = template.daily_activity
        fields['other1'].value = template.other1
        fields['other2'].value = template.other2

    def save_template(self, e):
        """テンプレート保存ハンドラ"""
        fields = self.fields
        main_diagnosis = fields['main_diagnosis']
        sheet_name_dropdown = fields['sheet_name_dropdown']

        if not main_diagnosis.value or not sheet_name_dropdown.value:
            self.dialog_manager.show_error_message("主病名とシート名を選択してください")
            return

        session = Session()
        template = session.query(Template).filter_by(
            main_disease=main_diagnosis.value,
            sheet_name=sheet_name_dropdown.value
        ).first()

        if not template:
            template = Template(
                main_disease=main_diagnosis.value,
                sheet_name=sheet_name_dropdown.value
            )
            session.add(template)

        self._update_template_from_fields(template)
        session.commit()
        session.close()

        self.dialog_manager.show_info_message("テンプレートが保存されました")

    def _update_template_from_fields(self, template):
        """フィールドからテンプレートを更新"""
        fields = self.fields

        template.target_bp = fields['target_bp'].value
        template.target_hba1c = fields['target_hba1c'].value
        template.goal1 = fields['goal1'].value
        template.goal2 = fields['goal2'].value
        template.diet1 = fields['diet1'].value
        template.diet2 = fields['diet2'].value
        template.diet3 = fields['diet3'].value
        template.diet4 = fields['diet4'].value
        template.exercise_prescription = fields['exercise_prescription'].value
        template.exercise_time = fields['exercise_time'].value
        template.exercise_frequency = fields['exercise_frequency'].value
        template.exercise_intensity = fields['exercise_intensity'].value
        template.daily_activity = fields['daily_activity'].value
        template.other1 = fields['other1'].value
        template.other2 = fields['other2'].value

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

    def create_treatment_plan_object(self, p_id, doctor_id, doctor_name, department, department_id, patients_df):
        """療養計画書オブジェクトを作成"""
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
        """療養計画書を作成"""
        try:
            patient_info = self.create_treatment_plan_object(
                p_id, doctor_id, doctor_name, department, department_id, patients_df)
            TreatmentPlanGenerator.generate_plan(patient_info, "LDTPform")
        except ValueError as ve:
            self.dialog_manager.show_error_message(str(ve))

    def save_treatment_plan(self, p_id, doctor_id, doctor_name, department, department_id, patients_df):
        """療養計画書を保存"""
        try:
            patient_info = self.create_treatment_plan_object(
                p_id, doctor_id, doctor_name, department, department_id, patients_df)

            session = Session()
            session.add(patient_info)
            session.commit()
            session.close()

            self.dialog_manager.show_info_message("データが保存されました")
            self.update_history(p_id)
        except ValueError as ve:
            self.dialog_manager.show_error_message(str(ve))

    def update_history(self, filter_patient_id=None):
        """履歴を更新 - サブクラスでオーバーライド"""
        pass

    def fetch_data(self, filter_patient_id=None):
        """データを取得 - サブクラスでオーバーライド"""
        pass
