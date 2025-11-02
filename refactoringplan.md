# main.py リファクタリング実行計画

## 概要

本計画は、約1850行の `main.py` を適切に分割し、保守性・拡張性・テスト容易性を向上させることを目的とします。

## リファクタリングの原則

- **後方互換性の維持**: 既存の機能を損なわない
- **段階的な移行**: 各ステップごとにテスト・検証を実施
- **KISS原則の遵守**: シンプルで読みやすいコードを維持
- **最小限の変更**: 必要最小限の範囲でコードを変更

## フェーズ1: インフラストラクチャ層の抽出

### 1.1 データベース接続の分離

**対象コード (main.py の行42-50)**
```python
engine = create_engine(db_url, pool_pre_ping=True, pool_size=10)
Session = sessionmaker(bind=engine)
Base = declarative_base()
```

**新規ファイル: `database/connection.py`**
- データベースエンジン、セッションメーカー、ベースクラスを管理
- `get_engine()`: エンジンを返す関数
- `get_session_factory()`: セッションファクトリを返す関数
- `get_base()`: ベースクラスを返す関数
- `@contextmanager get_session()`: セッション管理コンテキストマネージャ（main.pyの行407-413から移動）

**新規ファイル: `database/__init__.py`**
- `from .connection import get_engine, get_session_factory, get_base, get_session`

**main.py での変更**
```python
from database import get_engine, get_session_factory, get_base, get_session
```

### 1.2 設定管理の統合

**既存ファイル: `utils/config_manager.py`**
- 現在は `load_config()` のみを提供
- 追加機能不要（現状維持）

**新規ファイル: `utils/file_utils.py`**
- `close_excel_if_needed(target_path)`: Excelファイルを閉じる関数（main.pyの行220-240から移動）
- `format_date(date_str)`: 日付フォーマット関数（main.pyの行431-434から移動）

**新規ファイル: `utils/date_utils.py`**
- `calculate_issue_date_age(birth_date, issue_date)`: 年齢計算関数（main.pyの行880-885から移動）

**新規ファイル: `utils/__init__.py`**
```python
from . import config_manager
from .file_utils import close_excel_if_needed, format_date
from .date_utils import calculate_issue_date_age
```

## フェーズ2: モデル層の抽出

### 2.1 SQLAlchemyモデルの分離

**新規ファイル: `models/patient_info.py`**
- `PatientInfo` クラス（main.pyの行52-92から移動）

**新規ファイル: `models/main_disease.py`**
- `MainDisease` クラス（main.pyの行95-98から移動）

**新規ファイル: `models/sheet_name.py`**
- `SheetName` クラス（main.pyの行101-105から移動）

**新規ファイル: `models/template.py`**
- `Template` クラス（main.pyの行108-127から移動）

**新規ファイル: `models/__init__.py`**
```python
from database import get_base
Base = get_base()

from .patient_info import PatientInfo
from .main_disease import MainDisease
from .sheet_name import SheetName
from .template import Template

__all__ = ['Base', 'PatientInfo', 'MainDisease', 'SheetName', 'Template']
```

**main.py での変更**
```python
from models import Base, PatientInfo, MainDisease, SheetName, Template
```

### 2.2 データベース初期化の分離

**新規ファイル: `database/initializer.py`**
- `initialize_database()`: テーブル作成（main.pyの行437-438から移動）
- `seed_initial_data()`: 初期データ投入（main.pyの行489-631から移動）

**main.py での変更**
```python
from database.initializer import initialize_database, seed_initial_data
```

## フェーズ3: サービス層の実装

### 3.1 療養計画書生成サービス

**新規ファイル: `services/treatment_plan_service.py`**
- `TreatmentPlanGenerator` クラス（main.pyの行242-357から移動）
  - `generate_plan(patient_info, file_name)`: 計画書生成
  - `populate_common_sheet(common_sheet, patient_info)`: 共通シート入力

**main.py での変更**
```python
from services.treatment_plan_service import TreatmentPlanGenerator
```

### 3.2 テンプレート管理サービス

**新規ファイル: `services/template_service.py`**
- `TemplateManager` クラス（main.pyの行359-364から移動）
- `load_template(main_disease, sheet_name)`: テンプレート読み込み
- `save_template(template_data)`: テンプレート保存

**main.py での変更**
```python
from services.template_service import TemplateManager
```

### 3.3 患者データサービス

**新規ファイル: `services/patient_service.py`**
- `load_patient_data()`: 患者CSVデータ読み込み（main.pyの行389-404から移動）
- `load_main_diseases()`: 主病名マスタ読み込み（main.pyの行416-419から移動）
- `load_sheet_names(main_disease=None)`: シート名マスタ読み込み（main.pyの行422-428から移動）
- `fetch_patient_history(filter_patient_id=None)`: 患者履歴取得（main.pyの行1337-1357から移動）

