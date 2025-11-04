from .data_operations import DataOperationsMixin
from .form_operations import FormOperationsMixin
from .template_operations import TemplateOperationsMixin
from .treatment_plan_operations import TreatmentPlanOperationsMixin
from .ui_events import UIEventsMixin


class EventHandlers(
    UIEventsMixin,
    FormOperationsMixin,
    DataOperationsMixin,
    TreatmentPlanOperationsMixin,
    TemplateOperationsMixin
):
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

    def update_history(self, filter_patient_id=None):
        """履歴を更新 サブクラスでオーバーライド"""
        pass

    def fetch_data(self, filter_patient_id=None):
        """データを取得 サブクラスでオーバーライド"""
        pass


__all__ = ['EventHandlers']
