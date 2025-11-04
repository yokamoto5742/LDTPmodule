from datetime import date

from models import MainDisease, PatientInfo, SheetName, Template


class TestDatabaseCRUDOperations:
    """データベースのCRUD操作統合テスト"""

    def test_create_patient_info(self, test_db):
        """患者情報の作成テスト"""
        patient = PatientInfo(
            patient_id=1001,
            patient_name="田中太郎",
            kana="タナカタロウ",
            gender="男",
            birthdate=date(1985, 4, 10),
            issue_date=date(2025, 1, 15),
            issue_date_age=39,
            doctor_id=101,
            doctor_name="山田医師",
            department="内科",
            department_id=10,
            main_diagnosis="糖尿病",
            creation_count=1
        )

        test_db.add(patient)
        test_db.commit()

        result = test_db.query(PatientInfo).filter_by(patient_id=1001).first()
        assert result is not None
        assert result.patient_name == "田中太郎"
        assert result.creation_count == 1

    def test_read_patient_info(self, test_db):
        """患者情報の読み込みテスト"""
        # データ準備
        patient = PatientInfo(patient_id=2001, patient_name="佐藤花子")
        test_db.add(patient)
        test_db.commit()

        # 読み込み
        result = test_db.query(PatientInfo).filter_by(patient_id=2001).first()

        assert result is not None
        assert result.patient_name == "佐藤花子"

    def test_update_patient_info(self, test_db):
        """患者情報の更新テスト"""
        # データ準備
        patient = PatientInfo(
            patient_id=3001,
            patient_name="鈴木一郎",
            target_weight=70.0
        )
        test_db.add(patient)
        test_db.commit()

        # 更新
        patient = test_db.query(PatientInfo).filter_by(patient_id=3001).first()
        patient.target_weight = 68.5
        patient.patient_name = "鈴木一郎(更新)"
        test_db.commit()

        # 確認
        updated = test_db.query(PatientInfo).filter_by(patient_id=3001).first()
        assert updated.target_weight == 68.5
        assert updated.patient_name == "鈴木一郎(更新)"

    def test_delete_patient_info(self, test_db):
        """患者情報の削除テスト"""
        # データ準備
        patient = PatientInfo(patient_id=4001, patient_name="高橋次郎")
        test_db.add(patient)
        test_db.commit()

        # 削除
        patient = test_db.query(PatientInfo).filter_by(patient_id=4001).first()
        test_db.delete(patient)
        test_db.commit()

        # 確認
        result = test_db.query(PatientInfo).filter_by(patient_id=4001).first()
        assert result is None

    def test_create_main_disease(self, test_db):
        """主病名マスタの作成テスト"""
        disease = MainDisease(id=1, name="糖尿病")
        test_db.add(disease)
        test_db.commit()

        result = test_db.query(MainDisease).filter_by(id=1).first()
        assert result is not None
        assert result.name == "糖尿病"

    def test_create_sheet_name(self, test_db):
        """シート名マスタの作成テスト"""
        # 主病名を先に作成
        disease = MainDisease(id=1, name="糖尿病")
        test_db.add(disease)
        test_db.commit()

        # シート名を作成
        sheet = SheetName(id=1, name="糖尿病用", main_disease_id=1)
        test_db.add(sheet)
        test_db.commit()

        result = test_db.query(SheetName).filter_by(id=1).first()
        assert result is not None
        assert result.name == "糖尿病用"
        assert result.main_disease_id == 1


class TestDatabaseRelationships:
    """データベースのリレーションシップテスト"""

    def test_sheet_name_main_disease_relationship(self, test_db):
        """シート名と主病名の関連テスト"""
        # 主病名を作成
        disease1 = MainDisease(id=1, name="糖尿病")
        disease2 = MainDisease(id=2, name="高血圧")
        test_db.add_all([disease1, disease2])
        test_db.commit()

        # シート名を作成
        sheet1 = SheetName(id=1, name="糖尿病用", main_disease_id=1)
        sheet2 = SheetName(id=2, name="高血圧用", main_disease_id=2)
        test_db.add_all([sheet1, sheet2])
        test_db.commit()

        # 糖尿病用のシート名を取得
        sheets = test_db.query(SheetName).filter_by(main_disease_id=1).all()
        assert len(sheets) == 1
        assert sheets[0].name == "糖尿病用"

    def test_multiple_patients_same_id(self, test_db):
        """同一患者IDで複数レコードのテスト"""
        patient1 = PatientInfo(
            patient_id=5001,
            patient_name="患者A",
            creation_count=1,
            issue_date=date(2025, 1, 10)
        )
        patient2 = PatientInfo(
            patient_id=5001,
            patient_name="患者A",
            creation_count=2,
            issue_date=date(2025, 2, 15)
        )

        test_db.add_all([patient1, patient2])
        test_db.commit()

        results = test_db.query(PatientInfo).filter_by(patient_id=5001).all()
        assert len(results) == 2