**main.py での変更**
```python
from services.patient_service import (
    load_patient_data,
    load_main_diseases,
    load_sheet_names,
    fetch_patient_history
)
```

### 3.4 ファイル監視サービス

**新規ファイル: `services/file_monitor_service.py`**
- `MyHandler` クラス（main.pyの行367-373から移動）
- `start_file_monitoring(page)`: ファイル監視開始（main.pyの行376-381から移動）
- `check_file_exists(page)`: ファイル存在確認（main.pyの行384-387から移動）

**main.py での変更**
```python
from services.file_monitor_service import start_file_monitoring, check_file_exists
```

### 3.5 データエクスポート/インポートサービス

**新規ファイル: `services/data_export_service.py`**
- `export_to_csv(export_folder)`: CSV出力（main.pyの行762-809から移動）
- `import_from_csv(file_path)`: CSV取込（main.pyの行683-760から移動）

**新規ファイル: `services/__init__.py`**
```python
from .treatment_plan_service import TreatmentPlanGenerator
from .template_service import TemplateManager
from .patient_service import load_patient_data, load_main_diseases, load_sheet_names, fetch_patient_history
from .file_monitor_service import start_file_monitoring, check_file_exists
from .data_export_service import export_to_csv, import_from_csv
```

## フェーズ4: UI層の分離

### 4.1 UIコンポーネント（ウィジェット）の分離

**新規ファイル: `widgets/dropdown_items.py`**
- `DropdownItems` クラス（main.pyの行134-166から移動）

**新規ファイル: `widgets/form_fields.py`**
- `create_blue_outlined_dropdown()`: 青枠ドロップダウン作成（main.pyの行168-179から移動）
- `create_form_fields(dropdown_items)`: フォームフィールド作成（main.pyの行182-217から移動）

**新規ファイル: `widgets/button_styles.py`**
- `create_theme_aware_button_style(page)`: テーマ対応ボタンスタイル作成（main.pyの行441-457から移動）

**新規ファイル: `widgets/__init__.py`**
```python
from .dropdown_items import DropdownItems
from .form_fields import create_blue_outlined_dropdown, create_form_fields
from .button_styles import create_theme_aware_button_style
```

### 4.2 UI作成ロジックの分離

**新規ファイル: `app/ui_builder.py`**
- `build_patient_fields(initial_patient_id, input_height)`: 患者情報フィールド作成（main.pyの行1664-1675から抽出）
- `build_form_fields(dropdown_items, input_height, text_height)`: フォームフィールド作成（main.pyの行1676-1728から抽出）
- `build_guidance_items(...)`: 指導項目レイアウト作成（main.pyの行1730-1753から抽出）
- `build_history_table(data)`: 履歴テーブル作成（main.pyの行1759-1780から抽出）
- `build_buttons(page, handlers, button_style)`: ボタン作成（main.pyの行1786-1820から抽出）

**main.py での変更**
```python
from app.ui_builder import (
    build_patient_fields,
    build_form_fields,
    build_guidance_items,
    build_history_table,
    build_buttons
)
```

### 4.3 イベントハンドラの分離

**新規ファイル: `app/event_handlers.py`**
- `PatientEventHandlers` クラス
  - `on_patient_id_change()`: 患者ID変更（main.pyの行1035-1039から移動）
  - `on_issue_date_change()`: 発行日変更（main.pyの行811-814から移動）
  - `on_date_picker_dismiss()`: 日付ピッカー終了（main.pyの行816-820から移動）

- `FormEventHandlers` クラス
  - `on_main_diagnosis_change()`: 主病名変更（main.pyの行833-847から移動）
  - `on_sheet_name_change()`: シート名変更（main.pyの行849-851から移動）
  - `on_tobacco_checkbox_change()`: たばこチェックボックス変更（main.pyの行1712-1718から移動）

- `DataEventHandlers` クラス
  - `on_row_selected()`: 行選択（main.pyの行1279-1335から移動）
  - `create_new_plan()`: 新規作成（main.pyの行974-982から移動）
  - `save_new_plan()`: 新規保存（main.pyの行984-992から移動）
  - `save_data()`: データ保存（main.pyの行1041-1095から移動）
  - `print_plan()`: 印刷（main.pyの行994-1033から移動）
  - `copy_data()`: データコピー（main.pyの行1097-1175から移動）
  - `delete_data()`: データ削除（main.pyの行1234-1269から移動）

- `TemplateEventHandlers` クラス
  - `apply_template()`: テンプレート適用（main.pyの行1377-1402から移動）
  - `save_template()`: テンプレート保存（main.pyの行1404-1468から移動）

**main.py での変更**
```python
from app.event_handlers import (
    PatientEventHandlers,
    FormEventHandlers,
    DataEventHandlers,
    TemplateEventHandlers
)
```

