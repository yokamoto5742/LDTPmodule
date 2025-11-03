from datetime import date

import pytest

from utils.date_utils import calculate_issue_date_age


class TestCalculateIssueDateAge:
    """calculate_issue_date_age関数のテスト"""

    def test_calculate_age_same_month_day(self):
        """誕生日と発行日が同月同日の場合のテスト"""
        birth_date = date(1980, 5, 15)
        issue_date = date(2025, 5, 15)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 45

    def test_calculate_age_before_birthday(self):
        """発行日が誕生日前の場合のテスト"""
        birth_date = date(1980, 5, 15)
        issue_date = date(2025, 5, 14)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 44

    def test_calculate_age_after_birthday(self):
        """発行日が誕生日後の場合のテスト"""
        birth_date = date(1980, 5, 15)
        issue_date = date(2025, 5, 16)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 45

    def test_calculate_age_same_month_before_day(self):
        """同月だが日が誕生日前の場合のテスト"""
        birth_date = date(1980, 12, 25)
        issue_date = date(2025, 12, 24)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 44

    def test_calculate_age_same_month_after_day(self):
        """同月で日が誕生日後の場合のテスト"""
        birth_date = date(1980, 12, 25)
        issue_date = date(2025, 12, 26)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 45

    def test_calculate_age_before_birthday_month(self):
        """誕生月より前の月の場合のテスト"""
        birth_date = date(1980, 6, 15)
        issue_date = date(2025, 5, 20)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 44

    def test_calculate_age_after_birthday_month(self):
        """誕生月より後の月の場合のテスト"""
        birth_date = date(1980, 6, 15)
        issue_date = date(2025, 7, 10)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 45

    def test_calculate_age_year_boundary(self):
        """年末年始をまたぐケースのテスト"""
        birth_date = date(1980, 12, 31)
        issue_date = date(2025, 1, 1)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 44

    def test_calculate_age_leap_year_born(self):
        """閏年生まれのテスト"""
        birth_date = date(1980, 2, 29)
        issue_date = date(2025, 3, 1)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 45

    def test_calculate_age_leap_year_before_birthday(self):
        """閏年で誕生日前のテスト"""
        birth_date = date(1980, 2, 29)
        issue_date = date(2025, 2, 28)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 44

    def test_calculate_age_zero_years(self):
        """0歳のテスト"""
        birth_date = date(2025, 1, 1)
        issue_date = date(2025, 6, 1)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 0

    def test_calculate_age_100_years_old(self):
        """100歳のテスト"""
        birth_date = date(1925, 1, 1)
        issue_date = date(2025, 1, 2)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 100

    @pytest.mark.parametrize("birth_date,issue_date,expected_age", [
        (date(1990, 3, 20), date(2025, 3, 20), 35),
        (date(1990, 3, 20), date(2025, 3, 19), 34),
        (date(1990, 3, 20), date(2025, 3, 21), 35),
        (date(1985, 12, 31), date(2025, 12, 31), 40),
        (date(1985, 12, 31), date(2025, 12, 30), 39),
        (date(2000, 1, 1), date(2025, 1, 1), 25),
        (date(2000, 1, 1), date(2024, 12, 31), 24),
    ])
    def test_calculate_age_parametrized(self, birth_date, issue_date, expected_age):
        """パラメータ化された年齢計算テスト"""
        age = calculate_issue_date_age(birth_date, issue_date)
        assert age == expected_age

    def test_calculate_age_january_1st_birthday(self):
        """1月1日生まれのテスト"""
        birth_date = date(1980, 1, 1)
        issue_date = date(2025, 1, 1)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 45

    def test_calculate_age_december_31st_birthday(self):
        """12月31日生まれのテスト"""
        birth_date = date(1980, 12, 31)
        issue_date = date(2025, 12, 31)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 45

    def test_calculate_age_early_month_late_day(self):
        """月初生まれ、月末発行のテスト"""
        birth_date = date(1980, 3, 5)
        issue_date = date(2025, 3, 30)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 45

    def test_calculate_age_late_month_early_day(self):
        """月末生まれ、月初発行のテスト"""
        birth_date = date(1980, 3, 25)
        issue_date = date(2025, 3, 1)

        age = calculate_issue_date_age(birth_date, issue_date)

        assert age == 44
