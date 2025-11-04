import configparser

import flet as ft
import pandas as pd

from database import get_session, get_session_factory
from models import MainDisease, PatientInfo, SheetName
from utils import config_manager

Session = get_session_factory()


def load_patient_data():
    """患者CSVデータ読み込み"""
    try:
        config_csv = config_manager.load_config()
        csv_file_path = config_csv.get('FilePaths', 'patient_data')

        date_columns = [0, 6]  # 1列目と7列目を日付として読み込む
        nrows = 3  # csvファイルで先頭3行のみ読み込む

        df = pd.read_csv(csv_file_path, encoding="shift_jis", header=None, parse_dates=date_columns, nrows=nrows)
        return "", df

    except (configparser.NoSectionError, configparser.NoOptionError):
        return "エラー: config.iniファイルに'FilePaths'セクションまたは'patient_data'キーが見つかりません。", None
    except Exception as e:
        return f"エラー: {str(e)}", None


def load_main_diseases():
    """主病名マスタ読み込み"""
    with get_session() as session:
        main_diseases = session.query(MainDisease).all()
        return [ft.dropdown.Option(str(disease.name)) for disease in main_diseases]


def load_sheet_names(main_disease=None):
    """シート名マスタ読み込み"""
    with get_session() as session:
        if main_disease:
            sheet_names = session.query(SheetName).filter(SheetName.main_disease_id == main_disease).all()
        else:
            sheet_names = session.query(SheetName).all()
        return [ft.dropdown.Option(str(sheet.name)) for sheet in sheet_names]


def fetch_patient_history(filter_patient_id=None):
    """患者履歴取得"""
    if not filter_patient_id:
        return []

    session_fetch_data = Session()
    query = session_fetch_data.query(PatientInfo.id, PatientInfo.issue_date, PatientInfo.department,
                                     PatientInfo.doctor_name, PatientInfo.main_diagnosis,
                                     PatientInfo.sheet_name, PatientInfo.creation_count). \
        order_by(PatientInfo.patient_id.asc(), PatientInfo.id.desc())

    query = query.filter(PatientInfo.patient_id == filter_patient_id)

    return ({
        "id": str(info.id),
        "issue_date": info.issue_date.strftime("%Y/%m/%d") if info.issue_date else "",
        "department": info.department,
        "doctor_name": info.doctor_name,
        "main_diagnosis": info.main_diagnosis,
        "sheet_name": info.sheet_name,
        "count": info.creation_count
    } for info in query)
