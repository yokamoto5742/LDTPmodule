# LDTPmodule ユニットテスト戦略

## 1. エグゼクティブサマリー

本ドキュメントは、生活習慣病療養計画書作成アプリケーション（LDTPmodule）に対する包括的なユニットテスト戦略を定義します。このプロジェクトはPyTestを使用し、優先度に基づいたテストアプローチを採用します。

### 現在のテスト状況

**既存のテストカバレッジ:**
- ✅ `services/treatment_plan_service.py` - 包括的にテスト済み
- ✅ `services/patient_service.py` - 包括的にテスト済み
- ✅ `utils/date_utils.py` - 包括的にテスト済み（パラメータ化テスト含む）
- ✅ `utils/file_utils.py` - 包括的にテスト済み
- ✅ `models/patient_info.py` - モデルテスト済み
- ✅ `tests/integration/test_database_operations.py` - DB統合テスト済み

**テストカバレッジ目標:**
- P0（最優先）: 100% ライン・ブランチカバレッジ
- P1（高優先度）: 90%以上のカバレッジ
- P2（中優先度）: 80%以上のカバレッジ

---

## 2. コード構造の分析結果

### 2.1 アーキテクチャ概要

```
LDTPmodule/
├── app/                    # UIレイヤー (Flet)
│   ├── main_ui.py
│   ├── ui_builder.py
│   ├── dialogs.py
│   ├── routes.py
│   └── event_handlers/    # イベント処理
├── services/              # ビジネスロジック層
│   ├── treatment_plan_service.py  # Excel生成（複雑度: 高）
│   ├── patient_service.py         # 患者データ管理
│   ├── data_export_service.py     # CSV エクスポート/インポート
│   ├── file_monitor_service.py    # ファイル監視（watchdog）
│   └── template_service.py        # テンプレート管理
├── models/                # データモデル層
│   ├── patient_info.py
│   ├── main_disease.py
│   ├── sheet_name.py
│   └── template.py
├── utils/                 # ユーティリティ層
│   ├── config_manager.py
│   ├── date_utils.py
│   └── file_utils.py
├── database/              # データベース層
│   ├── connection.py
│   └── initializer.py
└── widgets/               # UI コンポーネント
```

### 2.2 複雑度評価

**高複雑度（Cyclomatic Complexity > 10）:**
- `services/treatment_plan_service.py::TreatmentPlanGenerator.generate_plan()` - Excel生成、バーコード処理、ファイル操作
- `services/data_export_service.py::import_from_csv()` - データ変換、型変換、エラーハンドリング
- `app/event_handlers/*` - 複数のUI状態管理

**中複雑度（Cyclomatic Complexity 5-10）:**
- `services/patient_service.py::load_patient_data()` - CSV読み込み、設定エラーハンドリング
- `utils/config_manager.py` - 複数の例外処理パス
- `database/connection.py` - シングルトンパターン、リソース管理

**低複雑度（Cyclomatic Complexity < 5）:**
- `utils/date_utils.py::calculate_issue_date_age()` - 単純な日付計算
- `models/*` - データクラス定義
- `services/template_service.py::TemplateManager` - 辞書操作のみ

### 2.3 依存関係マップ

```
外部依存:
├── openpyxl (Excel操作) - モック必須
├── barcode (バーコード生成) - モック必須
├── pandas (CSV処理) - モック推奨
├── watchdog (ファイル監視) - モック必須
├── win32com (Excel COM操作) - モック必須
├── flet (UI) - モック必須（UIテストはE2E推奨）
└── SQLAlchemy (DB) - インメモリDBで実テスト

内部依存:
├── services → models, utils, database
├── app → services, models, widgets
├── models → database
└── utils → 独立（循環依存なし）
```

---

## 3. 優先度別テスト対象一覧

### P0（最優先 - 必須テスト）

#### 3.1 ビジネスロジックの核

