import os
import time

import pandas as pd
import pythoncom
import win32com.client


def close_excel_if_needed(target_path):
    """特定のExcelファイルが開いているか確認し必要なら閉じる"""
    target_path = os.path.abspath(target_path).lower()

    try:
        # COMオブジェクトの初期化
        pythoncom.CoInitialize()
        excel = win32com.client.GetObject('Excel.Application')

        # 開いているワークブックをチェック
        for wb in excel.Workbooks:
            if os.path.abspath(wb.FullName).lower() == target_path:
                wb.Close(SaveChanges=False)
                time.sleep(0.1)
                break

    except:
        pass
    finally:
        pythoncom.CoUninitialize()


def format_date(date_str):
    """日付文字列をYYYY/MM/DD形式にフォーマット"""
    if pd.isna(date_str):
        return ""
    return pd.to_datetime(date_str).strftime("%Y/%m/%d")