class TestDatabaseQueryOperations:
    """データベースのクエリ操作テスト"""

    def test_query_all_patients(self, test_db):
        """全患者情報の取得テスト"""
        patients = [
            PatientInfo(patient_id=i, patient_name=f"患者{i}")
            for i in range(1, 6)
        ]
        test_db.add_all(patients)
        test_db.commit()

        results = test_db.query(PatientInfo).all()
        assert len(results) == 5

    def test_query_filter_by_department(self, test_db):
        """診療科でフィルタリングテスト"""
        patient1 = PatientInfo(patient_id=1, department="内科")
        patient2 = PatientInfo(patient_id=2, department="外科")
        patient3 = PatientInfo(patient_id=3, department="内科")

        test_db.add_all([patient1, patient2, patient3])
        test_db.commit()

        results = test_db.query(PatientInfo).filter_by(department="内科").all()
        assert len(results) == 2

    def test_query_order_by_issue_date(self, test_db):
        """発行日でソートテスト"""
        patient1 = PatientInfo(
            patient_id=1,
            issue_date=date(2025, 3, 1)
        )
        patient2 = PatientInfo(
            patient_id=2,
            issue_date=date(2025, 1, 1)
        )
        patient3 = PatientInfo(
            patient_id=3,
            issue_date=date(2025, 2, 1)
        )

        test_db.add_all([patient1, patient2, patient3])
        test_db.commit()

        results = test_db.query(PatientInfo).order_by(PatientInfo.issue_date.asc()).all()
        assert results[0].patient_id == 2  # 2025-01-01
        assert results[1].patient_id == 3  # 2025-02-01
        assert results[2].patient_id == 1  # 2025-03-01

    def test_query_count(self, test_db):
        """レコード数カウントテスト"""
        patients = [
            PatientInfo(patient_id=i)
            for i in range(1, 11)
        ]
        test_db.add_all(patients)
        test_db.commit()

        count = test_db.query(PatientInfo).count()
        assert count == 10


class TestDatabaseTransactions:
    """データベーストランザクションテスト"""

    def test_transaction_commit(self, test_db):
        """トランザクションのコミットテスト"""
        patient = PatientInfo(patient_id=1, patient_name="テスト患者")
        test_db.add(patient)
        test_db.commit()

        result = test_db.query(PatientInfo).filter_by(patient_id=1).first()
        assert result is not None

    def test_transaction_rollback(self, test_db):
        """トランザクションのロールバックテスト"""
        patient = PatientInfo(patient_id=2, patient_name="ロールバック患者")
        test_db.add(patient)
        test_db.rollback()

        result = test_db.query(PatientInfo).filter_by(patient_id=2).first()
        assert result is None

    def test_bulk_insert(self, test_db):
        """一括挿入テスト"""
        patients = [
            PatientInfo(patient_id=i, patient_name=f"患者{i}")
            for i in range(1, 101)
        ]
        test_db.add_all(patients)
        test_db.commit()

        count = test_db.query(PatientInfo).count()
        assert count == 100


class TestDatabaseConstraints:
    """データベース制約テスト"""

    def test_nullable_fields(self, test_db):
        """NULL許容フィールドのテスト"""
        # 最小限のデータで作成
        patient = PatientInfo(patient_id=1)
        test_db.add(patient)
        test_db.commit()

        result = test_db.query(PatientInfo).filter_by(patient_id=1).first()
        assert result is not None
        assert result.patient_name is None
        assert result.department is None

    def test_boolean_default_values(self, test_db):
        """Boolean型のデフォルト値テスト"""
        patient = PatientInfo(patient_id=1)
        test_db.add(patient)
        test_db.commit()

        result = test_db.query(PatientInfo).filter_by(patient_id=1).first()
        # Boolean型フィールドはNoneがデフォルト
        assert result.nonsmoker is None
        assert result.smoking_cessation is None


class TestComplexQueries:
    """複雑なクエリのテスト"""

    def test_filter_with_multiple_conditions(self, test_db):
        """複数条件でのフィルタリングテスト"""
        patient1 = PatientInfo(
            patient_id=1,
            department="内科",
            creation_count=1
        )
        patient2 = PatientInfo(
            patient_id=2,
            department="内科",
            creation_count=2
        )
        patient3 = PatientInfo(
            patient_id=3,
            department="外科",
            creation_count=1
        )

        test_db.add_all([patient1, patient2, patient3])
        test_db.commit()

        results = test_db.query(PatientInfo).filter_by(
            department="内科",
            creation_count=1
        ).all()

        assert len(results) == 1
        assert results[0].patient_id == 1

    def test_query_with_date_range(self, test_db):
        """日付範囲でのクエリテスト"""
        patient1 = PatientInfo(patient_id=1, issue_date=date(2025, 1, 10))
        patient2 = PatientInfo(patient_id=2, issue_date=date(2025, 1, 20))
        patient3 = PatientInfo(patient_id=3, issue_date=date(2025, 2, 5))

        test_db.add_all([patient1, patient2, patient3])
        test_db.commit()

        results = test_db.query(PatientInfo).filter(
            PatientInfo.issue_date >= date(2025, 1, 15),
            PatientInfo.issue_date <= date(2025, 1, 31)
        ).all()

        assert len(results) == 1
        assert results[0].patient_id == 2