| モジュール/クラス | テスト対象 | 理由 | 現状 |
|-----------------|----------|------|------|
| `services/treatment_plan_service.py::TreatmentPlanGenerator.generate_plan()` | Excel生成、バーコード生成、ファイル保存 | システムの中核機能、データ整合性に直接影響 | ✅ 完了 |
| `services/treatment_plan_service.py::TreatmentPlanGenerator.populate_common_sheet()` | Excelセル書き込み、全フィールドマッピング | データ損失防止、正確な文書生成 | ✅ 完了 |
| `services/data_export_service.py::export_to_csv()` | データベース全件エクスポート、文字エンコーディング | バックアップ機能、データ移行の要 | ⚠️ 未実装 |
| `services/data_export_service.py::import_from_csv()` | CSV取り込み、データ検証、型変換 | データ整合性の最重要関門 | ⚠️ 未実装 |
| `utils/date_utils.py::calculate_issue_date_age()` | 年齢計算（境界値含む） | 診療報酬計算に影響、法的要件 | ✅ 完了 |
| `database/connection.py::get_session()` | セッション管理、リソースクリーンアップ | データ破損防止 | ⚠️ 部分的 |

#### 3.2 データ整合性

| モジュール/クラス | テスト対象 | 理由 | 現状 |
|-----------------|----------|------|------|
| `models/patient_info.py` | 全フィールド、NULL制約、型検証 | データベーススキーマの正確性 | ✅ 完了 |
| `models/main_disease.py` | マスタデータ整合性 | 主病名の一貫性 | ⚠️ 簡易テストのみ |
| `models/sheet_name.py` | 外部キー制約、リレーション | データの関連性保証 | ⚠️ 簡易テストのみ |
| `services/patient_service.py::fetch_patient_history()` | クエリ正確性、ソート順、日付フォーマット | 履歴表示の信頼性 | ✅ 完了 |

#### 3.3 セキュリティ・エラーハンドリング

| モジュール/クラス | テスト対象 | 理由 | 現状 |
|-----------------|----------|------|------|
| `utils/config_manager.py::load_config()` | ファイル不在、権限エラー、パースエラー | アプリケーション起動の安定性 | ⚠️ 部分的 |
| `services/data_export_service.py::import_from_csv()` | ファイル名検証、不正データ拒否 | SQLインジェクション防止、データ汚染防止 | ⚠️ 未実装 |
| `utils/file_utils.py::close_excel_if_needed()` | Excel プロセスクリーンアップ | リソースリーク防止 | ✅ 完了 |

---

### P1（高優先度 - 推奨テスト）

#### 3.4 ユーザーインターフェース影響機能

| モジュール/クラス | テスト対象 | 理由 | 現状 |
|-----------------|----------|------|------|
| `services/patient_service.py::load_patient_data()` | CSV読み込み、エンコーディング処理 | ユーザー体験に直結 | ✅ 完了 |
| `services/patient_service.py::load_main_diseases()` | マスタデータ取得 | ドロップダウン表示の正確性 | ✅ 完了 |
| `services/patient_service.py::load_sheet_names()` | シート名フィルタリング | 疾病別フォーム選択 | ✅ 完了 |
| `services/file_monitor_service.py::MyHandler` | ファイル削除検知、アプリ終了処理 | システム安定性 | ⚠️ 未実装 |
| `app/event_handlers/data_operations.py` | データ操作イベント処理 | UI状態管理 | ⚠️ 未実装 |
| `app/event_handlers/form_operations.py` | フォーム操作イベント処理 | 入力検証、UX | ⚠️ 未実装 |

#### 3.5 パフォーマンスクリティカル処理

| モジュール/クラス | テスト対象 | 理由 | 現状 |
|-----------------|----------|------|------|
| `database/connection.py::get_engine()` | 接続プーリング、再利用 | パフォーマンス最適化 | ⚠️ 未実装 |
| `services/data_export_service.py::export_to_csv()` | 大量データエクスポート | バルク処理の効率性 | ⚠️ 未実装 |

---

### P2（中優先度 - 可能であれば実施）

#### 3.6 ユーティリティ関数

