import csv
import os
import re
from datetime import datetime
from typing import Any, Optional, Tuple

from sqlalchemy import Boolean, Date, Float, Integer

from database import get_session
from models import PatientInfo


def _convert_value(column, raw: str) -> Any:
    """CSV文字列をカラム型に応じてPython値に変換"""
    if raw == '' or raw is None:
        # Boolean は空文字を False ではなく None として扱う
        return None

    column_type = column.type
    if isinstance(column_type, Boolean):
        return raw == 'True'
    if isinstance(column_type, Date):
        return datetime.strptime(raw, '%Y-%m-%d').date()
    if isinstance(column_type, Integer):
        return int(raw)
    if isinstance(column_type, Float):
        return float(raw)
    return raw


def export_to_csv(export_folder: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """CSV出力"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"patient_info_export_{timestamp}.csv"
    csv_path = os.path.join(export_folder, csv_filename)
    os.makedirs(export_folder, exist_ok=True)

    try:
        with get_session() as session:
            patient_data = session.query(PatientInfo).all()
            columns = PatientInfo.__table__.columns

            with open(csv_path, 'w', newline='', encoding='shift_jis', errors='ignore') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([column.name for column in columns])
                for patient in patient_data:
                    writer.writerow([getattr(patient, column.name) for column in columns])

        return csv_filename, csv_path, None
    except Exception as e:
        return None, None, str(e)


def import_from_csv(file_path: str) -> Optional[str]:
    """CSV取込"""
    file_name = os.path.basename(file_path)
    if not re.match(r'^patient_info_.*\.csv$', file_name):
        return "インポートエラー:このファイルはインポートできません"

    try:
        columns = [c for c in PatientInfo.__table__.columns if c.name != 'id']
        with open(file_path, encoding='shift_jis') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            with get_session() as session:
                for row in csv_reader:
                    values = {col.name: _convert_value(col, row.get(col.name, '')) for col in columns}
                    session.add(PatientInfo(**values))
                session.commit()
        return None
    except Exception as e:
        return f"インポート中にエラーが発生しました: {str(e)}"
