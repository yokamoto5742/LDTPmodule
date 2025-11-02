def calculate_issue_date_age(birth_date, issue_date):
    """発行日時点の年齢を計算"""
    issue_date_age = issue_date.year - birth_date.year
    if issue_date.month < birth_date.month or (
            issue_date.month == birth_date.month and issue_date.day < birth_date.day):
        issue_date_age -= 1
    return issue_date_age