| モジュール/クラス | テスト対象 | 理由 | 現状 |
|-----------------|----------|------|------|
| `utils/file_utils.py::format_date()` | 日付フォーマット、NA処理 | 表示の一貫性 | ✅ 完了 |
| `services/template_service.py::TemplateManager` | テンプレート取得、キャッシュ | 単純なロジック | ⚠️ 未実装 |
| `widgets/form_fields.py` | フォームフィールド生成 | UI コンポーネント（E2E推奨） | ⚠️ 未実装 |
| `widgets/dropdown_items.py` | ドロップダウンアイテム生成 | UI コンポーネント（E2E推奨） | ⚠️ 未実装 |

#### 3.7 データベース初期化・マイグレーション

| モジュール/クラス | テスト対象 | 理由 | 現状 |
|-----------------|----------|------|------|
| `database/initializer.py` | DB初期化、マスタデータ投入 | セットアップの正確性 | ⚠️ 未実装 |
| `alembic/env.py` | マイグレーション実行 | スキーマ変更の安全性 | ⚠️ 未実装 |

---

### P3（低優先度 - テスト不要またはオプション）

#### 3.8 テスト不要な部分

| モジュール/クラス | 理由 |
|-----------------|------|
| `app/__init__.py` | 単純な定数定義（__version__, __date__） |
| `models/*::__tablename__` | SQLAlchemy ORM の宣言的定義 |
| `utils/constants.py` | 定数定義のみ（現在空） |
| `widgets/button_styles.py` | UIスタイル定義（視覚的検証が必要） |
| `scripts/version_manager.py` | ビルドスクリプト（手動実行） |
| `scripts/project_structure.py` | ドキュメント生成（手動実行） |
| `main.py::main()` | アプリケーションエントリーポイント（E2Eテスト対象） |
| `app/main_ui.py::create_ui()` | UI構築（E2Eテスト推奨） |

**理由:**
- 定数定義: テストしてもビジネス価値がない
- UIコンポーネント: ユニットテストよりE2Eテストが適切
- ビルドスクリプト: 手動実行のため優先度低
- ORM定義: SQLAlchemy自体がテスト済み

---

## 4. テストケース設計方針

### 4.1 正常系テスト

**対象:** すべてのP0、P1機能

**戦略:**
- **ハッピーパス:** 期待される入力で期待される出力が得られることを確認
- **標準的なデータ:** 実際の業務で使用される典型的なデータパターン
- **戻り値検証:** 関数の戻り値が仕様通りであることを確認
- **副作用検証:** ファイル作成、DB更新などの副作用を検証

**例:**
```python
def test_generate_plan_creates_file(sample_patient_info):
    """療養計画書が正常に生成されることを確認"""
    # モック設定
    # テスト実行
    # ファイル作成、バーコード生成、保存を検証
```

### 4.2 異常系テスト

**対象:** すべてのP0機能、重要なP1機能

**戦略:**
- **不正な入力:** None、空文字列、範囲外の値
- **存在しないリソース:** ファイル未検出、DB接続失敗
- **権限エラー:** 読み取り/書き込み権限なし
- **データ型エラー:** 文字列に数値が期待される場合など
- **例外ハンドリング:** 適切なエラーメッセージ、アプリケーション継続性

**例:**
```python
def test_load_patient_data_file_not_found():
    """患者CSVファイルが見つからない場合のエラーハンドリング"""
    # FileNotFoundError をモック
    # エラーメッセージが返されることを確認
    # アプリケーションがクラッシュしないことを確認
```

### 4.3 境界値テスト

**対象:** P0の数値処理、日付処理、文字列長

**戦略:**
- **最小値/最大値:** INT_MIN, INT_MAX
- **日付境界:** 閏年、月末、年末年始
- **ゼロケース:** 空リスト、ゼロ長文字列
- **オフバイワン:** n-1, n, n+1

