import pytest

from models.main_disease import MainDisease


@pytest.fixture
def sample_main_disease():
    """テスト用の主病名サンプルを作成"""
    return MainDisease(id=1, name="糖尿病")


class TestMainDiseaseModel:
    """MainDiseaseモデルのテストクラス"""

    def test_create_main_disease(self, test_db, sample_main_disease):
        """主病名の作成テスト"""
        # Arrange & Act
        test_db.add(sample_main_disease)
        test_db.commit()

        # Assert
        result = test_db.query(MainDisease).filter_by(id=1).first()
        assert result is not None
        assert result.name == "糖尿病"

    def test_main_disease_fields(self, sample_main_disease):
        """フィールドの検証"""
        # Assert
        assert sample_main_disease.id == 1
        assert sample_main_disease.name == "糖尿病"

    def test_main_disease_nullable_fields(self, test_db):
        """NULL制約のテスト"""
        # Arrange
        disease = MainDisease(id=99)

        # Act
        test_db.add(disease)
        test_db.commit()

        # Assert
        result = test_db.query(MainDisease).filter_by(id=99).first()
        assert result is not None
        assert result.name is None

    def test_main_disease_update(self, test_db, sample_main_disease):
        """更新テスト"""
        # Arrange
        test_db.add(sample_main_disease)
        test_db.commit()

        # Act
        disease = test_db.query(MainDisease).filter_by(id=1).first()
        disease.name = "高血圧"
        test_db.commit()

        # Assert
        updated = test_db.query(MainDisease).filter_by(id=1).first()
        assert updated.name == "高血圧"

    def test_main_disease_delete(self, test_db, sample_main_disease):
        """削除テスト"""
        # Arrange
        test_db.add(sample_main_disease)
        test_db.commit()

        # Act
        disease = test_db.query(MainDisease).filter_by(id=1).first()
        test_db.delete(disease)
        test_db.commit()

        # Assert
        result = test_db.query(MainDisease).filter_by(id=1).first()
        assert result is None

    def test_main_disease_multiple_records(self, test_db):
        """複数レコードの作成と取得"""
        # Arrange
        disease1 = MainDisease(id=1, name="糖尿病")
        disease2 = MainDisease(id=2, name="高血圧")
        disease3 = MainDisease(id=3, name="脂質異常症")

        # Act
        test_db.add_all([disease1, disease2, disease3])
        test_db.commit()

        # Assert
        results = test_db.query(MainDisease).all()
        assert len(results) == 3
        assert results[0].name == "糖尿病"
        assert results[1].name == "高血圧"
        assert results[2].name == "脂質異常症"

    def test_main_disease_query_by_name(self, test_db):
        """病名での検索テスト"""
        # Arrange
        disease1 = MainDisease(id=1, name="糖尿病")
        disease2 = MainDisease(id=2, name="高血圧")
        test_db.add_all([disease1, disease2])
        test_db.commit()

        # Act
        result = test_db.query(MainDisease).filter_by(name="糖尿病").first()

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.name == "糖尿病"

    def test_main_disease_empty_name(self, test_db):
        """空文字列の病名テスト"""
        # Arrange
        disease = MainDisease(id=1, name="")

        # Act
        test_db.add(disease)
        test_db.commit()

        # Assert
        result = test_db.query(MainDisease).filter_by(id=1).first()
        assert result is not None
        assert result.name == ""

    def test_main_disease_long_name(self, test_db):
        """長い病名のテスト"""
        # Arrange
        long_name = "非常に長い病名" * 10
        disease = MainDisease(id=1, name=long_name)

        # Act
        test_db.add(disease)
        test_db.commit()

        # Assert
        result = test_db.query(MainDisease).filter_by(id=1).first()
        assert result is not None
        assert result.name == long_name

    def test_main_disease_count(self, test_db):
        """レコード数のカウントテスト"""
        # Arrange
        diseases = [MainDisease(id=i, name=f"病名{i}") for i in range(1, 6)]
        test_db.add_all(diseases)
        test_db.commit()

        # Act
        count = test_db.query(MainDisease).count()

        # Assert
        assert count == 5

    def test_main_disease_order_by_id(self, test_db):
        """ID順でのソートテスト"""
        # Arrange
        disease1 = MainDisease(id=3, name="病名3")
        disease2 = MainDisease(id=1, name="病名1")
        disease3 = MainDisease(id=2, name="病名2")
        test_db.add_all([disease1, disease2, disease3])
        test_db.commit()

        # Act
        results = test_db.query(MainDisease).order_by(MainDisease.id).all()

        # Assert
        assert len(results) == 3
        assert results[0].id == 1
        assert results[1].id == 2
        assert results[2].id == 3

    def test_main_disease_filter_multiple_conditions(self, test_db):
        """複数条件でのフィルタテスト"""
        # Arrange
        disease1 = MainDisease(id=1, name="糖尿病")
        disease2 = MainDisease(id=2, name="糖尿病")
        disease3 = MainDisease(id=3, name="高血圧")
        test_db.add_all([disease1, disease2, disease3])
        test_db.commit()

        # Act
        result = test_db.query(MainDisease).filter_by(id=1, name="糖尿病").first()

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.name == "糖尿病"
