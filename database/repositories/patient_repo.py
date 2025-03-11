# database/repositories/patient_repo.py
from datetime import datetime
from models.patient import PatientInfo
from database.connection import DatabaseConnection


class PatientRepository:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_by_id(self, id):
        """IDで患者情報を取得"""
        with self.db.get_session() as session:
            return session.query(PatientInfo).filter(PatientInfo.id == id).first()

    def get_by_patient_id(self, patient_id):
        """患者IDで患者情報を取得"""
        with self.db.get_session() as session:
            return session.query(PatientInfo).filter(PatientInfo.patient_id == patient_id).all()

    def get_latest_by_patient_id(self, patient_id):
        """患者IDで最新の患者情報を取得"""
        with self.db.get_session() as session:
            return session.query(PatientInfo).filter(
                PatientInfo.patient_id == patient_id
            ).order_by(PatientInfo.id.desc()).first()

    def create(self, patient_info):
        """患者情報を作成"""
        with self.db.get_session() as session:
            session.add(patient_info)
            session.flush()
            new_id = patient_info.id
            session.commit()
            return new_id

    def update(self, id, data):
        """患者情報を更新"""
        with self.db.get_session() as session:
            patient = session.query(PatientInfo).filter(PatientInfo.id == id).first()
            if patient:
                for key, value in data.items():
                    if hasattr(patient, key):
                        setattr(patient, key, value)
                return True
            return False

    def delete(self, id):
        """患者情報を削除"""
        with self.db.get_session() as session:
            patient = session.query(PatientInfo).filter(PatientInfo.id == id).first()
            if patient:
                session.delete(patient)
                return True
            return False

    def fetch_history(self, patient_id):
        """患者の治療計画履歴を取得"""
        with self.db.get_session() as session:
            query = session.query(
                PatientInfo.id,
                PatientInfo.issue_date,
                PatientInfo.department,
                PatientInfo.doctor_name,
                PatientInfo.main_diagnosis,
                PatientInfo.sheet_name,
                PatientInfo.creation_count
            ).filter(
                PatientInfo.patient_id == patient_id
            ).order_by(
                PatientInfo.id.desc()
            )

            results = query.all()
            return [{
                "id": str(info.id),
                "issue_date": info.issue_date.strftime("%Y/%m/%d") if info.issue_date else "",
                "department": info.department,
                "doctor_name": info.doctor_name,
                "main_diagnosis": info.main_diagnosis,
                "sheet_name": info.sheet_name,
                "count": info.creation_count
            } for info in results]
