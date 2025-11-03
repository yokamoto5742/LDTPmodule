import os
from datetime import date
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from models.patient_info import PatientInfo
from services.treatment_plan_service import TreatmentPlanGenerator


@pytest.fixture
def sample_patient_info():
    """テスト用の患者情報サンプル"""
    patient = PatientInfo(
        patient_id=12345,
        patient_name="山田太郎",
        kana="ヤマダタロウ",
        gender="男",
        birthdate=date(1980, 5, 15),
        issue_date=date(2025, 1, 10),
        issue_date_age=44,
        doctor_id=1001,
        doctor_name="田中医師",
        department="内科",
        department_id=10,
        main_diagnosis="糖尿病",
        creation_count=1,
        target_weight=65.5,
        sheet_name="糖尿病用",
        target_bp="130/80",
        target_hba1c="7.0",
        goal1="体重を減らす",
        goal2="HbA1cを改善する",
        target_achievement="3ヶ月後",
        diet1="野菜を多く摂る",
        diet2="塩分控えめ",
        diet3="間食を減らす",
        diet4="腹八分目",
        diet_comment="バランスの良い食事を心がける",
        exercise_prescription="ウォーキング",
        exercise_time="30分",
        exercise_frequency="週5日",
        exercise_intensity="軽め",
        daily_activity="階段を使う",
        exercise_comment="無理のない範囲で継続する",
        nonsmoker=True,
        smoking_cessation=False,
        other1="定期的な血糖測定",
        other2="",
        ophthalmology=True,
        dental=True,
        cancer_screening=False
    )
    return patient


@pytest.fixture
def mock_config():
    """テスト用の設定をモック"""
    config_mock = MagicMock()
    config_mock.get.side_effect = lambda section, key: {
        ('Paths', 'template_path'): 'C:/test/template.xlsm',
        ('Paths', 'output_path'): 'C:/test/output',
    }.get((section, key), '')
    config_mock.getboolean.return_value = False
    config_mock.getfloat.side_effect = lambda key, default: default
    config_mock.getint.side_effect = lambda key, default: default
    return config_mock


