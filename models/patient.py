"""
患者情報を表すモデルを提供するモジュール
"""
from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from .base import Base


class PatientInfo(Base):
    """
    患者情報モデル

    生活習慣病療養計画書に関連する患者情報を格納するモデルクラス
    """
    __tablename__ = 'patient_info'

    # 基本情報
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer)
    patient_name = Column(String)
    kana = Column(String)
    gender = Column(String)
    birthdate = Column(Date)
    issue_date = Column(Date)
    issue_date_age = Column(Integer)

    # 医師・診療科情報
    doctor_id = Column(Integer)
    doctor_name = Column(String)
    department = Column(String)
    department_id = Column(Integer)

    # 診断・計画情報
    main_diagnosis = Column(String)
    creation_count = Column(Integer)
    target_weight = Column(Float)
    sheet_name = Column(String)

    # 目標情報
    target_bp = Column(String)
    target_hba1c = Column(String)
    goal1 = Column(String)
    goal2 = Column(String)
    target_achievement = Column(String)

    # 食事指導情報
    diet1 = Column(String)
    diet2 = Column(String)
    diet3 = Column(String)
    diet4 = Column(String)
    diet_comment = Column(String)

    # 運動指導情報
    exercise_prescription = Column(String)
    exercise_time = Column(String)
    exercise_frequency = Column(String)
    exercise_intensity = Column(String)
    daily_activity = Column(String)
    exercise_comment = Column(String)

    # 生活習慣関連情報
    nonsmoker = Column(Boolean)
    smoking_cessation = Column(Boolean)
    other1 = Column(String)
    other2 = Column(String)

    # 受診勧奨情報
    ophthalmology = Column(Boolean)
    dental = Column(Boolean)
    cancer_screening = Column(Boolean)
