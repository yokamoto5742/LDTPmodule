from database import get_session_factory
from models import MainDisease, PatientInfo
from services.patient_service import load_sheet_names

Session = get_session_factory()


class UIEventsMixin:
    """UIイベントハンドラを提供するMixin"""

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
