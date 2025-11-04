import configparser
from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from models import MainDisease, PatientInfo, SheetName
from services.patient_service import (
    fetch_patient_history,
    load_main_diseases,
    load_patient_data,
    load_sheet_names,
)


@pytest.fixture
def setup_test_data(test_db):
    """テスト用データのセットアップ"""
    # 主病名データ
    disease1 = MainDisease(id=1, name="糖尿病")
    disease2 = MainDisease(id=2, name="高血圧")
    disease3 = MainDisease(id=3, name="脂質異常症")

    # シート名データ
    sheet1 = SheetName(id=1, name="糖尿病用", main_disease_id=1)
    sheet2 = SheetName(id=2, name="高血圧用", main_disease_id=2)
    sheet3 = SheetName(id=3, name="脂質異常症用", main_disease_id=3)

    # 患者情報データ
    patient1 = PatientInfo(
        patient_id=1001,
        patient_name="患者A",
        issue_date=date(2025, 1, 10),
        department="内科",
        doctor_name="医師A",
        main_diagnosis="糖尿病",
        sheet_name="糖尿病用",
        creation_count=1
    )
    patient2 = PatientInfo(
        patient_id=1001,
        patient_name="患者A",
        issue_date=date(2025, 2, 15),
        department="内科",
        doctor_name="医師A",
        main_diagnosis="糖尿病",
        sheet_name="糖尿病用",
        creation_count=2
    )
    patient3 = PatientInfo(
        patient_id=2002,
        patient_name="患者B",
        issue_date=date(2025, 1, 20),
        department="循環器科",
        doctor_name="医師B",
        main_diagnosis="高血圧",
        sheet_name="高血圧用",
        creation_count=1
    )

    test_db.add_all([disease1, disease2, disease3, sheet1, sheet2, sheet3, patient1, patient2, patient3])
    test_db.commit()

    return test_db


class TestLoadPatientData:
    """load_patient_data関数のテスト"""

    @patch('services.patient_service.pd.read_csv')
    @patch('services.patient_service.config_manager.load_config')
    def test_load_patient_data_success(self, mock_config, mock_read_csv):
        """患者データ正常読み込みテスト"""
        # モック設定
        mock_config_obj = MagicMock()
        mock_config_obj.get.return_value = 'C:/test/pat.csv'
        mock_config.return_value = mock_config_obj

        # ダミーDataFrame
        df_data = {
            'col1': [pd.Timestamp('2025-01-01'), pd.Timestamp('2025-01-02'), pd.Timestamp('2025-01-03')],
            'col2': ['A', 'B', 'C'],
            'col3': [pd.Timestamp('2025-02-01'), pd.Timestamp('2025-02-02'), pd.Timestamp('2025-02-03')]
        }
        mock_df = pd.DataFrame(df_data)
        mock_read_csv.return_value = mock_df

        # テスト実行
        error_msg, df = load_patient_data()

        # 検証
        assert error_msg == ""
        assert df is not None
        assert len(df) == 3
        mock_read_csv.assert_called_once()

    @patch('services.patient_service.config_manager.load_config')
    def test_load_patient_data_config_error(self, mock_config):
        """設定ファイルエラー時のテスト"""
        # config.iniの読み込みエラーをシミュレート
        mock_config_obj = MagicMock()
        mock_config_obj.get.side_effect = configparser.NoSectionError('FilePaths')
        mock_config.return_value = mock_config_obj

        # テスト実行
        error_msg, df = load_patient_data()

        # 検証
        assert "エラー" in error_msg
        assert df is None

    @patch('services.patient_service.pd.read_csv')
    @patch('services.patient_service.config_manager.load_config')
    def test_load_patient_data_file_not_found(self, mock_config, mock_read_csv):
        """ファイル未検出時のテスト"""
        mock_config_obj = MagicMock()
        mock_config_obj.get.return_value = 'C:/test/not_found.csv'
        mock_config.return_value = mock_config_obj

        mock_read_csv.side_effect = FileNotFoundError("File not found")

        # テスト実行
        error_msg, df = load_patient_data()

        # 検証
        assert "エラー" in error_msg
        assert df is None


class TestLoadMainDiseases:
    """load_main_diseases関数のテスト"""

    @patch('services.patient_service.get_session')
    def test_load_main_diseases_success(self, mock_get_session, setup_test_data):
        """主病名マスタ正常読み込みテスト"""
        # モックセッション
        mock_get_session.return_value.__enter__.return_value = setup_test_data

        # テスト実行
        result = load_main_diseases()

        # 検証
        assert len(result) == 3
        assert result[0].key == "糖尿病"
        assert result[1].key == "高血圧"
        assert result[2].key == "脂質異常症"

    @patch('services.patient_service.get_session')
    def test_load_main_diseases_empty(self, mock_get_session, test_db):
        """空の主病名マスタテスト"""
        mock_get_session.return_value.__enter__.return_value = test_db

        # テスト実行
        result = load_main_diseases()

        # 検証
        assert len(result) == 0


