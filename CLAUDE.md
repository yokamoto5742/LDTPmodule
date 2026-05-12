# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## アプリ概要

生活習慣病療養計画書作成Windowsデスクトップアプリ。患者情報をSQLiteで管理し、Excelテンプレート（xlsm）にデータを流し込んでバーコード付き文書を生成する。

**エントリーポイント**: `main.py` → `ft.app(target=main)`

## コマンド

```bash
# アプリ実行
python main.py

# テスト
python -m pytest tests/ -v --tb=short
python -m pytest tests/services/test_treatment_plan_service.py -v
python -m pytest tests/services/test_patient_service.py::test_load_patient_data -v
python -m pytest tests/ -v --tb=short --cov=app --cov-report=html

# ビルド（PyInstaller で exe 生成）
python build.py

# DBマイグレーション
alembic revision --autogenerate -m "説明"
alembic upgrade head
alembic downgrade -1
```

## アーキテクチャ

三層構造：

```
UI層     app/            Flet コンポーネント・ルーティング・イベントハンドラ
サービス層 services/       ビジネスロジック（Excel生成・患者操作・ファイル監視）
データ層  database/ models/ SQLAlchemy ORM・接続管理
```

### UI層 (`app/`)

- `main_ui.py`: 全フォームフィールドを生成し `fields` 辞書に格納。`EventHandlers`・`DialogManager`・`RouteManager` を初期化して相互参照を設定する。
- `routes.py`: `RouteManager` が `/create`・`/edit`・`/template` の View を生成・管理。`page.on_route_change` に接続。
- `event_handlers/`: 操作ごとにファイルを分割（`data_operations.py`・`form_operations.py`・`template_operations.py`等）。
- `ui_builder.py`: テーブル・ボタン・指導項目レイアウトなど再利用UI要素のファクトリ関数群。

### サービス層 (`services/`)

- `treatment_plan_service.py`: `TreatmentPlanGenerator.generate_plan()` が openpyxl でテンプレート読み込み → データ入力 → バーコード（Code128）生成 → xlsm 保存。
- `patient_service.py`: pat.csv から患者データ読み込み・DBとの照合。
- `file_monitor_service.py`: watchdog で pat.csv を監視。削除で終了、更新でUI更新。
- `template_service.py`: 主病名・シート名ごとのテンプレートデフォルト値をDBで管理。

### データ層 (`database/` + `models/`)

- `database/connection.py`: シングルトンで engine・Session・Base を遅延初期化。`get_session()` コンテキストマネージャを使ってセッションを取得する。
- `database/initializer.py`: 起動時に `initialize_database()` でテーブル作成、`seed_initial_data()` でマスタ投入。
- モデル: `PatientInfo`（47フィールド）・`MainDisease`・`SheetName`・`Template`。

### 設定 (`utils/config.ini`)

全パス・サイズ設定を一元管理。`config_manager.load_config()` で取得。主要セクション: `[Database]`・`[Paths]`・`[FilePaths]`・`[Barcode]`・`[settings]`。

### UI文字列 (`utils/constants.py`)

画面表示文字列は `constants.py` の定数を参照し、コード内にマジック文字列を書かない。

## DBスキーマ変更手順

1. `models/patient_info.py` にカラム追加
2. `alembic revision --autogenerate -m "説明"` でマイグレーション生成
3. `alembic upgrade head` で適用
4. サービス層・UI層を更新

## Excelテンプレート変更手順

1. `C:\Shinseikai\LDTPapp\LDTPform.xlsm` を編集
2. `TreatmentPlanGenerator.populate_common_sheet()` のセル指定を更新
3. VBAマクロは `keep_vba=True` で自動保持される