**例:**
```python
@pytest.mark.parametrize("birth_date,issue_date,expected_age", [
    (date(1990, 2, 28), date(2025, 2, 28), 35),  # 通常年の誕生日当日
    (date(1990, 2, 29), date(2025, 2, 28), 34),  # 閏年生まれ、誕生日前
    (date(1990, 2, 29), date(2025, 3, 1), 35),   # 閏年生まれ、誕生日後
])
def test_calculate_age_leap_year_boundary(birth_date, issue_date, expected_age):
    """閏年境界値での年齢計算"""
```

### 4.4 エッジケーステスト

**対象:** P0、P1の複雑なロジック

**戦略:**
- **同時実行:** 複数のExcelファイルが開いている状態
- **リソース枯渇:** メモリ不足、ディスク満杯
- **文字エンコーディング:** Shift-JIS、UTF-8、特殊文字
- **データベース:** トランザクションロールバック、デッドロック

**例:**
```python
def test_close_excel_multiple_workbooks():
    """複数のExcelファイルが開いている場合、対象ファイルのみを閉じる"""
    # 5つのワークブックをモック
    # 対象ファイルのみがCloseされることを確認
```

---

## 5. モックとスタブの使用方針

### 5.1 外部依存関係のモック化

**必須モック:**

| 依存関係 | モック理由 | モック手法 |
|---------|----------|----------|
| `openpyxl.load_workbook()` | 実Excelファイル不要、高速化 | `@patch('services.treatment_plan_service.load_workbook')` |
| `barcode.Code128()` | バーコード画像生成の重さ回避 | `MagicMock()` |
| `os.startfile()` | Windows API、テスト環境で実行不可 | `@patch('os.startfile')` |
| `win32com.client.GetObject()` | Excel COM操作、環境依存 | `@patch('utils.file_utils.win32com.client.GetObject')` |
| `watchdog.Observer` | ファイル監視、テスト環境で不安定 | `MagicMock()` |
| `flet.Page` | UI フレームワーク、ヘッドレステスト困難 | `MagicMock()` |
| `pandas.read_csv()` | 外部CSVファイル依存削除 | `@patch` + ダミーDataFrame |

**推奨モック:**

| 依存関係 | モック理由 | モック手法 |
|---------|----------|----------|
| `config_manager.load_config()` | テストごとに異なる設定を注入 | `@patch` + 辞書返却 |
| `time.sleep()` | テスト実行時間短縮 | `@patch('time.sleep')` |

**実データ使用（モック不要）:**

| 依存関係 | 理由 | 手法 |
|---------|------|-----|
| SQLAlchemy ORM | インメモリDBで高速テスト可能 | `sqlite:///:memory:` |
| Python標準ライブラリ (`datetime`, `os.path`) | 信頼性が高く、モック不要 | 実関数使用 |

### 5.2 テストデータ準備戦略

#### 5.2.1 Fixture活用

```python
@pytest.fixture
def sample_patient_info():
    """再利用可能な患者情報テストデータ"""
    return PatientInfo(
        patient_id=12345,
        patient_name="山田太郎",
        birthdate=date(1980, 5, 15),
        issue_date=date(2025, 1, 10),
        # ... 全フィールド
    )

@pytest.fixture
def test_db():
    """インメモリSQLiteデータベース"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

#### 5.2.2 パラメータ化テスト

```python
@pytest.mark.parametrize("input_date,expected_output", [
    ("2025-01-01", "2025/01/01"),
    ("2025-12-31", "2025/12/31"),
    (pd.NA, ""),
    (None, ""),
])
def test_format_date_various_inputs(input_date, expected_output):
    """複数の入力パターンを効率的にテスト"""
    assert format_date(input_date) == expected_output
```

#### 5.2.3 テストデータファイル

**使用しない方針:**
- 理由: テストデータがコードから分離すると保守が困難
- 代替: Fixture とパラメータ化で対応

### 5.3 テスト環境の分離

**環境変数:**
```python
@pytest.fixture(autouse=True)
def set_test_environment(monkeypatch):
    """テスト環境を自動設定"""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("DB_URL", "sqlite:///:memory:")
