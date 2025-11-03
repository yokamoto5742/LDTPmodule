# 統合テスト

## 概要

`test_ui_flow.py` は、LDTPappのFletアプリケーションにおける主要なUIフローとイベントハンドラの統合テストです

## テスト対象モジュール

- `app.dialogs` - DialogManager（ダイアログとメッセージ表示管理）
- `app.event_handlers` - EventHandlers（UIイベントハンドラ管理）
- `app.routes` - RouteManager（ルーティング管理）

## テストクラス構成

### TestDialogManager
DialogManagerクラスの統合テスト

- `test_init_dialog_manager` - 初期化テスト
- `test_show_error_message` - エラーメッセージ表示テスト
- `test_show_info_message` - 情報メッセージ表示テスト
- `test_check_required_fields_success` - 必須フィールドチェック成功テスト
- `test_check_required_fields_missing_main_diagnosis` - 主病名未選択時のチェック
- `test_check_required_fields_missing_sheet_name` - シート名未選択時のチェック

### TestEventHandlers
EventHandlersクラスの統合テスト

- `test_init_event_handlers` - 初期化テスト
- `test_load_patient_info_success` - 患者情報読み込み成功テスト
- `test_load_patient_info_not_found` - 患者情報が見つからない場合のテスト
- `test_on_tobacco_checkbox_change_nonsmoker` - 非喫煙者チェックボックス変更テスト
- `test_on_tobacco_checkbox_change_smoking_cessation` - 禁煙実施方法チェックボックス変更テスト
- `test_create_treatment_plan_object` - 療養計画書オブジェクト作成テスト
- `test_create_treatment_plan_object_patient_not_found` - 患者が見つからない場合のエラーハンドリング

### TestRouteManager
RouteManagerクラスの統合テスト

- `test_init_route_manager` - 初期化テスト
- `test_open_create` - 新規作成画面を開くテスト
- `test_open_edit` - 編集画面を開くテスト
- `test_open_template` - テンプレート画面を開くテスト
- `test_open_route_resets_fields` - ホーム画面を開くときのフィールドリセットテスト
- `test_on_close` - ウィンドウを閉じるテスト

### TestUIFlowIntegration
UIフロー全体の統合テスト

- `test_dialog_and_event_handler_integration` - DialogManagerとEventHandlersの連携テスト
- `test_route_and_event_handler_integration` - RouteManagerとEventHandlersの連携テスト
- `test_full_ui_flow_create_and_save` - 新規作成から保存までのフルフローテスト

## テスト実行方法

### 基本実行
```bash
python -m pytest tests/integration/test_ui_flow.py -v
```

### カバレッジレポート付き実行
```bash
python -m pytest tests/integration/test_ui_flow.py -v --cov=app --cov-report=term-missing
```

### 特定のテストクラスのみ実行
```bash
python -m pytest tests/integration/test_ui_flow.py::TestDialogManager -v
```

### 特定のテストメソッドのみ実行
```bash
python -m pytest tests/integration/test_ui_flow.py::TestEventHandlers::test_load_patient_info_success -v
```

## テスト結果

実行結果: **22個のテスト全てに合格**

### カバレッジレポート（appモジュール）

| モジュール | カバレッジ |
|----------|----------|
| app/__init__.py | 100% |
| app/dialogs.py | 57% |
| app/event_handlers.py | 27% |
| app/routes.py | 57% |
| **総合** | **28%** |

## テストの特徴

1. **モックとスタブの使用**: Fletの実際のウィンドウを表示せずにUIロジックをテスト
2. **独立性**: 各テストは独立して実行可能
3. **PEP8準拠**: Pythonのコーディング規約に準拠
4. **日本語コメント**: 文末に"。"や"."をつけない形式

## 制約事項

- Fletは実際のウィンドウを表示するため、完全な統合テストは難しい
- モックを使用して主要なロジックのみをテスト
- データベース操作は部分的にモック化

## 今後の改善点

1. EventHandlersのカバレッジを向上させる（現在27%）
2. データベース操作の統合テストを追加
3. エラーハンドリングのエッジケーステストを追加
4. UI要素の相互作用テストを追加
