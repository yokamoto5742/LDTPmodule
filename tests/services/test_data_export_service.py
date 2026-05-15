import csv
import os
import tempfile
from datetime import date
from unittest.mock import MagicMock, Mock, patch

import pytest

from models import PatientInfo
from services.data_export_service import export_to_csv, import_from_csv


class TestExportToCsv:
    """export_to_csv関数のテストクラス"""

    @pytest.fixture
    def temp_export_dir(self):
        """一時エクスポートディレクトリのフィクスチャ"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def mock_patient_data(self):
        """テスト用患者データのフィクスチャ"""
        patient = Mock(spec=PatientInfo)
        patient.patient_id = 12345
        patient.patient_name = "山田太郎"
        patient.kana = "ヤマダタロウ"
        patient.gender = "男性"
        patient.birthdate = date(1980, 1, 1)
        patient.issue_date = date(2025, 1, 1)
        patient.issue_date_age = 45
        patient.doctor_id = 1
        patient.doctor_name = "鈴木医師"
        patient.department = "内科"
        patient.department_id = 10
        patient.main_diagnosis = "糖尿病"
        patient.sheet_name = "糖尿病"
        patient.creation_count = 1
        patient.target_weight = 70.5
        patient.target_bp = "130/80"
        patient.target_hba1c = "7.0"
        patient.goal1 = "体重減少"
        patient.goal2 = "運動習慣"
        patient.target_achievement = "3ヶ月"
        patient.diet1 = "カロリー制限"
        patient.diet2 = "塩分制限"
        patient.diet3 = ""
        patient.diet4 = ""
        patient.diet_comment = "バランスの良い食事"
        patient.exercise_prescription = "ウォーキング"
        patient.exercise_time = "30分"
        patient.exercise_frequency = "週5回"
        patient.exercise_intensity = "中等度"
        patient.daily_activity = "通勤時歩行"
        patient.exercise_comment = "無理のない範囲で"
        patient.nonsmoker = True
        patient.smoking_cessation = False
        patient.other1 = ""
        patient.other2 = ""
        patient.ophthalmology = True
        patient.dental = False
        patient.cancer_screening = True
        return [patient]

    @patch('services.data_export_service.get_session')
    def test_export_to_csv_success(self, mock_get_session, temp_export_dir, mock_patient_data):
        """正常系: CSV出力が成功する"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.all.return_value = mock_patient_data

        csv_filename, csv_path, error = export_to_csv(temp_export_dir)

        assert error is None
        assert csv_filename is not None
        assert csv_filename.startswith("patient_info_export_")
        assert csv_filename.endswith(".csv")
        assert csv_path is not None
        assert csv_path == os.path.join(temp_export_dir, csv_filename)
        assert os.path.exists(csv_path)

        with open(csv_path, 'r', encoding='shift_jis') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 2  # ヘッダー + 1データ行
            assert rows[0][0] == 'id'

    @patch('services.data_export_service.get_session')
    def test_export_to_csv_creates_directory(self, mock_get_session, mock_patient_data):
        """正常系: エクスポートフォルダが存在しない場合に作成される"""
        with tempfile.TemporaryDirectory() as tmpdir:
            non_existent_dir = os.path.join(tmpdir, "new_export_folder")

            mock_session = MagicMock()
            mock_get_session.return_value.__enter__.return_value = mock_session
            mock_session.query.return_value.all.return_value = mock_patient_data

            _, csv_path, error = export_to_csv(non_existent_dir)

            assert error is None
            assert os.path.exists(non_existent_dir)
            assert csv_path is not None
            assert os.path.exists(csv_path)

    @patch('services.data_export_service.get_session')
    def test_export_to_csv_empty_data(self, mock_get_session, temp_export_dir):
        """正常系: データが0件の場合でもヘッダーのみ出力される"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.all.return_value = []

        _, csv_path, error = export_to_csv(temp_export_dir)

        assert error is None
        assert csv_path is not None
        assert os.path.exists(csv_path)

        with open(csv_path, 'r', encoding='shift_jis') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 1  # ヘッダーのみ

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    @patch('services.data_export_service.get_session')
    def test_export_to_csv_permission_error(self, mock_get_session, _mock_open_func, temp_export_dir, mock_patient_data):
        """異常系: ファイル書き込み権限エラー"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.all.return_value = mock_patient_data

        csv_filename, csv_path, error = export_to_csv(temp_export_dir)

        assert csv_filename is None
        assert csv_path is None
        assert error is not None
        assert "Permission denied" in error

    @patch('builtins.open', side_effect=IOError("I/O error"))
    @patch('services.data_export_service.get_session')
    def test_export_to_csv_io_error(self, mock_get_session, _mock_open_func, temp_export_dir, mock_patient_data):
        """異常系: ファイルI/Oエラー"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.all.return_value = mock_patient_data

        csv_filename, csv_path, error = export_to_csv(temp_export_dir)

        assert csv_filename is None
        assert csv_path is None
        assert error is not None
        assert "I/O error" in error

    @patch('services.data_export_service.get_session')
    def test_export_to_csv_database_error(self, mock_get_session, temp_export_dir):
        """異常系: データベースクエリエラー"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.query.side_effect = Exception("Database connection failed")

        csv_filename, csv_path, error = export_to_csv(temp_export_dir)

        assert csv_filename is None
        assert csv_path is None
        assert error is not None
        assert "Database connection failed" in error

    @patch('services.data_export_service.get_session')
    def test_export_to_csv_filename_format(self, mock_get_session, temp_export_dir, mock_patient_data):
        """正常系: ファイル名のフォーマットが正しい"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.all.return_value = mock_patient_data

        csv_filename, _, error = export_to_csv(temp_export_dir)

        assert error is None
        assert csv_filename is not None
        import re
        pattern = r'^patient_info_export_\d{8}_\d{6}\.csv$'
        assert re.match(pattern, csv_filename)


class TestImportFromCsv:
    """import_from_csv関数のテストクラス"""

    @pytest.fixture
    def temp_csv_file(self):
        """一時CSVファイルのフィクスチャ"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', prefix='patient_info_',
                                        encoding='shift_jis', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'patient_id', 'patient_name', 'kana', 'gender', 'birthdate', 'issue_date',
                'issue_date_age', 'doctor_id', 'doctor_name', 'department', 'department_id',
                'main_diagnosis', 'sheet_name', 'creation_count', 'target_weight', 'target_bp',
                'target_hba1c', 'goal1', 'goal2', 'target_achievement', 'diet1', 'diet2',
                'diet3', 'diet4', 'diet_comment', 'exercise_prescription', 'exercise_time',
                'exercise_frequency', 'exercise_intensity', 'daily_activity', 'exercise_comment',
                'nonsmoker', 'smoking_cessation', 'other1', 'other2', 'ophthalmology',
                'dental', 'cancer_screening'
            ])
            writer.writeheader()
            writer.writerow({
                'patient_id': '12345',
                'patient_name': '山田太郎',
                'kana': 'ヤマダタロウ',
                'gender': '男性',
                'birthdate': '1980-01-01',
                'issue_date': '2025-01-01',
                'issue_date_age': '45',
                'doctor_id': '1',
                'doctor_name': '鈴木医師',
                'department': '内科',
                'department_id': '10',
                'main_diagnosis': '糖尿病',
                'sheet_name': '糖尿病',
                'creation_count': '1',
                'target_weight': '70.5',
                'target_bp': '130/80',
                'target_hba1c': '7.0',
                'goal1': '体重減少',
                'goal2': '運動習慣',
                'target_achievement': '3ヶ月',
                'diet1': 'カロリー制限',
                'diet2': '塩分制限',
                'diet3': '',
                'diet4': '',
                'diet_comment': 'バランスの良い食事',
                'exercise_prescription': 'ウォーキング',
                'exercise_time': '30分',
                'exercise_frequency': '週5回',
                'exercise_intensity': '中等度',
                'daily_activity': '通勤時歩行',
                'exercise_comment': '無理のない範囲で',
                'nonsmoker': 'True',
                'smoking_cessation': 'False',
                'other1': '',
                'other2': '',
                'ophthalmology': 'True',
                'dental': 'False',
                'cancer_screening': 'True'
            })
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @patch('services.data_export_service.get_session')
    def test_import_from_csv_success(self, mock_get_session, temp_csv_file):
        """正常系: CSV取込が成功する"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        error = import_from_csv(temp_csv_file)

        assert error is None
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

        added_patient = mock_session.add.call_args[0][0]
        assert added_patient.patient_id == 12345
        assert added_patient.patient_name == "山田太郎"
        assert added_patient.birthdate == date(1980, 1, 1)
        assert added_patient.issue_date == date(2025, 1, 1)
        assert added_patient.target_weight == 70.5
        assert added_patient.nonsmoker is True
        assert added_patient.smoking_cessation is False

    def test_import_from_csv_invalid_filename(self):
        """異常系: ファイル名が不正"""
        invalid_file = "invalid_filename.csv"

        error = import_from_csv(invalid_file)

        assert error == "インポートエラー:このファイルはインポートできません"

    @patch('services.data_export_service.get_session')
    def test_import_from_csv_file_not_found(self, _mock_get_session):
        """異常系: ファイルが存在しない"""
        non_existent_file = "patient_info_nonexistent.csv"

        error = import_from_csv(non_existent_file)

        assert error is not None
        assert "インポート中にエラーが発生しました" in error

    @patch('services.data_export_service.get_session')
    def test_import_from_csv_empty_file(self, mock_get_session):
        """異常系: 空のCSVファイル（データ行なし）"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', prefix='patient_info_',
                                        encoding='shift_jis', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'patient_name'])
            temp_path = f.name

        try:
            mock_session = MagicMock()
            mock_get_session.return_value.__enter__.return_value = mock_session

            error = import_from_csv(temp_path)

            assert error is None
            mock_session.add.assert_not_called()
            mock_session.commit.assert_called_once()
        finally:
            os.unlink(temp_path)

    @patch('services.data_export_service.get_session')
    def test_import_from_csv_invalid_date_format(self, mock_get_session):
        """異常系: 日付フォーマットが不正"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', prefix='patient_info_',
                                        encoding='shift_jis', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'patient_id', 'patient_name', 'kana', 'gender', 'birthdate', 'issue_date',
                'issue_date_age', 'doctor_id', 'doctor_name', 'department', 'department_id',
                'main_diagnosis', 'sheet_name', 'creation_count', 'target_weight', 'target_bp',
                'target_hba1c', 'goal1', 'goal2', 'target_achievement', 'diet1', 'diet2',
                'diet3', 'diet4', 'diet_comment', 'exercise_prescription', 'exercise_time',
                'exercise_frequency', 'exercise_intensity', 'daily_activity', 'exercise_comment',
                'nonsmoker', 'smoking_cessation', 'other1', 'other2', 'ophthalmology',
                'dental', 'cancer_screening'
            ])
            writer.writeheader()
            writer.writerow({
                'patient_id': '12345',
                'patient_name': '山田太郎',
                'kana': 'ヤマダタロウ',
                'gender': '男性',
                'birthdate': 'invalid-date',
                'issue_date': '2025-01-01',
                'issue_date_age': '45',
                'doctor_id': '1',
                'doctor_name': '鈴木医師',
                'department': '内科',
                'department_id': '10',
                'main_diagnosis': '糖尿病',
                'sheet_name': '糖尿病',
                'creation_count': '1',
                'target_weight': '70.5',
                'target_bp': '130/80',
                'target_hba1c': '7.0',
                'goal1': '体重減少',
                'goal2': '運動習慣',
                'target_achievement': '3ヶ月',
                'diet1': 'カロリー制限',
                'diet2': '塩分制限',
                'diet3': '',
                'diet4': '',
                'diet_comment': 'バランスの良い食事',
                'exercise_prescription': 'ウォーキング',
                'exercise_time': '30分',
                'exercise_frequency': '週5回',
                'exercise_intensity': '中等度',
                'daily_activity': '通勤時歩行',
                'exercise_comment': '無理のない範囲で',
                'nonsmoker': 'True',
                'smoking_cessation': 'False',
                'other1': '',
                'other2': '',
                'ophthalmology': 'True',
                'dental': 'False',
                'cancer_screening': 'True'
            })
            temp_path = f.name

        try:
            mock_session = MagicMock()
            mock_get_session.return_value.__enter__.return_value = mock_session

            error = import_from_csv(temp_path)

            assert error is not None
            assert "インポート中にエラーが発生しました" in error
        finally:
            os.unlink(temp_path)

    @patch('services.data_export_service.get_session')
    def test_import_from_csv_invalid_integer_format(self, mock_get_session):
        """異常系: 整数フォーマットが不正"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', prefix='patient_info_',
                                        encoding='shift_jis', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'patient_id', 'patient_name', 'kana', 'gender', 'birthdate', 'issue_date',
                'issue_date_age', 'doctor_id', 'doctor_name', 'department', 'department_id',
                'main_diagnosis', 'sheet_name', 'creation_count', 'target_weight', 'target_bp',
                'target_hba1c', 'goal1', 'goal2', 'target_achievement', 'diet1', 'diet2',
                'diet3', 'diet4', 'diet_comment', 'exercise_prescription', 'exercise_time',
                'exercise_frequency', 'exercise_intensity', 'daily_activity', 'exercise_comment',
                'nonsmoker', 'smoking_cessation', 'other1', 'other2', 'ophthalmology',
                'dental', 'cancer_screening'
            ])
            writer.writeheader()
            writer.writerow({
                'patient_id': 'not_a_number',
                'patient_name': '山田太郎',
                'kana': 'ヤマダタロウ',
                'gender': '男性',
                'birthdate': '1980-01-01',
                'issue_date': '2025-01-01',
                'issue_date_age': '45',
                'doctor_id': '1',
                'doctor_name': '鈴木医師',
                'department': '内科',
                'department_id': '10',
                'main_diagnosis': '糖尿病',
                'sheet_name': '糖尿病',
                'creation_count': '1',
                'target_weight': '70.5',
                'target_bp': '130/80',
                'target_hba1c': '7.0',
                'goal1': '体重減少',
                'goal2': '運動習慣',
                'target_achievement': '3ヶ月',
                'diet1': 'カロリー制限',
                'diet2': '塩分制限',
                'diet3': '',
                'diet4': '',
                'diet_comment': 'バランスの良い食事',
                'exercise_prescription': 'ウォーキング',
                'exercise_time': '30分',
                'exercise_frequency': '週5回',
                'exercise_intensity': '中等度',
                'daily_activity': '通勤時歩行',
                'exercise_comment': '無理のない範囲で',
                'nonsmoker': 'True',
                'smoking_cessation': 'False',
                'other1': '',
                'other2': '',
                'ophthalmology': 'True',
                'dental': 'False',
                'cancer_screening': 'True'
            })
            temp_path = f.name

        try:
            mock_session = MagicMock()
            mock_get_session.return_value.__enter__.return_value = mock_session

            error = import_from_csv(temp_path)

            assert error is not None
            assert "インポート中にエラーが発生しました" in error
        finally:
            os.unlink(temp_path)

    @patch('services.data_export_service.get_session')
    def test_import_from_csv_null_target_weight(self, mock_get_session):
        """正常系: target_weightがNullの場合"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', prefix='patient_info_',
                                        encoding='shift_jis', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'patient_id', 'patient_name', 'kana', 'gender', 'birthdate', 'issue_date',
                'issue_date_age', 'doctor_id', 'doctor_name', 'department', 'department_id',
                'main_diagnosis', 'sheet_name', 'creation_count', 'target_weight', 'target_bp',
                'target_hba1c', 'goal1', 'goal2', 'target_achievement', 'diet1', 'diet2',
                'diet3', 'diet4', 'diet_comment', 'exercise_prescription', 'exercise_time',
                'exercise_frequency', 'exercise_intensity', 'daily_activity', 'exercise_comment',
                'nonsmoker', 'smoking_cessation', 'other1', 'other2', 'ophthalmology',
                'dental', 'cancer_screening'
            ])
            writer.writeheader()
            writer.writerow({
                'patient_id': '12345',
                'patient_name': '山田太郎',
                'kana': 'ヤマダタロウ',
                'gender': '男性',
                'birthdate': '1980-01-01',
                'issue_date': '2025-01-01',
                'issue_date_age': '45',
                'doctor_id': '1',
                'doctor_name': '鈴木医師',
                'department': '内科',
                'department_id': '10',
                'main_diagnosis': '糖尿病',
                'sheet_name': '糖尿病',
                'creation_count': '1',
                'target_weight': '',
                'target_bp': '130/80',
                'target_hba1c': '7.0',
                'goal1': '体重減少',
                'goal2': '運動習慣',
                'target_achievement': '3ヶ月',
                'diet1': 'カロリー制限',
                'diet2': '塩分制限',
                'diet3': '',
                'diet4': '',
                'diet_comment': 'バランスの良い食事',
                'exercise_prescription': 'ウォーキング',
                'exercise_time': '30分',
                'exercise_frequency': '週5回',
                'exercise_intensity': '中等度',
                'daily_activity': '通勤時歩行',
                'exercise_comment': '無理のない範囲で',
                'nonsmoker': 'True',
                'smoking_cessation': 'False',
                'other1': '',
                'other2': '',
                'ophthalmology': 'True',
                'dental': 'False',
                'cancer_screening': 'True'
            })
            temp_path = f.name

        try:
            mock_session = MagicMock()
            mock_get_session.return_value.__enter__.return_value = mock_session

            error = import_from_csv(temp_path)

            assert error is None
            mock_session.add.assert_called_once()

            added_patient = mock_session.add.call_args[0][0]
            assert added_patient.target_weight is None
        finally:
            os.unlink(temp_path)

    @patch('services.data_export_service.get_session')
    def test_import_from_csv_database_commit_error(self, mock_get_session, temp_csv_file):
        """異常系: データベースコミットエラー"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.commit.side_effect = Exception("Database commit failed")

        error = import_from_csv(temp_csv_file)

        assert error is not None
        assert "インポート中にエラーが発生しました" in error
        assert "Database commit failed" in error
