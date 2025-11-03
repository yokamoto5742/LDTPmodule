# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## House Rules:
- 文章ではなくパッチの差分を返す。
- コードの変更範囲は最小限に抑える。
- コードの修正は直接適用する。
- Pythonのコーディング規約はPEP8に従います。
- KISSの原則に従い、できるだけシンプルなコードにします。
- 可読性を優先します。一度読んだだけで理解できるコードが最高のコードです。
- Pythonのコードのimport文は以下の適切な順序に並べ替えてください。
標準ライブラリ
サードパーティライブラリ
カスタムモジュール 
それぞれアルファベット順に並べます。importが先でfromは後です。

## CHANGELOG
このプロジェクトにおけるすべての重要な変更は日本語でdcos/CHANGELOG.mdに記録します。
フォーマットは[Keep a Changelog](https://keepachangelog.com/ja/1.1.0/)に基づきます。

## Automatic Notifications (Hooks)
自動通知は`.claude/settings.local.json` で設定済：
- **Stop Hook**: ユーザーがClaude Codeを停止した時に「タスクが完了しました」と通知
- **SessionEnd Hook**: セッション終了時に「Claude Code セッションが終了しました」と通知

## クリーンコードガイドライン
- 関数のサイズ：関数は50行以下に抑えることを目標にしてください。関数の処理が多すぎる場合は、より小さなヘルパー関数に分割してください。
- 単一責任：各関数とモジュールには明確な目的が1つあるようにします。無関係なロジックをまとめないでください。
- 命名：説明的な名前を使用してください。`tmp` 、`data`、`handleStuff`のような一般的な名前は避けてください。例えば、`doCalc`よりも`calculateInvoiceTotal` の方が適しています。
- DRY原則：コードを重複させないでください。類似のロジックが2箇所に存在する場合は、共有関数にリファクタリングしてください。それぞれに独自の実装が必要な場合はその理由を明確にしてください。
- コメント:分かりにくいロジックについては説明を加えます。説明不要のコードには過剰なコメントはつけないでください。
- コメントとdocstringは必要最小限に日本語で記述し、文末に"。"や"."をつけないでください。

## Project Overview

LDTPapp is a Windows desktop application for creating lifestyle disease treatment plans (生活習慣病療養計画書). Built with Flet (Python UI framework) and SQLAlchemy, it manages patient information and generates Excel-based treatment plan documents with barcode support.

## Development Commands

### Running the Application
```bash
python main.py
```

### Building Executable
```bash
python build.py
```
This script:
- Increments version number automatically
- Updates version in `app/__init__.py`
- Builds executable using PyInstaller with windowed mode
- Copies `config.ini` to dist folder
- Icon: `assets/LDPTapp_icon.ico`

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Version Management
```bash
# Update version and README
python scripts/version_manager.py
```

### Project Structure Output
```bash
# Generate project structure documentation
python scripts/project_structure.py
```

## Architecture

### Core Components

**main.py** (~1800+ lines)
- Main application entry point with Flet UI
- Database models: `PatientInfo`, `MainDisease`, `SheetName`, `Template`
- Key classes:
  - `TreatmentPlanGenerator`: Generates Excel treatment plans using openpyxl
  - `TemplateManager`: Manages Excel template customization
  - `MyHandler`: File system watcher for pat.csv (watchdog)
- UI creation in `create_ui()` function
- Database initialization in `initialize_database()`

**Database Schema (SQLAlchemy ORM)**
- `PatientInfo`: Main patient data table with extensive fields for treatment plans including targets, goals, diet, exercise prescriptions
- `MainDisease`: Disease master data
- `SheetName`: Template sheet configurations
- `Template`: Customizable treatment plan templates
- Database URL configured in `config.ini` (default: sqlite:///ldtp_app.db)

**Configuration System**
- `config.ini`: All application settings
  - Database connection
  - Window dimensions (1200x900)
  - File paths (template, output, patient CSV)
  - Barcode generation parameters
- `config_manager.py`: Reads config with error handling

**Build & Version**
- `build.py`: Automated PyInstaller build process
- `app/__init__.py`: Stores `__version__` and `__date__`
- `scripts/version_manager.py`: Increments version, updates app/__init__.py and README

### Data Flow

1. Patient CSV (`pat.csv`) is monitored by watchdog
2. User selects patient ID in UI → loads from database
3. User creates treatment plan with disease/sheet selection
4. `TreatmentPlanGenerator.generate_plan()` populates Excel template
5. Excel file saved to output path with barcode generation
6. Data persisted to SQLite database

### External Dependencies

**Critical Paths (configured in config.ini):**
- Template: `C:\Shinseikai\LDTPapp\LDTPform.xlsm`
- Patient CSV: `C:\InnoKarte\pat.csv` (monitored - app exits if deleted)
- Output: `C:\Shinseikai\LDTPapp\temp`
- Export: `C:\Shinseikai\LDTPapp\export_data`

**Excel Operations:**
- Uses `openpyxl` for .xlsm file manipulation
- Template-based document generation with cell population
- Barcode images inserted at position B2

**Windows-Specific:**
- Uses `pywin32` for Windows file operations
- Application designed for Windows-only deployment

### Directory Structure

```
app/          - Application metadata (__version__, __date__)
service/      - Service layer (currently minimal)
utils/        - Utility modules (constants.py)
scripts/      - Build and version management scripts
alembic/      - Database migration files
tests/        - Test suite (minimal - pytest not installed)
assets/       - Application resources (icon)
docs/         - Japanese documentation (README.md)
```

### Migration History

Database has evolved through these migrations:
- `e8a162cad8b8`: Added `issue_date_age` column
- `f8f972d2c860`: Added `diet_comment` and `exercise_comment` columns
- `ef0000fbb21d`: Added `cancer_screening` column

## Development Guidelines

### Code Patterns

1. **Database Operations**: Use `get_session()` context manager for SQLAlchemy sessions
2. **UI Components**: Flet controls created via helper functions like `create_blue_outlined_dropdown()`
3. **Excel Generation**: `TreatmentPlanGenerator.populate_common_sheet()` handles template population
4. **Error Handling**: File operations wrapped with Excel process cleanup (`close_excel_if_needed()`)

### Configuration Updates

When adding new settings:
1. Update `config.ini`
2. Reload config in code via `config_manager.read_config()`
3. Document in docs/README.md

### Adding Database Fields

1. Modify model in `main.py`
2. Create Alembic migration: `alembic revision --autogenerate -m "description"`
3. Test migration: `alembic upgrade head`
4. Update UI forms and Excel template population logic
5. Update `TreatmentPlanGenerator` if needed

### Excel Template Modifications

Template file is external (.xlsm format):
- Macros are preserved through openpyxl operations
- Cell addresses hardcoded in `populate_common_sheet()`
- Barcode position: B2 (configurable in config.ini)

### Language

Application is fully Japanese:
- UI text in Japanese
- Database content in Japanese
- Documentation in Japanese (docs/README.md)
- Code comments mixed Japanese/English
