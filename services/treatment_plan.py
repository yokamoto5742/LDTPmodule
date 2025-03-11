import os
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from io import BytesIO
from barcode.codex import Code128
from barcode.writer import ImageWriter
import configparser


class TreatmentPlanService:
    """治療計画書生成サービス"""

    def __init__(self):
        """設定を読み込む"""
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')
        self.template_path = self.config.get("Paths", "template_path")
        self.output_path = self.config.get("Paths", "output_path")
        self.barcode_config = self.config['Barcode']
        self.document_number = self.config.get('Document', 'document_number', fallback='39221')

    def generate_plan(self, patient_info):
        """治療計画書を生成してExcelファイルを出力する"""
        try:
            # ファイル名生成
            current_time = datetime.now().strftime("%H%M%S")
            patient_id = str(patient_info.patient_id).zfill(9)
            department_id = str(patient_info.department_id).zfill(3)
            doctor_id = str(patient_info.doctor_id).zfill(5)
            issue_date = patient_info.issue_date.strftime("%Y%m%d")

            new_file_name = f"{patient_id}{self.document_number}{department_id}{doctor_id}{issue_date}{current_time}.xlsm"
            file_path = os.path.join(self.output_path, new_file_name)

            # ディレクトリが存在しない場合は作成
            os.makedirs(self.output_path, exist_ok=True)

            # テンプレート読み込み
            workbook = load_workbook(self.template_path, keep_vba=True)
            common_sheet = workbook["共通情報"]
            initial_sheet = workbook["初回用"]
            continuous_sheet = workbook["継続用"]

            # 共通情報シートに患者情報を記入
            self._populate_common_sheet(common_sheet, patient_info)

            # バーコード生成
            barcode_data = f"{patient_id}{self.document_number}{department_id}{doctor_id}{issue_date}{current_time}"
            self._add_barcode_to_sheet(initial_sheet, barcode_data)
            self._add_barcode_to_sheet(continuous_sheet, barcode_data)

            # いったん保存
            workbook.save(file_path)

            # 適切なシートをアクティブに設定
            wb = load_workbook(file_path, read_only=False, keep_vba=True)
            ws_common = wb["共通情報"]
            ws_common.sheet_view.tabSelected = False

            # 全てのシートの選択状態をリセット
            for sheet in wb.worksheets:
                sheet.sheet_view.tabSelected = False

            # 適切なシートをアクティブにし、選択状態にする
            if patient_info.creation_count == 1:
                ws_plan = wb["初回用"]
            else:
                ws_plan = wb["継続用"]
            ws_plan.sheet_view.tabSelected = True
            wb.active = ws_plan

            wb.save(file_path)

            # ファイルを開く
            os.startfile(file_path)

            return file_path
        except Exception as e:
            # ログ出力等のエラーハンドリング
            print(f"治療計画書生成中にエラーが発生しました: {str(e)}")
            raise

    def _populate_common_sheet(self, common_sheet, patient_info):
        """共通情報シートに患者情報を記入する"""
        # PatientInfoの全属性をシートに記入
        field_mapping = {
            "B2": "patient_id",
            "B3": "patient_name",
            "B4": "kana",
            "B5": "gender",
            "B6": "birthdate",
            "B7": "issue_date",
            "B8": "doctor_id",
            "B9": "doctor_name",
            "B10": "department_id",
            "B11": "department",
            "B12": "main_diagnosis",
            "B13": "creation_count",
            "B14": "target_weight",
            "B15": "sheet_name",
            "B16": "target_bp",
            "B17": "target_hba1c",
            "B18": "goal1",
            "B19": "goal2",
            "B20": "target_achievement",
            "B21": "diet1",
            "B22": "diet2",
            "B23": "diet3",
            "B24": "diet4",
            "B25": "exercise_prescription",
            "B26": "exercise_time",
            "B27": "exercise_frequency",
            "B28": "exercise_intensity",
            "B29": "daily_activity",
            "B30": "nonsmoker",
            "B31": "smoking_cessation",
            "B32": "other1",
            "B33": "other2",
            "B34": "ophthalmology",
            "B35": "dental",
            "B36": "cancer_screening",
            "B37": "issue_date_age",
            "B38": "diet_comment",
            "B39": "exercise_comment",
        }

        for cell, attr in field_mapping.items():
            if hasattr(patient_info, attr):
                common_sheet[cell] = getattr(patient_info, attr)

    def _add_barcode_to_sheet(self, sheet, barcode_data):
        """シートにバーコードを追加する"""
        # バーコード生成の共通設定
        options = {
            'write_text': self.barcode_config.getboolean('write_text', False),
            'module_height': self.barcode_config.getfloat('module_height', 15),
            'module_width': self.barcode_config.getfloat('module_width', 0.25),
            'quiet_zone': self.barcode_config.getint('quiet_zone', 1),
        }

        # バーコード生成
        barcode = Code128(barcode_data, writer=ImageWriter())
        buffer = BytesIO()
        barcode.write(buffer, options=options)

        # イメージとして追加
        img = Image(buffer)
        img.width = self.barcode_config.getint('image_width', 200)
        img.height = self.barcode_config.getint('image_height', 30)
        image_position = self.barcode_config.get('image_position', 'B2')
        sheet.add_image(img, image_position)