from typing import Any, Callable, Dict, Optional

import flet as ft
import pandas as pd

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

    def __init__(
        self,
        page: ft.Page,
        fields: Dict[str, Any],
        df_patients: Optional[pd.DataFrame],
        dialog_manager: Any
    ) -> None:
        """
        初期化

        Args:
            page: Fletのページオブジェクト
            fields: フォームフィールドの辞書
            df_patients: 患者CSVのDataFrame
            dialog_manager: DialogManagerインスタンス
        """
        self.page: ft.Page = page
        self.fields: Dict[str, Any] = fields
        self.df_patients: Optional[pd.DataFrame] = df_patients
        self.dialog_manager: Any = dialog_manager
        self.selected_row: Optional[Dict[str, Any]] = None
        self.route_manager: Optional[Any] = None
        self.update_history: Optional[Callable[[Optional[str]], None]] = None
        self.fetch_data: Optional[Callable[[Optional[str]], Any]] = None


__all__ = ['EventHandlers']
