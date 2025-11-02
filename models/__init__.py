from database import get_base

Base = get_base()

from .main_disease import MainDisease
from .patient_info import PatientInfo
from .sheet_name import SheetName
from .template import Template

__all__ = ['Base', 'PatientInfo', 'MainDisease', 'SheetName', 'Template']