class TestLoadSheetNames:
    """load_sheet_names関数のテスト"""

    @patch('services.patient_service.get_session')
    def test_load_sheet_names_all(self, mock_get_session, setup_test_data):
        """全シート名読み込みテスト"""
        mock_get_session.return_value.__enter__.return_value = setup_test_data

        # テスト実行
        result = load_sheet_names()

        # 検証
        assert len(result) == 3
        assert result[0].key == "糖尿病用"
        assert result[1].key == "高血圧用"
        assert result[2].key == "脂質異常症用"

    @patch('services.patient_service.get_session')
    def test_load_sheet_names_filtered(self, mock_get_session, setup_test_data):
        """主病名IDでフィルタリングされたシート名読み込みテスト"""
        mock_get_session.return_value.__enter__.return_value = setup_test_data

        # テスト実行 (main_disease_id=1で絞り込み)
        result = load_sheet_names(main_disease=1)

        # 検証
        assert len(result) == 1
        assert result[0].key == "糖尿病用"

    @patch('services.patient_service.get_session')
    def test_load_sheet_names_empty(self, mock_get_session, test_db):
        """空のシート名マスタテスト"""
        mock_get_session.return_value.__enter__.return_value = test_db

        # テスト実行
        result = load_sheet_names()

        # 検証
        assert len(result) == 0

    @patch('services.patient_service.get_session')
    def test_load_sheet_names_no_match(self, mock_get_session, setup_test_data):
        """該当なしのフィルタリングテスト"""
        mock_get_session.return_value.__enter__.return_value = setup_test_data

        # テスト実行 (存在しないmain_disease_id)
        result = load_sheet_names(main_disease=999)

        # 検証
        assert len(result) == 0


class TestFetchPatientHistory:
    """fetch_patient_history関数のテスト"""

    @patch('services.patient_service.Session')
    def test_fetch_patient_history_success(self, mock_session_class, setup_test_data):
        """患者履歴取得成功テスト"""
        # モックセッション
        mock_session_class.return_value = setup_test_data

        # テスト実行
        result = list(fetch_patient_history(filter_patient_id=1001))

        # 検証
        assert len(result) == 2
        assert result[0]['issue_date'] == "2025/02/15"  # 降順
        assert result[1]['issue_date'] == "2025/01/10"
        assert result[0]['count'] == 2
        assert result[1]['count'] == 1

    @patch('services.patient_service.Session')
    def test_fetch_patient_history_single_record(self, mock_session_class, setup_test_data):
        """単一レコードの患者履歴テスト"""
        mock_session_class.return_value = setup_test_data

        # テスト実行
        result = list(fetch_patient_history(filter_patient_id=2002))

        # 検証
        assert len(result) == 1
        assert result[0]['department'] == "循環器科"
        assert result[0]['doctor_name'] == "医師B"
        assert result[0]['main_diagnosis'] == "高血圧"

    @patch('services.patient_service.Session')
    def test_fetch_patient_history_no_patient_id(self, mock_session_class, setup_test_data):
        """患者ID未指定時のテスト"""
        mock_session_class.return_value = setup_test_data

        # テスト実行
        result = list(fetch_patient_history(filter_patient_id=None))

        # 検証
        assert len(result) == 0

    @patch('services.patient_service.Session')
    def test_fetch_patient_history_empty_patient_id(self, mock_session_class, setup_test_data):
        """空の患者IDテスト"""
        mock_session_class.return_value = setup_test_data

        # テスト実行
        result = list(fetch_patient_history(filter_patient_id=""))

        # 検証
        assert len(result) == 0

    @patch('services.patient_service.Session')
    def test_fetch_patient_history_no_match(self, mock_session_class, setup_test_data):
        """該当患者なしのテスト"""
        mock_session_class.return_value = setup_test_data

        # テスト実行
        result = list(fetch_patient_history(filter_patient_id=9999))

        # 検証
        assert len(result) == 0

    @patch('services.patient_service.Session')
    def test_fetch_patient_history_date_format(self, mock_session_class, setup_test_data):
        """日付フォーマットのテスト"""
        mock_session_class.return_value = setup_test_data

        # テスト実行
        result = list(fetch_patient_history(filter_patient_id=1001))

        # 検証
        assert result[0]['issue_date'] == "2025/02/15"
        assert result[1]['issue_date'] == "2025/01/10"
        # 日付フォーマットが正しいか確認
        assert "/" in result[0]['issue_date']

    @patch('services.patient_service.Session')
    def test_fetch_patient_history_all_fields(self, mock_session_class, setup_test_data):
        """全フィールド取得テスト"""
        mock_session_class.return_value = setup_test_data

        # テスト実行
        result = list(fetch_patient_history(filter_patient_id=1001))

        # 検証
        record = result[0]
        assert 'id' in record
        assert 'issue_date' in record
        assert 'department' in record
        assert 'doctor_name' in record
        assert 'main_diagnosis' in record
        assert 'sheet_name' in record
        assert 'count' in record
