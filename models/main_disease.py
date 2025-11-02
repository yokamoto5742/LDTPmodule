from sqlalchemy import Column, Integer, String

from database import get_base

Base = get_base()


class MainDisease(Base):
    __tablename__ = "main_diseases"
    id = Column(Integer, primary_key=True)
    name = Column(String)  # 主病名