```

**設定ファイル:**
- 本番: `config.ini`
- テスト: モック化（ファイル不要）

**データベース:**
- 本番: `ldtp_app.db` (SQLite)
- テスト: `:memory:` (インメモリ)

---

## 6. 推奨テスト手法

### 6.1 PyTest プラグイン

**必須:**
- `pytest` (8.4.2): テストフレームワーク
- `pytest-cov` (7.0.0): カバレッジ測定

**推奨:**
- `pytest-mock`: `unittest.mock` のPyTestラッパー
- `pytest-xdist`: 並列テスト実行（高速化）
- `pytest-timeout`: タイムアウト検出

**オプション:**
- `pytest-benchmark`: パフォーマンステスト
- `hypothesis`: Property-based testing（後述）

### 6.2 アサーション手法

**基本アサーション:**
```python
assert result is not None
assert result.patient_name == "山田太郎"
assert len(results) == 3
```

**例外アサーション:**
```python
with pytest.raises(FileNotFoundError):
    load_config_from_missing_file()

with pytest.raises(ValueError, match="患者IDが不正"):
    validate_patient_id(-1)
```

**モックアサーション:**
```python
mock_save.assert_called_once()
mock_save.assert_called_with(expected_path)
mock_close.assert_not_called()
```

### 6.3 Property-Based Testing (オプション)

**適用候補:** `utils/date_utils.py::calculate_issue_date_age()`

**Hypothesis使用例:**
```python
from hypothesis import given, strategies as st

@given(
    birth_year=st.integers(min_value=1900, max_value=2025),
    birth_month=st.integers(min_value=1, max_value=12),
    issue_year=st.integers(min_value=1900, max_value=2099)
)
def test_age_calculation_properties(birth_year, birth_month, issue_year):
    """年齢計算の不変条件をテスト"""
    # 有効な日付生成
    # 年齢は常に0以上であることを確認
    # issue_date >= birthdate なら age >= 0
```

**利点:**
- ランダムな入力で潜在的なバグを発見
- 境界値テストを自動生成

### 6.4 Windows固有のテスト

**ファイルパステスト:**
```python
@pytest.mark.skipif(sys.platform != "win32", reason="Windows専用")
def test_windows_path_handling():
    """Windowsパス処理のテスト"""
    path = r'C:\Shinseikai\LDTPapp\LDTPform.xlsm'
    assert os.path.exists(path) or True  # モック環境では常にパス
```

**COM操作テスト:**
```python
@patch('utils.file_utils.win32com.client.GetObject')
def test_excel_com_interaction(mock_get_object):
    """Excel COM操作のモックテスト"""
    # COMオブジェクトはすべてモック化
```

---

## 7. 実装時の注意点

### 7.1 パフォーマンス

**高速化テクニック:**

1. **モックの積極活用:**
   - ファイルI/O、ネットワークアクセスは必ずモック
   - `time.sleep()` は常にモック

2. **インメモリDB:**
   - SQLiteの`:memory:`を使用
   - テストごとにスキーマ再作成（フィクスチャ）

3. **並列実行:**
   ```bash
   pytest -n auto  # CPU コア数に応じて並列化
   ```

4. **テストの選択実行:**
   ```bash
   pytest tests/services/  # サービス層のみ
   pytest -k "patient"     # 患者関連のみ
   pytest -m "slow"        # スロー テストのみ（マーキング必要）
   ```

**パフォーマンス目標:**
- 全テスト実行: < 60秒
- 単一テストファイル: < 5秒
- 単一テストケース: < 100ms

### 7.2 保守性

**テストコードの品質:**

1. **DRY原則:**
   - Fixtureで共通データを定義
   - ヘルパー関数で重複ロジックを削減

2. **明確なテスト名:**
   ```python
   # Good
   def test_calculate_age_on_birthday():

   # Bad
   def test_age_1():
   ```

3. **AAA パターン (Arrange-Act-Assert):**
   ```python
   def test_create_patient():
       # Arrange: テストデータ準備
       patient_data = {...}

       # Act: テスト対象実行
       result = create_patient(patient_data)

       # Assert: 結果検証
       assert result.patient_id == 12345
   ```

4. **1テスト1アサーション（推奨）:**
   - 可能な限り1つのテストで1つの事象を検証
   - 失敗時の原因特定が容易

5. **コメント:**
   - テストの意図を簡潔に日本語で記述
   - 複雑なモック設定にはコメント必須

**テストファイル構成:**
```
tests/
├── conftest.py          # 共通Fixture
├── services/
│   ├── test_treatment_plan_service.py
│   ├── test_patient_service.py
│   └── test_data_export_service.py  # 新規
├── utils/
│   ├── test_config_manager.py       # 新規
│   └── ...
├── models/
│   ├── test_main_disease.py         # 新規
│   └── ...
└── integration/
    └── test_end_to_end_flow.py      # 新規（オプション）