### 4.4 ルーティングの分離

**新規ファイル: `app/routes.py`**
- `RouteManager` クラス
  - `route_change()`: ルート変更処理（main.pyの行1470-1603から移動）
  - `view_pop()`: ビュー戻る（main.pyの行1605-1608から移動）
  - `open_create()`: 新規作成画面（main.pyの行1610-1611から移動）
  - `open_edit()`: 編集画面（main.pyの行1613-1614から移動）
  - `open_template()`: テンプレート画面（main.pyの行1616-1618から移動）
  - `open_route()`: ホーム画面（main.pyの行1620-1642から移動）

**main.py での変更**
```python
from app.routes import RouteManager
```

### 4.5 ダイアログとその他UI要素

**新規ファイル: `app/dialogs.py`**
- `SettingsDialog` クラス
  - `open_settings_dialog()`: 設定ダイアログ表示（main.pyの行645-673から移動）
  - `open_file_picker()`: ファイルピッカー表示（関連コード）

- `ErrorDialog` クラス
  - `show_error_message(message)`: エラーメッセージ表示（main.pyの行959-963から移動）
  - `check_required_fields()`: 必須フィールドチェック（main.pyの行965-972から移動）

**main.py での変更**
```python
from app.dialogs import SettingsDialog, ErrorDialog
```

### 4.6 メインUI制御

**新規ファイル: `app/main_ui.py`**
- `create_ui(page)`: メインUI作成関数（main.pyの行460-1840から大幅にリファクタリング）
  - 各UI要素の生成を `ui_builder` に委譲
  - イベントハンドラを `event_handlers` から取得
  - ルーティングを `routes` に委譲

**main.py での最終形**
```python
import flet as ft
from app.main_ui import create_ui
from services.file_monitor_service import start_file_monitoring, check_file_exists

def main(page: ft.Page):
    start_file_monitoring(page)
    check_file_exists(page)
    create_ui(page)

if __name__ == "__main__":
    ft.app(target=main)
```

## フェーズ5: テストと検証

### 5.1 単体テストの作成

**新規ファイル: `tests/models/test_patient_info.py`**
- PatientInfoモデルのテスト

**新規ファイル: `tests/services/test_treatment_plan_service.py`**
- TreatmentPlanGeneratorのテスト

**新規ファイル: `tests/services/test_patient_service.py`**
- 患者サービスのテスト

**新規ファイル: `tests/utils/test_date_utils.py`**
- 日付ユーティリティのテスト

**新規ファイル: `tests/utils/test_file_utils.py`**
- ファイルユーティリティのテスト

### 5.2 統合テスト

**新規ファイル: `tests/integration/test_ui_flow.py`**
- UI全体のフロー確認

**新規ファイル: `tests/integration/test_database_operations.py`**
- データベース操作の確認

## 実装スケジュール

### ステップ1: インフラストラクチャ層（1日目）
1. `database/connection.py` 作成
2. `database/__init__.py` 作成
3. `utils/file_utils.py` 作成
4. `utils/date_utils.py` 作成
5. main.pyで対応するインポートを修正
6. 動作確認

### ステップ2: モデル層（1日目）
1. `models/patient_info.py` 作成
2. `models/main_disease.py` 作成
3. `models/sheet_name.py` 作成
4. `models/template.py` 作成
5. `models/__init__.py` 作成
6. `database/initializer.py` 作成
7. main.pyで対応するインポートを修正
8. 動作確認

### ステップ3: サービス層（2日目）
1. `services/treatment_plan_service.py` 作成
2. `services/template_service.py` 作成
3. `services/patient_service.py` 作成
4. `services/file_monitor_service.py` 作成
5. `services/data_export_service.py` 作成
6. `services/__init__.py` 作成
7. main.pyで対応するインポートを修正
8. 動作確認

### ステップ4: ウィジェット層（2日目）
1. `widgets/dropdown_items.py` 作成
2. `widgets/form_fields.py` 作成
3. `widgets/button_styles.py` 作成
4. `widgets/__init__.py` 更新
5. main.pyで対応するインポートを修正
6. 動作確認

### ステップ5: UI層（3日目）
1. `app/event_handlers.py` 作成
2. `app/routes.py` 作成
3. `app/dialogs.py` 作成
4. `app/ui_builder.py` 作成
5. `app/main_ui.py` 作成
6. main.pyを最小限に整理
7. 動作確認

### ステップ6: テストと最終検証（3日目）
1. 各モジュールの単体テスト作成
2. 統合テストの実施
3. ビルド確認（build.py実行）
4. 実行ファイルの動作確認
5. ドキュメント更新（docs/README.md）

## リファクタリング後のディレクトリ構造

