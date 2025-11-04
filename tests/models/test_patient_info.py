from datetime import date

import pytest

from models.patient_info import PatientInfo


@pytest.fixture
def sample_patient_info():
    """テスト用の患者情報サンプルを作成"""
    return PatientInfo(
        patient_id=12345,
        patient_name="山田太郎",
        kana="ヤマダタロウ",
        gender="男",
        birthdate=date(1980, 5, 15),
        issue_date=date(2025, 1, 10),
        issue_date_age=44,
        doctor_id=1001,
        doctor_name="田中医師",
        department="内科",
        department_id=10,
        main_diagnosis="糖尿病",
        creation_count=1,
        target_weight=65.5,
        sheet_name="糖尿病用",
        target_bp="130/80",
        target_hba1c="7.0",
        goal1="体重を減らす",
        goal2="HbA1cを改善する",
        target_achievement="3ヶ月後",
        diet1="野菜を多く摂る",
        diet2="塩分控えめ",
        diet3="間食を減らす",
        diet4="腹八分目",
        diet_comment="バランスの良い食事を心がける",
        exercise_prescription="ウォーキング",
        exercise_time="30分",
        exercise_frequency="週5日",
        exercise_intensity="軽め",
        daily_activity="階段を使う",
        exercise_comment="無理のない範囲で継続する",
        nonsmoker=True,
        smoking_cessation=False,
        other1="定期的な血糖測定",
        other2="",
        ophthalmology=True,
        dental=True,
        cancer_screening=False
    )


class TestPatientInfoModel:
    """PatientInfoモデルのテストクラス"""

    def test_create_patient_info(self, test_db, sample_patient_info):
        """患者情報の作成テスト"""
        test_db.add(sample_patient_info)
        test_db.commit()

        result = test_db.query(PatientInfo).filter_by(patient_id=12345).first()
        assert result is not None
        assert result.patient_name == "山田太郎"
        assert result.kana == "ヤマダタロウ"

    def test_patient_info_fields(self, sample_patient_info):
        """フィールドの検証テスト"""
        assert sample_patient_info.patient_id == 12345
        assert sample_patient_info.gender == "男"
        assert sample_patient_info.birthdate == date(1980, 5, 15)
        assert sample_patient_info.issue_date_age == 44

    def test_patient_info_nullable_fields(self, test_db):
        """NULL許容フィールドのテスト"""
        minimal_patient = PatientInfo(patient_id=99999)
        test_db.add(minimal_patient)
        test_db.commit()

        result = test_db.query(PatientInfo).filter_by(patient_id=99999).first()
        assert result is not None
        assert result.patient_name is None
        assert result.target_weight is None
        assert result.diet_comment is None

    def test_patient_info_boolean_fields(self, sample_patient_info):
        """Boolean型フィールドのテスト"""
        assert sample_patient_info.nonsmoker is True
        assert sample_patient_info.smoking_cessation is False
        assert sample_patient_info.ophthalmology is True
        assert sample_patient_info.dental is True
        assert sample_patient_info.cancer_screening is False

    def test_patient_info_date_fields(self, sample_patient_info):
        """日付フィールドのテスト"""
        assert sample_patient_info.birthdate == date(1980, 5, 15)
        assert sample_patient_info.issue_date == date(2025, 1, 10)

    def test_patient_info_update(self, test_db, sample_patient_info):
        """患者情報の更新テスト"""
        test_db.add(sample_patient_info)
        test_db.commit()

        patient = test_db.query(PatientInfo).filter_by(patient_id=12345).first()
        patient.target_weight = 63.0
        patient.target_hba1c = "6.5"
        test_db.commit()

        updated = test_db.query(PatientInfo).filter_by(patient_id=12345).first()
        assert updated.target_weight == 63.0
        assert updated.target_hba1c == "6.5"

    def test_patient_info_delete(self, test_db, sample_patient_info):
        """患者情報の削除テスト"""
        test_db.add(sample_patient_info)
        test_db.commit()

        patient = test_db.query(PatientInfo).filter_by(patient_id=12345).first()
        test_db.delete(patient)
        test_db.commit()

        result = test_db.query(PatientInfo).filter_by(patient_id=12345).first()
        assert result is None

    def test_patient_info_multiple_records(self, test_db):
        """複数レコードの作成と取得テスト"""
        patient1 = PatientInfo(patient_id=1, patient_name="患者1")
        patient2 = PatientInfo(patient_id=2, patient_name="患者2")
        patient3 = PatientInfo(patient_id=3, patient_name="患者3")

        test_db.add_all([patient1, patient2, patient3])
        test_db.commit()

        results = test_db.query(PatientInfo).all()
        assert len(results) == 3

    def test_patient_info_filter_by_creation_count(self, test_db):
        """作成回数でのフィルタリングテスト"""
        patient1 = PatientInfo(patient_id=1, creation_count=1)
        patient2 = PatientInfo(patient_id=2, creation_count=1)
        patient3 = PatientInfo(patient_id=3, creation_count=2)

        test_db.add_all([patient1, patient2, patient3])
        test_db.commit()

        first_time = test_db.query(PatientInfo).filter_by(creation_count=1).all()
        assert len(first_time) == 2

    def test_patient_info_diet_fields(self, sample_patient_info):
        """食事指導フィールドのテスト"""
        assert sample_patient_info.diet1 == "野菜を多く摂る"
        assert sample_patient_info.diet2 == "塩分控えめ"
        assert sample_patient_info.diet3 == "間食を減らす"
        assert sample_patient_info.diet4 == "腹八分目"
        assert sample_patient_info.diet_comment == "バランスの良い食事を心がける"

    def test_patient_info_exercise_fields(self, sample_patient_info):
        """運動指導フィールドのテスト"""
        assert sample_patient_info.exercise_prescription == "ウォーキング"
        assert sample_patient_info.exercise_time == "30分"
        assert sample_patient_info.exercise_frequency == "週5日"
        assert sample_patient_info.exercise_intensity == "軽め"
        assert sample_patient_info.daily_activity == "階段を使う"
        assert sample_patient_info.exercise_comment == "無理のない範囲で継続する"

    def test_patient_info_float_field(self, sample_patient_info):
        """Float型フィールドのテスト"""
        assert isinstance(sample_patient_info.target_weight, float)
        assert sample_patient_info.target_weight == 65.5
