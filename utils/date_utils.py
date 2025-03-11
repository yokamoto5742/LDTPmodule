import pandas as pd
from datetime import datetime, date


def format_date(date_str):
    """
    日付文字列または日付オブジェクトを指定された形式に変換する

    Args:
        date_str: 変換する日付（文字列、datetime、または pandas Timestamp）

    Returns:
        str: フォーマットされた日付文字列 (YYYY/MM/DD)、または空の文字列（欠損値の場合）
    """
    if pd.isna(date_str):  # pd.isna()で欠損値かどうかを判定
        return ""
    return pd.to_datetime(date_str).strftime("%Y/%m/%d")


def calculate_issue_date_age(birth_date, issue_date):
    """
    生年月日と発行日から年齢を計算する

    Args:
        birth_date: 生年月日（datetime.date または datetime.datetime）
        issue_date: 発行日（datetime.date または datetime.datetime）

    Returns:
        int: 計算された年齢
    """
    # datetimeオブジェクトを確実にdate型に変換
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    if isinstance(issue_date, datetime):
        issue_date = issue_date.date()

    # 年齢計算（誕生日がまだ来ていなければ年齢から1を引く）
    issue_date_age = issue_date.year - birth_date.year
    if issue_date.month < birth_date.month or (
            issue_date.month == birth_date.month and issue_date.day < birth_date.day):
        issue_date_age -= 1

    return issue_date_age


def parse_date(date_str, formats=None):
    """
    様々な形式の日付文字列をdatetime.dateオブジェクトに変換する

    Args:
        date_str: 変換する日付文字列
        formats: 試行する日付フォーマットのリスト（デフォルトは一般的な形式）

    Returns:
        datetime.date: パースされた日付、または None（変換できない場合）
    """
    if not date_str:
        return None

    if formats is None:
        formats = ["%Y/%m/%d", "%Y-%m-%d", "%Y年%m月%d日", "%d/%m/%Y", "%m/%d/%Y"]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    # pandasを使用した日付解析を試みる
    try:
        return pd.to_datetime(date_str).date()
    except (ValueError, TypeError):
        return None


def get_today():
    """
    今日の日付を取得する

    Returns:
        datetime.date: 今日の日付
    """
    return date.today()


def get_age(birth_date):
    """
    生年月日から現在の年齢を計算する

    Args:
        birth_date: 生年月日（datetime.date または datetime.datetime または文字列）

    Returns:
        int: 計算された年齢、または None（計算できない場合）
    """
    if isinstance(birth_date, str):
        birth_date = parse_date(birth_date)

    if not birth_date:
        return None

    today = get_today()
    return calculate_issue_date_age(birth_date, today)


def date_to_str(date_obj, format_str="%Y/%m/%d"):
    """
    datetime.dateオブジェクトを文字列に変換する

    Args:
        date_obj: 変換する日付オブジェクト
        format_str: 出力フォーマット

    Returns:
        str: フォーマットされた日付文字列、または空の文字列（Noneの場合）
    """
    if not date_obj:
        return ""

    return date_obj.strftime(format_str)


def is_valid_date(year, month, day):
    """
    日付が有効かどうかを確認する

    Args:
        year: 年
        month: 月
        day: 日

    Returns:
        bool: 有効な日付であればTrue
    """
    try:
        date(year, month, day)
        return True
    except ValueError:
        return False


def add_months(source_date, months):
    """
    日付に指定された月数を加える

    Args:
        source_date: 元の日付
        months: 加える月数（負の値も可）

    Returns:
        datetime.date: 計算された日付
    """
    if not source_date:
        return None

    # datetimeオブジェクトを確実にdate型に変換
    if isinstance(source_date, datetime):
        source_date = source_date.date()

    # 月の計算
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1

    # 日付の調整（月末を超えないように）
    day = min(source_date.day,
              [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])

    return date(year, month, day)


def is_leap_year(year):
    """
    うるう年かどうかを判定する

    Args:
        year: 年

    Returns:
        bool: うるう年であればTrue
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def get_date_diff_in_days(date1, date2):
    """
    2つの日付の差を日数で取得する

    Args:
        date1: 1つ目の日付
        date2: 2つ目の日付

    Returns:
        int: 日数差（date2 - date1）
    """
    if isinstance(date1, str):
        date1 = parse_date(date1)
    if isinstance(date2, str):
        date2 = parse_date(date2)

    if not date1 or not date2:
        return None

    return (date2 - date1).days


def get_fiscal_year(target_date=None):
    """
    指定された日付の日本の会計年度を取得する

    Args:
        target_date: 対象日付（デフォルトは今日）

    Returns:
        int: 会計年度
    """
    if target_date is None:
        target_date = get_today()

    if isinstance(target_date, str):
        target_date = parse_date(target_date)

    if target_date.month < 4:  # 4月始まりの会計年度
        return target_date.year - 1
    return target_date.year
