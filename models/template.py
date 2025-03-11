from sqlalchemy import Column, Integer, String, ForeignKey
from models.base import Base


class MainDisease(Base):
    """主病名のマスターテーブル"""
    __tablename__ = "main_diseases"

    id = Column(Integer, primary_key=True)
    name = Column(String)  # 主病名


class SheetName(Base):
    """シート名のマスターテーブル（主病名と関連付け）"""
    __tablename__ = "sheet_names"

    id = Column(Integer, primary_key=True)
    main_disease_id = Column(Integer)  # 主病名IDへの参照
    name = Column(String)  # シート名


class Template(Base):
    """治療計画書のテンプレート情報"""
    __tablename__ = 'templates'

    id = Column(Integer, primary_key=True)
    main_disease = Column(String)  # 主病名
    sheet_name = Column(String)  # シート名

    # 目標情報
    target_bp = Column(String)  # 目標血圧
    target_hba1c = Column(String)  # 目標HbA1c
    goal1 = Column(String)  # 達成目標
    goal2 = Column(String)  # 行動目標

    # 食事指導情報
    diet1 = Column(String)
    diet2 = Column(String)
    diet3 = Column(String)
    diet4 = Column(String)

    # 運動指導情報
    exercise_prescription = Column(String)  # 運動処方
    exercise_time = Column(String)  # 運動時間
    exercise_frequency = Column(String)  # 運動頻度
    exercise_intensity = Column(String)  # 運動強度
    daily_activity = Column(String)  # 日常活動量

    # その他の指導情報
    other1 = Column(String)
    other2 = Column(String)


class TemplateManager:
    """テンプレートを管理するクラス"""

    def __init__(self):
        """テンプレートマネージャーを初期化"""
        self.templates = {}

    def get_template(self, main_disease, sheet_name):
        """指定された主病名とシート名のテンプレートを取得"""
        return self.templates.get((main_disease, sheet_name))
