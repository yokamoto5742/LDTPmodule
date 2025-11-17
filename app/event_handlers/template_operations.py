from typing import Any

from database import get_session_factory
from models import Template

Session = get_session_factory()


class TemplateOperationsMixin:
    """テンプレート操作を提供するMixin"""

    page: Any
    fields: dict[str, Any]
    dialog_manager: Any

    def apply_template(self, e: Any) -> None:
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

    def _apply_template_to_fields(self, template: Any) -> None:
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

    def save_template(self, e: Any) -> None:
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

    def _update_template_from_fields(self, template: Any) -> None:
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
