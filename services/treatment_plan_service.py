import os
import time
from datetime import datetime
from io import BytesIO
from typing import Any

from barcode.codex import Code128
from barcode.writer import ImageWriter
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from utils import config_manager

config = config_manager.load_config()
barcode_config = config['Barcode']

DOCUMENT_NUMBER = "39221"

# 共通情報シートのセルとPatientInfo属性の対応
COMMON_SHEET_CELL_MAP: list[tuple[str, str]] = [
    ("B2", "patient_id"),
    ("B3", "patient_name"),
    ("B4", "kana"),
    ("B5", "gender"),
    ("B6", "birthdate"),
    ("B7", "issue_date"),
    ("B8", "doctor_id"),
    ("B9", "doctor_name"),
    ("B10", "department_id"),
    ("B11", "department"),
    ("B12", "main_diagnosis"),
    ("B13", "creation_count"),
    ("B14", "target_weight"),
    ("B15", "sheet_name"),
    ("B16", "target_bp"),
    ("B17", "target_hba1c"),
    ("B18", "goal1"),
    ("B19", "goal2"),
    ("B20", "target_achievement"),
    ("B21", "diet1"),
    ("B22", "diet2"),
    ("B23", "diet3"),
    ("B24", "diet4"),
    ("B25", "exercise_prescription"),
    ("B26", "exercise_time"),
    ("B27", "exercise_frequency"),
    ("B28", "exercise_intensity"),
    ("B29", "daily_activity"),
    ("B30", "nonsmoker"),
    ("B31", "smoking_cessation"),
    ("B32", "other1"),
    ("B33", "other2"),
    ("B34", "ophthalmology"),
    ("B35", "dental"),
    ("B36", "cancer_screening"),
    ("B37", "issue_date_age"),
    ("B38", "diet_comment"),
    ("B39", "exercise_comment"),
]


class TreatmentPlanGenerator:
    @staticmethod
    def generate_plan(patient_info, file_name):  # noqa: ARG004  # シグネチャ維持のため保持
        del file_name
        template_path = config.get("Paths", "template_path")
        output_path = config.get("Paths", "output_path")

        document_code = TreatmentPlanGenerator._build_document_code(patient_info)
        new_file_name = f"{document_code}.xlsm"
        file_path = os.path.join(output_path, new_file_name)

        workbook = load_workbook(template_path, keep_vba=True)
        TreatmentPlanGenerator.populate_common_sheet(workbook["共通情報"], patient_info)

        options = TreatmentPlanGenerator._build_barcode_options()
        buffers = [
            TreatmentPlanGenerator._add_barcode_to_sheet(workbook["初回用"], document_code, options),
            TreatmentPlanGenerator._add_barcode_to_sheet(workbook["継続用"], document_code, options),
        ]

        TreatmentPlanGenerator._activate_target_sheet(workbook, patient_info.creation_count)

        workbook.save(file_path)

        for buffer in buffers:
            buffer.close()

        time.sleep(0.1)
        os.startfile(file_path)

    @staticmethod
    def _build_document_code(patient_info) -> str:
        patient_id = str(patient_info.patient_id).zfill(9)
        department_id = str(patient_info.department_id).zfill(3)
        doctor_id = str(patient_info.doctor_id).zfill(5)
        issue_date = patient_info.issue_date.strftime("%Y%m%d")
        current_time = datetime.now().strftime("%H%M%S")
        return f"{patient_id}{DOCUMENT_NUMBER}{department_id}{doctor_id}{issue_date}{current_time}"

    @staticmethod
    def _build_barcode_options() -> dict[str, Any]:
        return {
            'write_text': barcode_config.getboolean('write_text', False),
            'module_height': barcode_config.getfloat('module_height', 15),
            'module_width': barcode_config.getfloat('module_width', 0.25),
            'quiet_zone': barcode_config.getint('quiet_zone', 1),
        }

    @staticmethod
    def _add_barcode_to_sheet(sheet: Worksheet, data: str, options: dict) -> BytesIO:
        barcode = Code128(data, writer=ImageWriter())
        buffer = BytesIO()
        barcode.write(buffer, options=options)
        buffer.seek(0)  # 重要: ポインタを先頭に戻す
        img = Image(buffer)
        img.width = barcode_config.getint('image_width', 200)
        img.height = barcode_config.getint('image_height', 30)
        sheet.add_image(img, barcode_config.get('image_position', 'B2'))
        return buffer

    @staticmethod
    def _activate_target_sheet(workbook: Workbook, creation_count: int) -> None:
        for sheet in workbook.worksheets:
            sheet.sheet_view.tabSelected = False

        target_name = "初回用" if creation_count == 1 else "継続用"
        ws_plan = workbook[target_name]
        ws_plan.sheet_view.tabSelected = True
        workbook.active = ws_plan

    @staticmethod
    def populate_common_sheet(common_sheet, patient_info):
        for cell, attr in COMMON_SHEET_CELL_MAP:
            common_sheet[cell] = getattr(patient_info, attr)
