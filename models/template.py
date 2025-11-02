from sqlalchemy import Column, Integer, String

from database import get_base

Base = get_base()


class Template(Base):
    __tablename__ = 'templates'
    id = Column(Integer, primary_key=True)
    main_disease = Column(String)
    sheet_name = Column(String)
    target_bp = Column(String)
    target_hba1c = Column(String)
    goal1 = Column(String)
    goal2 = Column(String)
    diet1 = Column(String)
    diet2 = Column(String)
    diet3 = Column(String)
    diet4 = Column(String)
    exercise_prescription = Column(String)
    exercise_time = Column(String)
    exercise_frequency = Column(String)
    exercise_intensity = Column(String)
    daily_activity = Column(String)
    other1 = Column(String)
    other2 = Column(String)
