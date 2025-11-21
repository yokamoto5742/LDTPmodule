# 生活習慣病療養計画書作成アプリ

生活習慣病患者の療養計画書を効率的に作成・管理するWindows専用デスクトップアプリケーションです。患者情報をSQLiteデータベースで管理し、Excelテンプレートベースで自動生成します。

**現在のバージョン**: 2.0.3
**最終更新日**: 2025年11月21日

## 主要機能

- **患者情報管理**: 患者データをSQLiteに記録・更新
- **療養計画書自動生成**: Excelテンプレートをベースに自動入力
- **バーコード付き文書**: 生成した療養計画書にバーコードを自動挿入
- **ファイル監視**: pat.csv（患者データソース）の変更を自動監視
- **テンプレートカスタマイズ**: 疾病別・目標別の療養計画テンプレート管理
- **データエクスポート**: 患者情報のCSVエクスポート機能

## 技術スタック

**コア技術**
- **Python 3.11**: プログラミング言語
- **Flet 0.23.0**: UIフレームワーク
- **SQLAlchemy 2.0.39**: ORM（データベース操作）
- **SQLite**: ローカルデータベース

**Excel文書生成**
- **openpyxl 3.1.5**: Excelファイル操作（マクロ保持対応）
- **python-barcode 0.15.1**: バーコード画像生成
- **pypng 0.20220715.0**: PNG画像処理

**データ処理・連携**
- **pandas 2.0.3**: CSV等のデータ処理
- **watchdog 4.0.2**: ファイルシステム監視

## 前提条件

**システム要件**
- Windows10 64ビット以上
- Python 3.11以上
- メモリ: 4GB以上推奨

## インストール

1. リポジトリをクローン
   ```bash
   git clone https://github.com/yokamoto5742/LDTPapp.git
   cd LDTPmodule
   ```

2. 仮想環境を作成・有効化
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. 依存パッケージをインストール
   ```bash
   pip install -r requirements.txt
   ```

4. 設定ファイルを確認・編集
   ```bash
   # utils/config.ini を環境に合わせて編集
   # 特にテンプレートパス、出力パスを確認
   ```

5. アプリケーションを起動
   ```bash
   python main.py
   ```

## 使用方法

### 基本的なワークフロー

1. **アプリケーション起動**
   ```bash
   python main.py
   ```
   - pat.csvファイルの存在を自動確認（ない場合は終了）
   - データベースを自動初期化

2. **患者情報の選択**
   - 患者IDを入力・検索
   - 対象患者の情報が自動読み込み

3. **療養計画書の作成**
   - 主病名（高血圧症、脂質異常症、糖尿病など）を選択
   - シート名（目標数値別）を選択
   - 各項目を入力（目標値、食事・運動処方など）

4. **ドキュメント生成**
   - 「新規登録して印刷」ボタンで自動生成
   - ファイル名: `{患者ID}{文書番号}{部門ID}{医師ID}{日付}{時刻}.xlsm`
   - 出力先: `C:\Shinseikai\LDTPapp\temp`
   - バーコード自動挿入（B2セル）

### テンプレート編集

1. 「テンプレート編集」ボタンをクリック
2. 主病名とシート名を選択
3. テンプレートのデフォルト値を編集
4. 保存

### データのエクスポート

- 「設定」画面からCSVエクスポート機能でデータ出力
- エクスポート先: `C:\Shinseikai\LDTPapp\export_data`

## プロジェクト構造

```
LDTPmodule/
├── main.py                     # アプリケーションエントリーポイント
├── app/                        # UI・ダイアログ層
│   ├── __init__.py            # バージョン情報（__version__, __date__）
│   ├── main_ui.py             # メインUI構築
│   ├── ui_builder.py          # UI要素生成ユーティリティ
│   ├── dialogs.py             # ダイアログコンポーネント
│   ├── routes.py              # ルーティング処理
│   └── event_handlers/        # イベントハンドラー
│
├── models/                     # SQLAlchemyモデル
│   ├── patient_info.py        # 患者情報テーブル
│   ├── main_disease.py        # 主病名マスタ
│   ├── sheet_name.py          # シート名マスタ
│   └── template.py            # テンプレートデータ
│
├── database/                   # データベース層
│   ├── connection.py          # DB接続設定
│   └── initializer.py         # テーブル初期化・シードデータ
│
├── services/                   # ビジネスロジック層
│   ├── treatment_plan_service.py  # Excel生成・バーコード処理
│   ├── patient_service.py         # 患者情報操作
│   ├── template_service.py        # テンプレート管理
│   ├── file_monitor_service.py    # pat.csv監視（watchdog）
│   └── data_export_service.py     # データエクスポート
│
├── utils/                      # ユーティリティ
│   ├── config.ini             # 設定ファイル
│   ├── config_manager.py      # 設定読み込みユーティリティ
│   └── constants.py           # 定数定義
│
├── alembic/                    # データベースマイグレーション
│
├── tests/                      # テストスイート
│
├── assets/                     # リソース
│   └── LDPTapp_icon.ico       # アプリケーションアイコン
│
└── docs/                       # ドキュメント
    ├── README.md              # このファイル
    └── CHANGELOG.md           # 変更履歴
```

## 設定（config.ini）

`utils/config.ini` で以下をカスタマイズ可能:

