from sqlalchemy import Column, Integer, String

from database import get_base

Base = get_base()


class SheetName(Base):
    __tablename__ = "sheet_names"
    id = Column(Integer, primary_key=True)
    main_disease_id = Column(Integer)
    name = Column(String)  # シート名
