from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from utils.file_utils import close_excel_if_needed, format_date


class TestCloseExcelIfNeeded:
    """close_excel_if_needed関数のテスト"""

    @patch('utils.file_utils.pythoncom')
    @patch('utils.file_utils.win32com.client.GetObject')
    def test_close_excel_target_file_open(self, mock_get_object, mock_pythoncom):
        """対象ファイルが開いている場合のテスト"""
        # モックExcelアプリケーション
        mock_excel = MagicMock()
        mock_wb1 = MagicMock()
        mock_wb1.FullName = r'C:\test\file.xlsm'
        mock_wb2 = MagicMock()
        mock_wb2.FullName = r'C:\test\other.xlsm'

        mock_excel.Workbooks = [mock_wb1, mock_wb2]
        mock_get_object.return_value = mock_excel

        # テスト実行
        close_excel_if_needed(r'C:\test\file.xlsm')

        # 検証
        mock_pythoncom.CoInitialize.assert_called_once()
        mock_pythoncom.CoUninitialize.assert_called_once()
        mock_wb1.Close.assert_called_once_with(SaveChanges=False)
        mock_wb2.Close.assert_not_called()

    @patch('utils.file_utils.pythoncom')
    @patch('utils.file_utils.win32com.client.GetObject')
    def test_close_excel_target_file_not_open(self, mock_get_object, mock_pythoncom):
        """対象ファイルが開いていない場合のテスト"""
        # モックExcelアプリケーション
        mock_excel = MagicMock()
        mock_wb1 = MagicMock()
        mock_wb1.FullName = r'C:\test\other1.xlsm'
        mock_wb2 = MagicMock()
        mock_wb2.FullName = r'C:\test\other2.xlsm'

        mock_excel.Workbooks = [mock_wb1, mock_wb2]
        mock_get_object.return_value = mock_excel

        # テスト実行
        close_excel_if_needed(r'C:\test\file.xlsm')

        # 検証
        mock_pythoncom.CoInitialize.assert_called_once()
        mock_pythoncom.CoUninitialize.assert_called_once()
        mock_wb1.Close.assert_not_called()
        mock_wb2.Close.assert_not_called()

    @patch('utils.file_utils.pythoncom')
    @patch('utils.file_utils.win32com.client.GetObject')
    def test_close_excel_no_excel_running(self, mock_get_object, mock_pythoncom):
        """Excelが起動していない場合のテスト"""
        # Excelが起動していないケースをシミュレート
        mock_get_object.side_effect = Exception("Excel not running")

        # テスト実行（例外が発生しないことを確認）
        try:
            close_excel_if_needed(r'C:\test\file.xlsm')
        except Exception:
            pytest.fail("close_excel_if_needed raised Exception unexpectedly!")

        # 検証
        mock_pythoncom.CoInitialize.assert_called_once()
        mock_pythoncom.CoUninitialize.assert_called_once()

    @patch('utils.file_utils.pythoncom')
    @patch('utils.file_utils.win32com.client.GetObject')
    def test_close_excel_relative_path(self, mock_get_object, mock_pythoncom):
        """相対パス指定時のテスト"""
        # モックExcelアプリケーション
        mock_excel = MagicMock()
        mock_wb = MagicMock()
        # 絶対パスとして返す
        mock_wb.FullName = r'C:\Users\yokam\PycharmProjects\LDTPmodule\test.xlsm'

        mock_excel.Workbooks = [mock_wb]
        mock_get_object.return_value = mock_excel

        # テスト実行（相対パスで指定）
        close_excel_if_needed('test.xlsm')

        # 検証
        mock_pythoncom.CoInitialize.assert_called_once()
        mock_pythoncom.CoUninitialize.assert_called_once()

    @patch('utils.file_utils.pythoncom')
    @patch('utils.file_utils.win32com.client.GetObject')
    def test_close_excel_case_insensitive(self, mock_get_object, mock_pythoncom):
        """大文字小文字を区別しないテスト"""
        # モックExcelアプリケーション
        mock_excel = MagicMock()
        mock_wb = MagicMock()
        mock_wb.FullName = r'C:\Test\FILE.XLSM'

        mock_excel.Workbooks = [mock_wb]
        mock_get_object.return_value = mock_excel

        # テスト実行（小文字で指定）
        close_excel_if_needed(r'C:\test\file.xlsm')

        # 検証: 大文字小文字を区別せずにマッチする
        mock_wb.Close.assert_called_once_with(SaveChanges=False)

    @patch('utils.file_utils.pythoncom')
    @patch('utils.file_utils.win32com.client.GetObject')
    def test_close_excel_multiple_workbooks(self, mock_get_object, mock_pythoncom):
        """複数のワークブックが開いている場合のテスト"""
        # モックExcelアプリケーション
        mock_excel = MagicMock()
        workbooks = []
        for i in range(5):
            wb = MagicMock()
            wb.FullName = rf'C:\test\file{i}.xlsm'
            workbooks.append(wb)

        # 対象ファイルを3番目に配置
        workbooks[2].FullName = r'C:\test\target.xlsm'

        mock_excel.Workbooks = workbooks
        mock_get_object.return_value = mock_excel

        # テスト実行
        close_excel_if_needed(r'C:\test\target.xlsm')

        # 検証: 対象ファイルのみが閉じられる
        workbooks[2].Close.assert_called_once_with(SaveChanges=False)
        for i in [0, 1, 3, 4]:
            workbooks[i].Close.assert_not_called()


