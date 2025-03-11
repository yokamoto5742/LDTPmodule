import os
import csv
import re
from datetime import datetime
import pandas as pd
import configparser
from ..models.patient import PatientInfo
from ..database.connection import get_session


class CSVService:
    """
    CSVファイルの読み込み、インポート、エクスポート機能を提供するサービスクラス
    """

    def __init__(self):
        """CSVサービスの初期化"""
        # 設定ファイルの読み込み
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')
        self.csv_file_path = self.config.get('FilePaths', 'patient_data')
        self.export_folder = self.config.get('FilePaths', 'export_folder')

    def load_patient_data(self):
        """
        患者データのCSVファイルを読み込む

        Returns:
            tuple: (エラーメッセージ, DataFrame) - エラーがない場合は最初の要素は空文字列
        """
        try:
            # 日付列の指定（0列目と6列目を日付として読み込む）
            date_columns = [0, 6]
            # 先頭3行のみ読み込む
            nrows = 3

            df = pd.read_csv(
                self.csv_file_path,
                encoding="shift_jis",
                header=None,
                parse_dates=date_columns,
                nrows=nrows
            )
            return "", df

        except (configparser.NoSectionError, configparser.NoOptionError):
            return "エラー: config.iniファイルに'FilePaths'セクションまたは'patient_data'キーが見つかりません。", None
        except Exception as e:
            return f"エラー: {str(e)}", None

    def format_date(self, date_str):
        """
        日付文字列をフォーマットする

        Args:
            date_str: 日付文字列または日付オブジェクト

        Returns:
            str: フォーマットされた日付文字列 (YYYY/MM/DD)
        """
        if pd.isna(date_str):  # pd.isna()で欠損値かどうかを判定
            return ""
        return pd.to_datetime(date_str).strftime("%Y/%m/%d")

    def import_csv(self, file_path):
        """
        CSVファイルからデータをインポートする

        Args:
            file_path (str): インポートするCSVファイルのパス

        Returns:
            tuple: (成功フラグ, メッセージ)
        """
        # ファイル名のバリデーション
        file_name = os.path.basename(file_path)
        if not re.match(r'^patient_info_.*\.csv$', file_name):
            return False, "インポートエラー: このファイルはインポートできません"

        try:
            with open(file_path, 'r', encoding='shift_jis') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                with get_session() as session:
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

            return True, "CSVファイルからデータがインポートされました"

        except Exception as e:
            return False, f"インポート中にエラーが発生しました: {str(e)}"

    def export_to_csv(self):
        """
        患者データをCSVファイルにエクスポートする

        Returns:
            tuple: (成功フラグ, メッセージ, ファイルパス)
        """
        try:
            # CSVファイル名を現在の日時で生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"patient_info_export_{timestamp}.csv"
            csv_path = os.path.join(self.export_folder, csv_filename)

            # エクスポートフォルダが存在しない場合は作成
            os.makedirs(self.export_folder, exist_ok=True)

            # セッションを開始
            with get_session() as session:
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

            return True, f"データがCSVファイル '{csv_filename}' にエクスポートされました", csv_path

        except Exception as e:
            return False, f"エクスポート中にエラーが発生しました: {str(e)}", None

    def check_file_exists(self):
        """
        患者データCSVファイルが存在するかを確認する

        Returns:
            bool: ファイルが存在する場合True、それ以外はFalse
        """
        return os.path.exists(self.csv_file_path)