```
LDTPmodule/
├── main.py                      # 約30行（エントリーポイントのみ）
├── config.ini
├── build.py
├── requirements.txt
├── alembic.ini
├── ldtp_app.db
├── CLAUDE.md
├── refactoringplan.md          # 本ドキュメント
├── .gitignore
│
├── app/                        # UI層
│   ├── __init__.py             # __version__, __date__
│   ├── main_ui.py              # メインUI制御（約200行）
│   ├── ui_builder.py           # UI要素生成（約200行）
│   ├── event_handlers.py       # イベントハンドラ（約400行）
│   ├── routes.py               # ルーティング（約150行）
│   └── dialogs.py              # ダイアログ（約100行）
│
├── widgets/                    # ウィジェット層
│   ├── __init__.py
│   ├── dropdown_items.py       # ドロップダウン管理（約40行）
│   ├── form_fields.py          # フォームフィールド（約60行）
│   └── button_styles.py        # ボタンスタイル（約20行）
│
├── models/                     # モデル層
│   ├── __init__.py
│   ├── patient_info.py         # 患者情報モデル（約50行）
│   ├── main_disease.py         # 疾病マスタモデル（約10行）
│   ├── sheet_name.py           # シート名モデル（約10行）
│   └── template.py             # テンプレートモデル（約25行）
│
├── services/                   # サービス層
│   ├── __init__.py
│   ├── treatment_plan_service.py   # 療養計画書生成（約120行）
│   ├── template_service.py         # テンプレート管理（約30行）
│   ├── patient_service.py          # 患者データ管理（約60行）
│   ├── file_monitor_service.py     # ファイル監視（約30行）
│   └── data_export_service.py      # データエクスポート/インポート（約150行）
│
├── database/                   # データベース層
│   ├── __init__.py
│   ├── connection.py           # データベース接続（約40行）
│   └── initializer.py          # データベース初期化（約160行）
│
├── utils/                      # ユーティリティ層
│   ├── __init__.py
│   ├── config_manager.py       # 設定管理（既存）
│   ├── file_utils.py           # ファイルユーティリティ（約30行）
│   ├── date_utils.py           # 日付ユーティリティ（約10行）
│   └── constants.py            # 定数定義
│
├── scripts/                    # スクリプト
│   ├── __init__.py
│   ├── version_manager.py
│   └── project_structure.py
│
├── alembic/                    # マイグレーション
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── tests/                      # テスト
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── test_patient_info.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── test_treatment_plan_service.py
│   │   └── test_patient_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── test_date_utils.py
│   │   └── test_file_utils.py
│   └── integration/
│       ├── __init__.py
│       ├── test_ui_flow.py
│       └── test_database_operations.py
│
├── assets/
│   └── LDPTapp_icon.ico
│
└── docs/
    ├── README.md
    └── CHANGELOG.md
```

## リファクタリング後の行数削減

| ファイル/モジュール | リファクタリング前 | リファクタリング後 | 削減率 |
|------------------|----------------|----------------|--------|
| main.py | ~1850行 | ~30行 | 98% |
| app/ | - | ~1050行 | - |
| widgets/ | - | ~120行 | - |
| models/ | - | ~95行 | - |
| services/ | - | ~390行 | - |
| database/ | - | ~200行 | - |
| utils/ | ~50行 | ~90行 | - |
| **合計** | ~1900行 | ~1975行 | - |

※行数はコメント・空行を含む概算

## リスク管理

### 潜在的リスク

1. **インポート循環依存**: モジュール間の循環参照
   - **対策**: 依存関係を明確に設計、必要に応じて遅延インポート

2. **グローバル変数の扱い**: `selected_row` などのグローバル状態
   - **対策**: クラスインスタンス変数として管理

3. **既存の動作への影響**: リファクタリングによる予期せぬバグ
   - **対策**: 各ステップで動作確認、テスト作成

4. **ビルドプロセスへの影響**: PyInstallerの依存解決
   - **対策**: 新規モジュールを明示的に含める設定

### ロールバック計画

- Gitで各ステップをコミット
- 問題が発生した場合は前のステップに戻す

## 成功基準

1. ✅ すべての既存機能が正常に動作する
2. ✅ main.pyが100行以下になる
3. ✅ 各モジュールが単一責任を持つ
4. ✅ テストカバレッジが50%以上
5. ✅ ビルドが成功し、実行ファイルが正常に動作する
6. ✅ コードレビューで問題が指摘されない

## まとめ

本リファクタリング計画により、以下の成果が期待されます：

- **保守性の向上**: 各モジュールが小さく、理解しやすい
- **テスト容易性の向上**: 独立したモジュールで単体テストが可能
- **拡張性の向上**: 新機能の追加が容易
- **可読性の向上**: コードの構造が明確
- **チーム開発の促進**: モジュール単位での並行開発が可能

リファクタリングは段階的に実施し、各ステップで動作確認とテストを行います。