class TestFormatDate:
    """format_date関数のテスト"""

    def test_format_date_valid_datetime(self):
        """有効な日付文字列のフォーマットテスト"""
        date_str = "2025-01-15"
        result = format_date(date_str)
        assert result == "2025/01/15"

    def test_format_date_with_time(self):
        """時刻付き日付文字列のフォーマットテスト"""
        date_str = "2025-01-15 14:30:00"
        result = format_date(date_str)
        assert result == "2025/01/15"

    def test_format_date_na_value(self):
        """NA値のテスト"""
        result = format_date(pd.NA)
        assert result == ""

    def test_format_date_none_value(self):
        """None値のテスト"""
        result = format_date(None)
        assert result == ""

    def test_format_date_nan_value(self):
        """NaN値のテスト"""
        result = format_date(float('nan'))
        assert result == ""

    def test_format_date_timestamp(self):
        """Timestamp型のテスト"""
        timestamp = pd.Timestamp("2025-03-20")
        result = format_date(timestamp)
        assert result == "2025/03/20"

    def test_format_date_datetime_object(self):
        """datetime型オブジェクトのテスト"""
        dt = datetime(2025, 12, 31, 23, 59, 59)
        result = format_date(dt)
        assert result == "2025/12/31"

    def test_format_date_single_digit_month_day(self):
        """月・日が1桁の場合のテスト"""
        date_str = "2025-1-5"
        result = format_date(date_str)
        assert result == "2025/01/05"

    def test_format_date_different_formats(self):
        """異なる日付フォーマットのテスト"""
        test_cases = [
            ("2025/01/15", "2025/01/15"),
            ("2025.01.15", "2025/01/15"),
            ("01-15-2025", "2025/01/15"),
        ]

        for input_date, expected in test_cases:
            result = format_date(input_date)
            assert result == expected

    @pytest.mark.parametrize("date_str,expected", [
        ("2025-01-01", "2025/01/01"),
        ("2025-12-31", "2025/12/31"),
        ("2025-06-15", "2025/06/15"),
        ("2000-02-29", "2000/02/29"),  # 閏年
    ])
    def test_format_date_parametrized(self, date_str, expected):
        """パラメータ化された日付フォーマットテスト"""
        result = format_date(date_str)
        assert result == expected

    def test_format_date_leap_year(self):
        """閏年のテスト"""
        date_str = "2024-02-29"
        result = format_date(date_str)
        assert result == "2024/02/29"

    def test_format_date_century_boundary(self):
        """世紀の境界のテスト"""
        date_str = "2000-01-01"
        result = format_date(date_str)
        assert result == "2000/01/01"

    def test_format_date_future_date(self):
        """未来の日付のテスト"""
        date_str = "2099-12-31"
        result = format_date(date_str)
        assert result == "2099/12/31"

    def test_format_date_past_century(self):
        """過去の世紀の日付のテスト"""
        date_str = "1900-01-01"
        result = format_date(date_str)
        assert result == "1900/01/01"
