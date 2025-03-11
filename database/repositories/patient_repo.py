from datetime import datetime
from sqlalchemy import desc
from ...models.patient import PatientInfo
from ..connection import get_session


class PatientRepository:
    """
    患者情報（PatientInfo）へのデータアクセスを提供するリポジトリクラス
    """

    @staticmethod
    def get_by_id(id):
        """
        指定されたIDの患者情報を取得する

        Args:
            id (int): 患者情報のID

        Returns:
            PatientInfo: 該当する患者情報、見つからない場合はNone
        """
        with get_session() as session:
            return session.query(PatientInfo).filter(PatientInfo.id == id).first()

    @staticmethod
    def get_by_patient_id(patient_id):
        """
        指定された患者IDの患者情報を取得する（最新の情報）

        Args:
            patient_id (int): 患者ID

        Returns:
            PatientInfo: 該当する最新の患者情報、見つからない場合はNone
        """
        with get_session() as session:
            return session.query(PatientInfo). \
                filter(PatientInfo.patient_id == patient_id). \
                order_by(desc(PatientInfo.id)).first()

    @staticmethod
    def get_history(patient_id=None):
        """
        患者の治療計画履歴を取得する

        Args:
            patient_id (int, optional): 特定の患者IDでフィルタリングする場合に指定

        Returns:
            list: 患者の治療計画履歴のリスト（辞書形式）
        """
        with get_session() as session:
            query = session.query(
                PatientInfo.id,
                PatientInfo.issue_date,
                PatientInfo.department,
                PatientInfo.doctor_name,
                PatientInfo.main_diagnosis,
                PatientInfo.sheet_name,
                PatientInfo.creation_count
            ).order_by(PatientInfo.patient_id.asc(), PatientInfo.id.desc())

            if patient_id:
                query = query.filter(PatientInfo.patient_id == patient_id)

            # 表示用にデータ整形
            return [{
                "id": str(info.id),
                "issue_date": info.issue_date.strftime("%Y/%m/%d") if info.issue_date else "",
                "department": info.department,
                "doctor_name": info.doctor_name,
                "main_diagnosis": info.main_diagnosis,
                "sheet_name": info.sheet_name,
                "count": info.creation_count
            } for info in query]

    @staticmethod
    def create(patient_info):
        """
        新しい患者情報を作成する

        Args:
            patient_info (PatientInfo): 作成する患者情報オブジェクト

        Returns:
            PatientInfo: 作成された患者情報（IDが設定された状態）
        """
        with get_session() as session:
            session.add(patient_info)
            session.commit()
            session.refresh(patient_info)
            return patient_info

    @staticmethod
    def update(id, update_data):
        """
        既存の患者情報を更新する

        Args:
            id (int): 更新する患者情報のID
            update_data (dict): 更新するフィールドと値の辞書

        Returns:
            PatientInfo: 更新された患者情報、見つからない場合はNone
        """
        with get_session() as session:
            patient_info = session.query(PatientInfo).filter(PatientInfo.id == id).first()
            if patient_info:
                for key, value in update_data.items():
                    setattr(patient_info, key, value)
                session.commit()
                return patient_info
            return None

    @staticmethod
    def delete(id):
        """
        患者情報を削除する

        Args:
            id (int): 削除する患者情報のID

        Returns:
            bool: 削除が成功した場合True、それ以外はFalse
        """
        with get_session() as session:
            patient_info = session.query(PatientInfo).filter(PatientInfo.id == id).first()
            if patient_info:
                session.delete(patient_info)
                session.commit()
                return True
            return False

    @staticmethod
    def calculate_issue_date_age(birth_date, issue_date):
        """
        発行日時点での年齢を計算する

        Args:
            birth_date (datetime.date): 生年月日
            issue_date (datetime.date): 発行日

        Returns:
            int: 発行日時点での年齢
        """
        issue_date_age = issue_date.year - birth_date.year
        if issue_date.month < birth_date.month or (
                issue_date.month == birth_date.month and issue_date.day < birth_date.day):
            issue_date_age -= 1
        return issue_date_age

    @staticmethod
    def copy_latest_plan(patient_id, patient_csv_info):
        """
        最新の治療計画をコピーして新しい計画を作成する

        Args:
            patient_id (int): 患者ID
            patient_csv_info (pandas.Series): CSVから読み込んだ患者情報

        Returns:
            PatientInfo: 作成された新しい患者情報、作成できなかった場合はNone
        """
        with get_session() as session:
            # 最新の患者情報を取得
            patient_info = session.query(PatientInfo). \
                filter(PatientInfo.patient_id == patient_id). \
                order_by(PatientInfo.id.desc()).first()

            if not patient_info:
                return None

            # 新しい計画を作成（前回の内容をベースに）
            patient_info_copy = PatientInfo(
                patient_id=patient_info.patient_id,
                patient_name=patient_info.patient_name,
                kana=patient_info.kana,
                gender=patient_info.gender,
                birthdate=patient_info.birthdate,
                issue_date=datetime.now().date(),
                issue_date_age=patient_info.issue_date_age,
                doctor_id=int(patient_csv_info.iloc[9]),
                doctor_name=patient_csv_info.iloc[10],
                department_id=int(patient_csv_info.iloc[13]),
                department=patient_csv_info.iloc[14],
                main_diagnosis=patient_info.main_diagnosis,
                sheet_name=patient_info.sheet_name,
                creation_count=patient_info.creation_count + 1,
                target_weight=patient_info.target_weight,
                target_bp=patient_info.target_bp,
                target_hba1c=patient_info.target_hba1c,
                goal1=patient_info.goal1,
                goal2=patient_info.goal2,
                target_achievement=patient_info.target_achievement,
                diet1=patient_info.diet1,
                diet2=patient_info.diet2,
                diet3=patient_info.diet3,
                diet4=patient_info.diet4,
                diet_comment=patient_info.diet_comment,
                exercise_prescription=patient_info.exercise_prescription,
                exercise_time=patient_info.exercise_time,
                exercise_frequency=patient_info.exercise_frequency,
                exercise_intensity=patient_info.exercise_intensity,
                daily_activity=patient_info.daily_activity,
                exercise_comment=patient_info.exercise_comment,
                nonsmoker=patient_info.nonsmoker,
                smoking_cessation=patient_info.smoking_cessation,
                other1=patient_info.other1,
                other2=patient_info.other2,
                ophthalmology=patient_info.ophthalmology,
                dental=patient_info.dental,
                cancer_screening=patient_info.cancer_screening
            )
            session.add(patient_info_copy)
            session.commit()
            session.refresh(patient_info_copy)
            return patient_info_copy