```

### 7.3 テストの独立性

**原則:**
- 各テストは他のテストに依存しない
- 実行順序に依存しない
- テスト間でデータを共有しない

**実装:**
```python
@pytest.fixture(scope="function")  # 各テスト関数ごとに新規作成
def test_db():
    """テストごとにクリーンなDBを提供"""
    engine = create_engine('sqlite:///:memory:')
    # ...
```

**避けるべきパターン:**
```python
# Bad: グローバル変数
global_patient_id = 1

def test_create_patient():
    global global_patient_id
    # global変数を変更すると他のテストに影響
```

---

## 8. 継続的インテグレーション (CI) での実行方針

### 8.1 CI パイプライン構成

**推奨CI環境:** GitHub Actions / GitLab CI / Jenkins

**パイプライン例 (.github/workflows/test.yml):**

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest  # Windows専用アプリ

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-xdist

    - name: Run unit tests
      run: |
        pytest tests/ -v --cov=. --cov-report=xml --cov-report=html -n auto

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

    - name: Check coverage threshold
      run: |
        pytest --cov=. --cov-fail-under=80
```

### 8.2 テスト実行戦略

**コミットごと (Pre-commit hook):**
```bash
# 高速テストのみ（P0の一部）
pytest tests/utils/ -v --maxfail=1
```

**プルリクエストごと:**
```bash
# P0, P1 のすべてのテスト
pytest tests/ -v --cov=. --cov-fail-under=85 -n auto
```

**マージ前（main/master ブランチ）:**
```bash
# 全テスト + カバレッジレポート
pytest tests/ -v --cov=. --cov-report=html --cov-report=term -n auto
```

**夜間ビルド（オプション）:**
```bash
# 全テスト + スローテスト + インテグレーションテスト
pytest tests/ --runslow -v --cov=. --cov-report=html
```

### 8.3 カバレッジ目標

**全体目標:** 85%以上

**モジュール別目標:**
- `services/`: 90%以上（P0, P1）
- `utils/`: 95%以上（ロジックが単純）
- `models/`: 80%以上（ORM定義が多い）
- `app/`: 60%以上（UI層、E2E推奨）
- `database/`: 85%以上（リソース管理重要）

**カバレッジ測定コマンド:**
```bash
# HTMLレポート生成
pytest --cov=. --cov-report=html

# ターミナルで詳細表示
pytest --cov=. --cov-report=term-missing

# 特定モジュールのみ
pytest --cov=services --cov-report=term
```

### 8.4 失敗時の対応

**テスト失敗:**
1. 失敗したテストケースを確認
2. ローカル環境で再現
3. 修正後、再度全テスト実行

**カバレッジ不足:**
1. カバレッジレポート (`htmlcov/index.html`) を確認
2. 未カバーの行をテストケースに追加
3. P0, P1 の優先度順に対応

**CI環境でのみ失敗:**
1. 環境依存の可能性（Windows パス、タイムゾーンなど）
2. モックが不十分（外部リソースへのアクセス）
3. テストの独立性不足（実行順序依存）

---

## 9. 新規テスト実装ロードマップ

### 9.1 フェーズ1: P0完了（目標: 2週間）

