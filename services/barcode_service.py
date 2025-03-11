import configparser
from datetime import datetime
from io import BytesIO
from barcode.codex import Code128
from barcode.writer import ImageWriter
from openpyxl.drawing.image import Image


class BarcodeService:
    """
    バーコード生成と管理を担当するサービスクラス
    """

    def __init__(self):
        """バーコードサービスの初期化"""
        # 設定ファイルから設定を読み込む
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')
        self.barcode_config = self.config['Barcode']
        self.document_number = self.config.get('Document', 'document_number', fallback='39221')

    def get_barcode_options(self):
        """
        バーコード生成オプションを取得する

        Returns:
            dict: バーコード生成のオプション設定
        """
        return {
            'write_text': self.barcode_config.getboolean('write_text', False),
            'module_height': self.barcode_config.getfloat('module_height', 15),
            'module_width': self.barcode_config.getfloat('module_width', 0.25),
            'quiet_zone': self.barcode_config.getint('quiet_zone', 1),
        }

    def generate_barcode_data(self, patient_id, department_id, doctor_id, issue_date):
        """
        バーコードデータ文字列を生成する

        Args:
            patient_id (int): 患者ID
            department_id (int): 診療科ID
            doctor_id (int): 医師ID
            issue_date (datetime.date): 発行日

        Returns:
            str: バーコードデータ文字列
        """
        # 各要素を適切な形式に整形
        patient_id_str = str(patient_id).zfill(9)
        department_id_str = str(department_id).zfill(3)
        doctor_id_str = str(doctor_id).zfill(5)
        issue_date_str = issue_date.strftime("%Y%m%d")
        current_time = datetime.now().strftime("%H%M%S")

        # バーコードデータ文字列を構築
        barcode_data = f"{patient_id_str}{self.document_number}{department_id_str}{doctor_id_str}{issue_date_str}{current_time}"
        return barcode_data

    def create_barcode_image(self, barcode_data):
        """
        バーコード画像を生成する

        Args:
            barcode_data (str): バーコードデータ文字列

        Returns:
            BytesIO: バーコード画像データを含むバッファ
        """
        options = self.get_barcode_options()
        barcode = Code128(barcode_data, writer=ImageWriter())
        buffer = BytesIO()
        barcode.write(buffer, options=options)
        return buffer

    def add_barcode_to_sheet(self, sheet, barcode_data):
        """
        Excelシートにバーコードを追加する

        Args:
            sheet: openpyxlのワークシートオブジェクト
            barcode_data (str): バーコードデータ文字列
        """
        # バーコード画像を生成
        buffer = self.create_barcode_image(barcode_data)

        # イメージとして追加
        img = Image(buffer)
        img.width = self.barcode_config.getint('image_width', 200)
        img.height = self.barcode_config.getint('image_height', 30)
        image_position = self.barcode_config.get('image_position', 'B2')

        # シートに追加
        sheet.add_image(img, image_position)

    def generate_filename(self, patient_id, department_id, doctor_id, issue_date):
        """
        Excel出力ファイル名を生成する

        Args:
            patient_id (int): 患者ID
            department_id (int): 診療科ID
            doctor_id (int): 医師ID
            issue_date (datetime.date): 発行日

        Returns:
            str: 出力ファイル名
        """
        patient_id_str = str(patient_id).zfill(9)
        department_id_str = str(department_id).zfill(3)
        doctor_id_str = str(doctor_id).zfill(5)
        issue_date_str = issue_date.strftime("%Y%m%d")
        current_time = datetime.now().strftime("%H%M%S")

        return f"{patient_id_str}{self.document_number}{department_id_str}{doctor_id_str}{issue_date_str}{current_time}.xlsm"