class TestTreatmentPlanGenerator:
    """TreatmentPlanGeneratorクラスのテスト"""

    @patch('services.treatment_plan_service.Image')
    @patch('services.treatment_plan_service.Code128')
    @patch('services.treatment_plan_service.load_workbook')
    @patch('services.treatment_plan_service.config')
    @patch('os.startfile')
    def test_generate_plan_creates_file(self, mock_startfile, mock_config, mock_load_wb, mock_code128, mock_image, sample_patient_info):
        """療養計画書生成テスト"""
        # モックの設定
        mock_config.get.side_effect = lambda section, key: {
            ('Paths', 'template_path'): 'C:/test/template.xlsm',
            ('Paths', 'output_path'): 'C:/test/output',
        }.get((section, key), '')

        mock_wb = MagicMock()
        mock_sheet = MagicMock()
        mock_wb.__getitem__.return_value = mock_sheet
        mock_wb.worksheets = [mock_sheet]
        mock_load_wb.return_value = mock_wb

        mock_barcode_config = MagicMock()
        mock_barcode_config.getboolean.return_value = False
        mock_barcode_config.getfloat.side_effect = lambda key, default: default
        mock_barcode_config.getint.side_effect = lambda key, default: {
            'quiet_zone': 1,
            'image_width': 200,
            'image_height': 30
        }.get(key, default)
        mock_barcode_config.get.return_value = 'B2'
        mock_config.__getitem__.return_value = mock_barcode_config

        # バーコード生成のモック
        mock_barcode_instance = MagicMock()
        mock_code128.return_value = mock_barcode_instance

        # 画像のモック
        mock_image_instance = MagicMock()
        mock_image.return_value = mock_image_instance

        # テスト実行
        TreatmentPlanGenerator.generate_plan(sample_patient_info, 'test.xlsm')

        # 検証
        mock_load_wb.assert_called_once()
        mock_wb.save.assert_called_once()
        mock_startfile.assert_called_once()

    def test_populate_common_sheet(self, sample_patient_info):
        """共通情報シートへのデータ設定テスト"""
        # モックシートの作成
        mock_sheet = MagicMock()

        # メソッド実行
        TreatmentPlanGenerator.populate_common_sheet(mock_sheet, sample_patient_info)

        # 検証: 主要なフィールドが設定されているか
        assert mock_sheet.__setitem__.call_count > 0

        # 特定のセルへの設定を検証
        calls = mock_sheet.__setitem__.call_args_list
        cell_values = {call[0][0]: call[0][1] for call in calls}

        assert cell_values.get("B2") == 12345
        assert cell_values.get("B3") == "山田太郎"
        assert cell_values.get("B4") == "ヤマダタロウ"
        assert cell_values.get("B5") == "男"

    def test_populate_common_sheet_all_fields(self, sample_patient_info):
        """共通情報シート - 全フィールド設定テスト"""
        mock_sheet = {}

        # カスタムの__setitem__を実装
        def mock_setitem(key, value):
            mock_sheet[key] = value

        sheet_mock = MagicMock()
        sheet_mock.__setitem__.side_effect = mock_setitem

        TreatmentPlanGenerator.populate_common_sheet(sheet_mock, sample_patient_info)

        # 主要フィールドの検証
        assert mock_sheet["B2"] == 12345  # patient_id
        assert mock_sheet["B3"] == "山田太郎"  # patient_name
        assert mock_sheet["B12"] == "糖尿病"  # main_diagnosis
        assert mock_sheet["B13"] == 1  # creation_count
        assert mock_sheet["B14"] == 65.5  # target_weight

    def test_populate_common_sheet_boolean_fields(self):
        """共通情報シート - Boolean型フィールドテスト"""
        patient = PatientInfo(
            nonsmoker=True,
            smoking_cessation=False,
            ophthalmology=True,
            dental=False,
            cancer_screening=True
        )

        mock_sheet = {}

        def mock_setitem(key, value):
            mock_sheet[key] = value

        sheet_mock = MagicMock()
        sheet_mock.__setitem__.side_effect = mock_setitem

        TreatmentPlanGenerator.populate_common_sheet(sheet_mock, patient)

        assert mock_sheet["B30"] is True  # nonsmoker
        assert mock_sheet["B31"] is False  # smoking_cessation
        assert mock_sheet["B34"] is True  # ophthalmology
        assert mock_sheet["B35"] is False  # dental
        assert mock_sheet["B36"] is True  # cancer_screening

    def test_populate_common_sheet_date_fields(self):
        """共通情報シート - 日付フィールドテスト"""
        patient = PatientInfo(
            birthdate=date(1990, 3, 20),
            issue_date=date(2025, 2, 15)
        )

        mock_sheet = {}

        def mock_setitem(key, value):
            mock_sheet[key] = value

        sheet_mock = MagicMock()
        sheet_mock.__setitem__.side_effect = mock_setitem

        TreatmentPlanGenerator.populate_common_sheet(sheet_mock, patient)

        assert mock_sheet["B6"] == date(1990, 3, 20)  # birthdate
        assert mock_sheet["B7"] == date(2025, 2, 15)  # issue_date

    def test_populate_common_sheet_diet_fields(self):
        """共通情報シート - 食事指導フィールドテスト"""
        patient = PatientInfo(
            diet1="野菜中心",
            diet2="塩分制限",
            diet3="糖質控えめ",
            diet4="規則正しい食事",
            diet_comment="バランス重視"
        )

        mock_sheet = {}

        def mock_setitem(key, value):
            mock_sheet[key] = value

        sheet_mock = MagicMock()
        sheet_mock.__setitem__.side_effect = mock_setitem

        TreatmentPlanGenerator.populate_common_sheet(sheet_mock, patient)

        assert mock_sheet["B21"] == "野菜中心"
        assert mock_sheet["B22"] == "塩分制限"
        assert mock_sheet["B23"] == "糖質控えめ"
        assert mock_sheet["B24"] == "規則正しい食事"
        assert mock_sheet["B38"] == "バランス重視"

    def test_populate_common_sheet_exercise_fields(self):
        """共通情報シート - 運動指導フィールドテスト"""
        patient = PatientInfo(
            exercise_prescription="ジョギング",
            exercise_time="40分",
            exercise_frequency="週3回",
            exercise_intensity="中程度",
            daily_activity="通勤で歩く",
            exercise_comment="無理なく続ける"
        )

        mock_sheet = {}

        def mock_setitem(key, value):
            mock_sheet[key] = value

        sheet_mock = MagicMock()
        sheet_mock.__setitem__.side_effect = mock_setitem

        TreatmentPlanGenerator.populate_common_sheet(sheet_mock, patient)

        assert mock_sheet["B25"] == "ジョギング"
        assert mock_sheet["B26"] == "40分"
        assert mock_sheet["B27"] == "週3回"
        assert mock_sheet["B28"] == "中程度"
        assert mock_sheet["B29"] == "通勤で歩く"
        assert mock_sheet["B39"] == "無理なく続ける"

    def test_populate_common_sheet_with_none_values(self):
        """共通情報シート - None値のテスト"""
        patient = PatientInfo(
            patient_id=999,
            patient_name=None,
            target_weight=None,
            diet_comment=None
        )

        mock_sheet = {}

        def mock_setitem(key, value):
            mock_sheet[key] = value

        sheet_mock = MagicMock()
        sheet_mock.__setitem__.side_effect = mock_setitem

        TreatmentPlanGenerator.populate_common_sheet(sheet_mock, patient)

        assert mock_sheet["B2"] == 999
        assert mock_sheet["B3"] is None
        assert mock_sheet["B14"] is None
        assert mock_sheet["B38"] is None

    @patch('services.treatment_plan_service.load_workbook')
    @patch('services.treatment_plan_service.config')
    @patch('os.startfile')
    def test_generate_plan_file_naming(self, mock_startfile, mock_config, mock_load_wb):
        """ファイル名生成テスト"""
        patient = PatientInfo(
            patient_id=123,
            department_id=5,
            doctor_id=99,
            issue_date=date(2025, 1, 15),
            creation_count=1
        )

        mock_config.get.side_effect = lambda section, key: {
            ('Paths', 'template_path'): 'C:/test/template.xlsm',
            ('Paths', 'output_path'): 'C:/test/output',
        }.get((section, key), '')

        mock_wb = MagicMock()
        mock_sheet = MagicMock()
        mock_wb.__getitem__.return_value = mock_sheet
        mock_wb.worksheets = [mock_sheet]
        mock_load_wb.return_value = mock_wb

        mock_barcode_config = MagicMock()
        mock_barcode_config.getboolean.return_value = False
        mock_barcode_config.getfloat.side_effect = lambda key, default: default
        mock_barcode_config.getint.side_effect = lambda key, default: default
        mock_barcode_config.get.return_value = 'B2'
        mock_config.__getitem__.return_value = mock_barcode_config

        TreatmentPlanGenerator.generate_plan(patient, 'test.xlsm')

        # ファイル保存が呼ばれたことを確認
        assert mock_wb.save.call_count == 1
        saved_path = mock_wb.save.call_args[0][0]

        # ファイル名の構成要素を確認
        filename = os.path.basename(saved_path)
        assert filename.startswith("000000123")  # patient_id (9桁ゼロ埋め)
        assert "39221" in filename  # document_number
        assert filename.endswith(".xlsm")