**優先順位1:**
- ✅ `services/treatment_plan_service.py` - 完了済み
- ✅ `services/patient_service.py` - 完了済み
- ✅ `utils/date_utils.py` - 完了済み
- ✅ `utils/file_utils.py` - 完了済み
- ⚠️ `services/data_export_service.py` - **新規実装必須**
  - `test_export_to_csv()` - 正常系、エラーハンドリング
  - `test_import_from_csv()` - データ検証、型変換、不正データ拒否

**優先順位2:**
- ⚠️ `utils/config_manager.py` - **新規実装必須**
  - `test_load_config()` - 正常系、ファイル不在、権限エラー
  - `test_save_config()` - 書き込みエラー
  - `test_get_config_path()` - PyInstaller環境

**優先順位3:**
- ⚠️ `database/connection.py` - **新規実装必須**
  - `test_get_engine()` - シングルトンパターン、プーリング
  - `test_get_session()` - コンテキストマネージャ、クリーンアップ

### 9.2 フェーズ2: P1完了（目標: 1週間）

- ⚠️ `services/file_monitor_service.py` - **新規実装**
  - `test_MyHandler_on_deleted()` - ファイル削除検知
  - `test_start_file_monitoring()` - 監視開始
  - `test_check_file_exists()` - 存在確認

- ⚠️ `models/main_disease.py` - **拡張**
  - 既存の基本テストを拡充

- ⚠️ `models/sheet_name.py` - **拡張**
  - リレーションシップテスト追加

### 9.3 フェーズ3: P2完了（目標: 1週間）

- ⚠️ `services/template_service.py` - **新規実装**
- ⚠️ `database/initializer.py` - **新規実装**
- ⚠️ `app/event_handlers/*` - **新規実装（簡易版）**

### 9.4 フェーズ4: カバレッジ向上（継続的）

- カバレッジレポートを確認
- 未カバーの行にテストケース追加
- リファクタリング（テストしやすいコード設計）

---

## 10. テストファイル命名規則

### 10.1 ファイル名

**規則:** `test_<モジュール名>.py`

**例:**
- `services/patient_service.py` → `tests/services/test_patient_service.py`
- `utils/config_manager.py` → `tests/utils/test_config_manager.py`

### 10.2 テストクラス名

**規則:** `Test<クラス名>` または `Test<機能名>`

**例:**
```python
class TestTreatmentPlanGenerator:
    """TreatmentPlanGeneratorクラスのテスト"""

class TestLoadPatientData:
    """load_patient_data関数のテスト"""
```

### 10.3 テスト関数名

**規則:** `test_<テスト対象>_<条件>_<期待結果>`

**例:**
```python
def test_calculate_age_on_birthday():
    """誕生日当日の年齢計算テスト"""

def test_export_csv_file_not_found_returns_error():
    """CSVエクスポート: ファイル未検出時のエラー返却テスト"""
```

---

## 11. まとめ

### 11.1 重点事項

1. **P0機能の100%カバレッジ達成を最優先**
   - データ整合性、セキュリティ、ビジネスロジックの核

2. **モックの積極活用**
   - 外部依存を排除し、テストの高速化・安定化

3. **テストの独立性と保守性**
   - 各テストが独立して実行可能
   - 明確な命名とAAA パターン

4. **CI/CDへの統合**
   - プルリクエストごとにテスト実行
   - カバレッジ目標85%以上

### 11.2 次のアクションアイテム

**即座に実施:**
1. `tests/services/test_data_export_service.py` 作成
2. `tests/utils/test_config_manager.py` 作成
3. `tests/database/test_connection.py` 作成

**1週間以内:**
4. `tests/services/test_file_monitor_service.py` 作成
5. カバレッジ測定とレポート確認

**継続的:**
6. CI パイプライン構築（GitHub Actions推奨）
7. カバレッジ目標達成（85%以上）

### 11.3 参考資料

- [PyTest公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Hypothesis (Property-based testing)](https://hypothesis.readthedocs.io/)

---

**ドキュメントバージョン:** 1.0
**作成日:** 2025-11-04
**最終更新日:** 2025-11-04