```ini
[Database]
db_url = sqlite:///ldtp_app.db

[settings]
window_width = 1200          # ウィンドウ幅
window_height = 900          # ウィンドウ高さ

[Paths]
template_path = C:\Shinseikai\LDTPapp\LDTPform.xlsm
output_path = C:\Shinseikai\LDTPapp\temp

[FilePaths]
patient_data = C:\InnoKarte\pat.csv
export_folder = C:\Shinseikai\LDTPapp\export_data
manual_pdf = C:\Shinseikai\LDTPapp\LDTPapp_manual.pdf

[Barcode]
write_text = false           # バーコード下にテキスト表記
module_height = 15           # バーコード高さ
image_position = B2          # バーコード挿入位置
```

## データベーススキーマ

### PatientInfo テーブル
患者の詳細情報（47フィールド）

**基本情報**
- `patient_id`: 患者ID
- `patient_name`: 患者名
- `kana`: カナ表記
- `gender`: 性別
- `birthdate`: 生年月日
- `issue_date`: 発行日
- `issue_date_age`: 発行日時点の年齢

**医療情報**
- `main_diagnosis`: 主病名
- `target_weight`: 目標体重
- `target_bp`: 目標血圧
- `target_hba1c`: 目標HbA1c
- `cancer_screening`: 癌検診有無

**処方情報**
- `goal1`, `goal2`: 達成目標
- `target_achievement`: 達成期限
- `diet1-4`: 食事処方（複数項目）
- `diet_comment`: 食事コメント
- `exercise_prescription`: 運動処方
- `exercise_time`: 運動時間
- `exercise_frequency`: 運動頻度
- `exercise_intensity`: 運動強度
- `exercise_comment`: 運動コメント
- `daily_activity`: 日常生活活動
- `nonsmoker`: 喫煙者状態
- `smoking_cessation`: 禁煙状態

### MainDisease テーブル
主病名マスタ: 高血圧症、脂質異常症、糖尿病

### SheetName テーブル
シート名マスタ: 疾病ごとの目標数値別シート定義

### Template テーブル
テンプレートデータ: 疾病・シート別のデフォルト値

## 開発ガイドライン

### 開発コマンド

**アプリケーション実行**
```bash
python main.py
```

**実行ファイルビルド**
```bash
python build.py
```
- version_manager で自動バージョンアップ
- PyInstaller で実行ファイル生成
- config.ini を dist フォルダにコピー
- ウィンドウモード有効、アイコン設定済み

**バージョン管理**
```bash
python scripts/version_manager.py
```
- app/__init__.py の __version__ を更新
- 最終更新日付を __date__ に設定
- docs/README.md のバージョン情報も更新

**プロジェクト構造表示**
```bash
python scripts/project_structure.py
```

**データベースマイグレーション**
```bash
# 新規マイグレーション作成
alembic revision --autogenerate -m "説明"

# マイグレーション適用
alembic upgrade head

# マイグレーション元に戻す
alembic downgrade -1
```

**テスト実行**
```bash
pytest tests/
pytest tests/ -v              # 詳細表示
pytest tests/ --cov           # カバレッジ表示
```

### アーキテクチャパターン

**三層構造**
- **UI層** (app/): Flet UIコンポーネント
- **サービス層** (services/): ビジネスロジック
- **データ層** (database/, models/): ORM・永続化

**主要な処理フロー**

1. **患者データ読み込み**
   - pat.csv → watchdog 監視
   - PatientInfo から患者レコード取得
   - UI に表示

2. **生活習慣病療養計画書生成**
   ```
   入力情報 → TreatmentPlanGenerator.generate_plan()
   → テンプレート読み込み（openpyxl）
   → populate_common_sheet() でデータ入力
   → バーコード生成（python-barcode）
   → ファイル出力（/temp）
   → DBに登録
   ```

3. **ファイル監視**
   - pat.csv を watchdog 監視
   - 削除検出 → アプリ終了
   - 更新検出 → UI更新

### 新機能追加時の手順

**データベーススキーマ追加**
1. models/patient_info.py にカラム追加
2. `alembic revision --autogenerate -m "カラム説明"`
3. `alembic upgrade head` でマイグレーション実行
4. services/ でビジネスロジック実装
5. app/ で UI 追加

**Excel テンプレート変更**
1. `C:\Shinseikai\LDTPapp\LDTPform.xlsm` を編集
2. TreatmentPlanGenerator.populate_common_sheet() の セル指定を更新
3. 新しいマクロは openpyxl の keep_vba=True で保持

## トラブルシューティング

**「pat.csvが見つかりません」エラー**
- 原因: pat.csv ファイルが削除されたか、パスが間違い
- 解決: config.ini の FilePaths.patient_data を確認・修正

**テンプレート読み込みエラー**
- 原因: template_path の Excelファイルが開かれている、または破損している
- 解決: Excelを閉じる、ファイル権限確認、テンプレートファイル再確認

**バーコード生成失敗**
- 原因: 患者IDやドキュメント番号が不正、または出力パスに書き込み権限がない
- 解決: パスの権限確認、config.ini の Barcode 設定確認

**データベース接続エラー**
- 原因: ldtp_app.db ファイルが破損、ディスク容量不足
- 解決: DB ファイル削除（再初期化）、ディスク容量確認

## ライセンス

このプロジェクトのライセンス情報についてはLICENSEファイルを参照してください。

## 参考資料

- [CHANGELOG.md](./CHANGELOG.md): バージョン変更履歴
- [Flet ドキュメント](https://flet.dev): UI フレームワーク
- [SQLAlchemy ドキュメント](https://docs.sqlalchemy.org): ORM ライブラリ
- [openpyxl ドキュメント](https://openpyxl.readthedocs.io): Excel 操作
