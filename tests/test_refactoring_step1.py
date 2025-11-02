"""
リファクタリングステップ1の動作確認テスト
"""
import sys
from datetime import date

import pandas as pd

from database import get_base, get_engine, get_session
from utils import calculate_issue_date_age, format_date

# Windows環境での日本語出力のためのエンコーディング設定
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def test_database_connection():
    """データベース接続のテスト"""
    print("Testing database connection...")
    engine = get_engine()
    assert engine is not None, "Engine should not be None"
    print("[OK] Database engine created successfully")


def test_base_creation():
    """Baseクラスの取得テスト"""
    print("Testing Base class...")
    Base = get_base()
    assert Base is not None, "Base should not be None"
    print("[OK] Base class obtained successfully")


def test_session_context_manager():
    """セッションコンテキストマネージャのテスト"""
    print("Testing session context manager...")
    with get_session() as session:
        assert session is not None, "Session should not be None"
        print("[OK] Session created successfully")
    print("[OK] Session closed successfully")


def test_calculate_issue_date_age():
    """年齢計算関数のテスト"""
    print("Testing calculate_issue_date_age...")

    # テストケース1: 誕生日前
    birth_date = date(1990, 6, 15)
    issue_date = date(2025, 3, 10)
    age = calculate_issue_date_age(birth_date, issue_date)
    assert age == 34, f"Expected 34, got {age}"
    print(f"[OK] Test case 1: age={age} (birth before issue date)")

    # テストケース2: 誕生日後
    birth_date = date(1990, 6, 15)
    issue_date = date(2025, 8, 20)
    age = calculate_issue_date_age(birth_date, issue_date)
    assert age == 35, f"Expected 35, got {age}"
    print(f"[OK] Test case 2: age={age} (birth after issue date)")

    # テストケース3: 誕生日当日
    birth_date = date(1990, 6, 15)
    issue_date = date(2025, 6, 15)
    age = calculate_issue_date_age(birth_date, issue_date)
    assert age == 35, f"Expected 35, got {age}"
    print(f"[OK] Test case 3: age={age} (same day)")


def test_format_date():
    """日付フォーマット関数のテスト"""
    print("Testing format_date...")

    # テストケース1: 通常の日付
    date_str = "2025-03-15"
    formatted = format_date(date_str)
    assert formatted == "2025/03/15", f"Expected '2025/03/15', got '{formatted}'"
    print(f"[OK] Test case 1: {formatted}")

    # テストケース2: NaN
    formatted = format_date(pd.NaT)
    assert formatted == "", f"Expected empty string, got '{formatted}'"
    print(f"[OK] Test case 2: NaN handled correctly")


def main():
    """すべてのテストを実行"""
    print("=" * 50)
    print("リファクタリングステップ1 動作確認テスト")
    print("=" * 50)

    tests = [
        test_database_connection,
        test_base_creation,
        test_session_context_manager,
        test_calculate_issue_date_age,
        test_format_date,
    ]

    for test in tests:
        print()
        try:
            test()
        except Exception as e:
            print(f"[NG] Test failed: {e}")
            raise

    print()
    print("=" * 50)
    print("すべてのテストが成功しました！")
    print("=" * 50)


if __name__ == "__main__":
    main()
