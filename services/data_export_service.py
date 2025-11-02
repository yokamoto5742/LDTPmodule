import csv
import os
import re
from datetime import datetime

from database import get_session_factory
from models import PatientInfo

Session = get_session_factory()


def export_to_csv(export_folder):
    """CSV出力"""
    # CSVファイル名を現在の日時で生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"patient_info_export_{timestamp}.csv"
    csv_path = os.path.join(export_folder, csv_filename)

    # エクスポートフォルダが存在しない場合は作成
    os.makedirs(export_folder, exist_ok=True)

    # セッションを開始
    session = Session()

    try:
        # PatientInfoテーブルからすべてのデータを取得
        patient_data = session.query(PatientInfo).all()

        # CSVファイルを書き込みモードで開く
        with open(csv_path, 'w', newline='', encoding='shift_jis', errors='ignore') as csvfile:
            writer = csv.writer(csvfile)

            # ヘッダー行を書き込む
            writer.writerow([column.name for column in PatientInfo.__table__.columns])

            # データ行を書き込む
            for patient in patient_data:
                writer.writerow([getattr(patient, column.name) for column in PatientInfo.__table__.columns])

        return csv_filename, csv_path, None
    except Exception as e:
        return None, None, str(e)
    finally:
        session.close()


def import_from_csv(file_path):
    """CSV取込"""
    file_name = os.path.basename(file_path)
    if not re.match(r'^patient_info_.*\.csv$', file_name):
        return "インポートエラー:このファイルはインポートできません"

    try:
        with open(file_path, encoding='shift_jis') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            session = Session()
            for row in csv_reader:
                patient_info = PatientInfo(
                    patient_id=int(row['patient_id']),
                    patient_name=row['patient_name'],
                    kana=row['kana'],
                    gender=row['gender'],
                    birthdate=datetime.strptime(row['birthdate'], '%Y-%m-%d').date(),
                    issue_date=datetime.strptime(row['issue_date'], '%Y-%m-%d').date(),
                    issue_date_age=int(row['issue_date_age']),
                    doctor_id=int(row['doctor_id']),
                    doctor_name=row['doctor_name'],
                    department=row['department'],
                    department_id=int(row['department_id']),
                    main_diagnosis=row['main_diagnosis'],
                    sheet_name=row['sheet_name'],
                    creation_count=int(row['creation_count']),
                    target_weight=float(row['target_weight']) if row['target_weight'] else None,
                    target_bp=row['target_bp'],
                    target_hba1c=row['target_hba1c'],
                    goal1=row['goal1'],
                    goal2=row['goal2'],
                    target_achievement=row['target_achievement'],
                    diet1=row['diet1'],
                    diet2=row['diet2'],
                    diet3=row['diet3'],
                    diet4=row['diet4'],
                    diet_comment=row['diet_comment'],
                    exercise_prescription=row['exercise_prescription'],
                    exercise_time=row['exercise_time'],
                    exercise_frequency=row['exercise_frequency'],
                    exercise_intensity=row['exercise_intensity'],
                    daily_activity=row['daily_activity'],
                    exercise_comment=row['exercise_comment'],
                    nonsmoker=row['nonsmoker'] == 'True',
                    smoking_cessation=row['smoking_cessation'] == 'True',
                    other1=row['other1'],
                    other2=row['other2'],
                    ophthalmology=row['ophthalmology'] == 'True',
                    dental=row['dental'] == 'True',
                    cancer_screening=row['cancer_screening'] == 'True'
                )
                session.add(patient_info)
            session.commit()
            session.close()
            return None
    except Exception as e:
        return f"インポート中にエラーが発生しました: {str(e)}"
