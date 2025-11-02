import os
import time
from datetime import datetime
from io import BytesIO

from barcode.codex import Code128
from barcode.writer import ImageWriter
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

from utils import config_manager

config = config_manager.load_config()
barcode_config = config['Barcode']


class TreatmentPlanGenerator:
    @staticmethod
    def generate_plan(patient_info, file_name):
        template_path = config.get("Paths", "template_path")
        output_path = config.get("Paths", "output_path")
        current_time = datetime.now().strftime("%H%M%S")
        patient_id = str(patient_info.patient_id).zfill(9)
        document_number = "39221"
        department_id = str(patient_info.department_id).zfill(3)
        doctor_id = str(patient_info.doctor_id).zfill(5)
        issue_date = patient_info.issue_date.strftime("%Y%m%d")
        new_file_name = f"{patient_id}{document_number}{department_id}{doctor_id}{issue_date}{current_time}.xlsm"
        file_path = os.path.join(output_path, new_file_name)
        workbook = load_workbook(template_path, keep_vba=True)
        common_sheet = workbook["共通情報"]

        # 共通情報シートにデータを設定
        TreatmentPlanGenerator.populate_common_sheet(common_sheet, patient_info)

        # バーコード生成の共通設定
        options = {
            'write_text': barcode_config.getboolean('write_text', False),
            'module_height': barcode_config.getfloat('module_height', 15),
            'module_width': barcode_config.getfloat('module_width', 0.25),
            'quiet_zone': barcode_config.getint('quiet_zone', 1),
        }

        # バーコードデータの生成
        issue_date = patient_info.issue_date.strftime("%Y%m%d")
        barcode_data = f"{patient_id}{document_number}{department_id}{doctor_id}{issue_date}{current_time}"

        # バッファオブジェクト参照を保持（後で閉じるため）
        buffers = []

        def add_barcode_to_sheet(sheet):
            barcode = Code128(barcode_data, writer=ImageWriter())
            buffer = BytesIO()
            barcode.write(buffer, options=options)
            buffer.seek(0)  # 重要: ポインタを先頭に戻す
            img = Image(buffer)
            img.width = barcode_config.getint('image_width', 200)
            img.height = barcode_config.getint('image_height', 30)
            image_position = barcode_config.get('image_position', 'B2')
            sheet.add_image(img, image_position)
            buffers.append(buffer)

        # 両方のシートにバーコードを追加
        initial_sheet = workbook["初回用"]
        continuous_sheet = workbook["継続用"]
        add_barcode_to_sheet(initial_sheet)
        add_barcode_to_sheet(continuous_sheet)

        # すべてのシートの選択状態をリセット
        for sheet in workbook.worksheets:
            sheet.sheet_view.tabSelected = False

        # 適切なシートをアクティブにする
        if patient_info.creation_count == 1:
            ws_plan = workbook["初回用"]
        else:
            ws_plan = workbook["継続用"]
        ws_plan.sheet_view.tabSelected = True
        workbook.active = ws_plan

        # ファイルを保存
        workbook.save(file_path)

        # ファイル保存後にバッファを閉じる
        for buffer in buffers:
            buffer.close()

        # Excelファイルを開く
        time.sleep(0.1)
        os.startfile(file_path)

    @staticmethod
    def populate_common_sheet(common_sheet, patient_info):
        common_sheet["B2"] = patient_info.patient_id
        common_sheet["B3"] = patient_info.patient_name
        common_sheet["B4"] = patient_info.kana
        common_sheet["B5"] = patient_info.gender
        common_sheet["B6"] = patient_info.birthdate
        common_sheet["B7"] = patient_info.issue_date
        common_sheet["B8"] = patient_info.doctor_id
        common_sheet["B9"] = patient_info.doctor_name
        common_sheet["B10"] = patient_info.department_id
        common_sheet["B11"] = patient_info.department
        common_sheet["B12"] = patient_info.main_diagnosis
        common_sheet["B13"] = patient_info.creation_count
        common_sheet["B14"] = patient_info.target_weight
        common_sheet["B15"] = patient_info.sheet_name
        common_sheet["B16"] = patient_info.target_bp
        common_sheet["B17"] = patient_info.target_hba1c
        common_sheet["B18"] = patient_info.goal1
        common_sheet["B19"] = patient_info.goal2
        common_sheet["B20"] = patient_info.target_achievement
        common_sheet["B21"] = patient_info.diet1
        common_sheet["B22"] = patient_info.diet2
        common_sheet["B23"] = patient_info.diet3
        common_sheet["B24"] = patient_info.diet4
        common_sheet["B25"] = patient_info.exercise_prescription
        common_sheet["B26"] = patient_info.exercise_time
        common_sheet["B27"] = patient_info.exercise_frequency
        common_sheet["B28"] = patient_info.exercise_intensity
        common_sheet["B29"] = patient_info.daily_activity
        common_sheet["B30"] = patient_info.nonsmoker
        common_sheet["B31"] = patient_info.smoking_cessation
        common_sheet["B32"] = patient_info.other1
        common_sheet["B33"] = patient_info.other2
        common_sheet["B34"] = patient_info.ophthalmology
        common_sheet["B35"] = patient_info.dental
        common_sheet["B36"] = patient_info.cancer_screening
        common_sheet["B37"] = patient_info.issue_date_age
        common_sheet["B38"] = patient_info.diet_comment
        common_sheet["B39"] = patient_info.exercise_comment
