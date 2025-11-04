import pytest

from models.main_disease import MainDisease
from models.sheet_name import SheetName


@pytest.fixture
def sample_sheet_name():
    """テスト用のシート名サンプルを作成"""
    return SheetName(id=1, main_disease_id=10, name="糖尿病用シート")


@pytest.fixture
def sample_main_disease(test_db):
    """テスト用の主病名を作成"""
    disease = MainDisease(id=10, name="糖尿病")
    test_db.add(disease)
    test_db.commit()
    return disease


class TestSheetNameModel:
    """SheetNameモデルのテストクラス"""

    def test_create_sheet_name(self, test_db, sample_sheet_name):
        """シート名の作成テスト"""
        # Arrange & Act
        test_db.add(sample_sheet_name)
        test_db.commit()

        # Assert
        result = test_db.query(SheetName).filter_by(id=1).first()
        assert result is not None
        assert result.name == "糖尿病用シート"
        assert result.main_disease_id == 10

    def test_sheet_name_fields(self, sample_sheet_name):
        """フィールドの検証"""
        # Assert
        assert sample_sheet_name.id == 1
        assert sample_sheet_name.main_disease_id == 10
        assert sample_sheet_name.name == "糖尿病用シート"

    def test_sheet_name_with_main_disease_id(self, test_db, sample_main_disease):
        """main_disease_idとの関連テスト"""
        # Arrange
        sheet = SheetName(id=1, main_disease_id=10, name="テストシート")

        # Act
        test_db.add(sheet)
        test_db.commit()

        # Assert
        result = test_db.query(SheetName).filter_by(id=1).first()
        assert result is not None
        assert result.main_disease_id == 10
        disease = test_db.query(MainDisease).filter_by(id=10).first()
        assert disease is not None
        assert disease.name == "糖尿病"

    def test_sheet_name_filter_by_main_disease_id(self, test_db, sample_main_disease):
        """main_disease_idでのフィルタリングテスト"""
        # Arrange
        sheet1 = SheetName(id=1, main_disease_id=10, name="シート1")
        sheet2 = SheetName(id=2, main_disease_id=10, name="シート2")
        sheet3 = SheetName(id=3, main_disease_id=20, name="シート3")
        test_db.add_all([sheet1, sheet2, sheet3])
        test_db.commit()

        # Act
        results = test_db.query(SheetName).filter_by(main_disease_id=10).all()

        # Assert
        assert len(results) == 2
        assert all(sheet.main_disease_id == 10 for sheet in results)

    def test_sheet_name_multiple_sheets_for_same_disease(self, test_db, sample_main_disease):
        """同じ疾病に対する複数シートのテスト"""
        # Arrange
        sheet1 = SheetName(id=1, main_disease_id=10, name="シート1")
        sheet2 = SheetName(id=2, main_disease_id=10, name="シート2")
        sheet3 = SheetName(id=3, main_disease_id=10, name="シート3")

        # Act
        test_db.add_all([sheet1, sheet2, sheet3])
        test_db.commit()

        # Assert
        results = test_db.query(SheetName).filter_by(main_disease_id=10).all()
        assert len(results) == 3
        assert results[0].name == "シート1"
        assert results[1].name == "シート2"
        assert results[2].name == "シート3"

    def test_sheet_name_update(self, test_db, sample_sheet_name):
        """更新テスト"""
        # Arrange
        test_db.add(sample_sheet_name)
        test_db.commit()

        # Act
        sheet = test_db.query(SheetName).filter_by(id=1).first()
        sheet.name = "変更後シート名"
        sheet.main_disease_id = 20
        test_db.commit()

        # Assert
        updated = test_db.query(SheetName).filter_by(id=1).first()
        assert updated.name == "変更後シート名"
        assert updated.main_disease_id == 20

    def test_sheet_name_delete(self, test_db, sample_sheet_name):
        """削除テスト"""
        # Arrange
        test_db.add(sample_sheet_name)
        test_db.commit()

        # Act
        sheet = test_db.query(SheetName).filter_by(id=1).first()
        test_db.delete(sheet)
        test_db.commit()

        # Assert
        result = test_db.query(SheetName).filter_by(id=1).first()
        assert result is None

    def test_sheet_name_nullable_fields(self, test_db):
        """NULL制約のテスト"""
        # Arrange
        sheet = SheetName(id=99)

        # Act
        test_db.add(sheet)
        test_db.commit()

        # Assert
        result = test_db.query(SheetName).filter_by(id=99).first()
        assert result is not None
        assert result.main_disease_id is None
        assert result.name is None

    def test_sheet_name_query_by_name(self, test_db):
        """シート名での検索テスト"""
        # Arrange
        sheet1 = SheetName(id=1, main_disease_id=10, name="糖尿病用")
        sheet2 = SheetName(id=2, main_disease_id=20, name="高血圧用")
        test_db.add_all([sheet1, sheet2])
        test_db.commit()

        # Act
        result = test_db.query(SheetName).filter_by(name="糖尿病用").first()

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.main_disease_id == 10

    def test_sheet_name_empty_name(self, test_db):
        """空文字列のシート名テスト"""
        # Arrange
        sheet = SheetName(id=1, main_disease_id=10, name="")

        # Act
        test_db.add(sheet)
        test_db.commit()

        # Assert
        result = test_db.query(SheetName).filter_by(id=1).first()
        assert result is not None
        assert result.name == ""

    def test_sheet_name_count_by_disease(self, test_db):
        """疾病IDごとのシート数カウントテスト"""
        # Arrange
        sheets = [
            SheetName(id=1, main_disease_id=10, name="シート1"),
            SheetName(id=2, main_disease_id=10, name="シート2"),
            SheetName(id=3, main_disease_id=20, name="シート3"),
            SheetName(id=4, main_disease_id=20, name="シート4"),
            SheetName(id=5, main_disease_id=20, name="シート5"),
        ]
        test_db.add_all(sheets)
        test_db.commit()

        # Act
        count_10 = test_db.query(SheetName).filter_by(main_disease_id=10).count()
        count_20 = test_db.query(SheetName).filter_by(main_disease_id=20).count()

        # Assert
        assert count_10 == 2
        assert count_20 == 3

    def test_sheet_name_order_by_id(self, test_db):
        """ID順でのソートテスト"""
        # Arrange
        sheet1 = SheetName(id=3, main_disease_id=10, name="シート3")
        sheet2 = SheetName(id=1, main_disease_id=10, name="シート1")
        sheet3 = SheetName(id=2, main_disease_id=10, name="シート2")
        test_db.add_all([sheet1, sheet2, sheet3])
        test_db.commit()

        # Act
        results = test_db.query(SheetName).order_by(SheetName.id).all()

        # Assert
        assert len(results) == 3
        assert results[0].id == 1
        assert results[1].id == 2
        assert results[2].id == 3

    def test_sheet_name_filter_multiple_conditions(self, test_db):
        """複数条件でのフィルタテスト"""
        # Arrange
        sheet1 = SheetName(id=1, main_disease_id=10, name="共通名")
        sheet2 = SheetName(id=2, main_disease_id=20, name="共通名")
        sheet3 = SheetName(id=3, main_disease_id=10, name="別名")
        test_db.add_all([sheet1, sheet2, sheet3])
        test_db.commit()

        # Act
        result = test_db.query(SheetName).filter_by(main_disease_id=10, name="共通名").first()

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.main_disease_id == 10
        assert result.name == "共通名"

    def test_sheet_name_long_name(self, test_db):
        """長いシート名のテスト"""
        # Arrange
        long_name = "非常に長いシート名" * 10
        sheet = SheetName(id=1, main_disease_id=10, name=long_name)

        # Act
        test_db.add(sheet)
        test_db.commit()

        # Assert
        result = test_db.query(SheetName).filter_by(id=1).first()
        assert result is not None
        assert result.name == long_name

    def test_sheet_name_different_diseases_same_name(self, test_db):
        """異なる疾病で同じシート名のテスト"""
        # Arrange
        sheet1 = SheetName(id=1, main_disease_id=10, name="標準シート")
        sheet2 = SheetName(id=2, main_disease_id=20, name="標準シート")
        test_db.add_all([sheet1, sheet2])
        test_db.commit()

        # Act
        results = test_db.query(SheetName).filter_by(name="標準シート").all()

        # Assert
        assert len(results) == 2
        assert results[0].main_disease_id != results[1].main_disease_id
