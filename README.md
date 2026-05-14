# 生活習慣病療養計画書作成アプリ LDTPapp

生活習慣病（高血圧症・脂質異常症・糖尿病）の**療養計画書を、外来の流れを止めずに作成する**Windowsデスクトップアプリです。患者ごとの計画内容をSQLiteに記録し、Excelテンプレート（xlsm）へ自動で流し込んで、バーコード付き文書を生成します。

## 目次

- [解決したい課題](#解決したい課題)
- [特徴](#特徴)
- [動作環境](#動作環境)
- [インストール方法](#インストール方法)
- [使い方](#使い方)
- [設定（config.ini）](#設定configini)
- [設計ノート（なぜこの作りなのか）](#設計ノートなぜこの作りなのか)
- [アーキテクチャ](#アーキテクチャ)
- [拡張ポイント（フォークして使う方へ）](#拡張ポイントフォークして使う方へ)
- [トラブルシューティング](#トラブルシューティング)
- [ライセンス](#ライセンス)
- [更新履歴](#更新履歴)

## 解決したい課題

導入前、療養計画書は**Excelファイルのテンプレートに毎回手入力**して作成していました。

- ファイルに患者ごとのデータが残らない → **毎回ゼロから作り直し**
- 計画内容は患者ごとにほぼ同じ → **同じ入力作業の繰り返しで時間が溶ける**
- 忙しい外来の中で、この重複作業が地味に診療を圧迫する

このアプリは「**一度入力した計画は患者に紐づけて保存し、次回は呼び出して微修正するだけ**」という状態を作ることで、この繰り返しを消すのが目的です。

## 特徴

- **患者ごとの計画を永続化** — 作成した計画書の内容をSQLiteに保存。次回受診時は患者IDで呼び出し、変わった項目だけ直して再発行できる。
- **疾病別テンプレート** — 主病名・目標数値別にデフォルト値をDB管理。「ほぼ同じ内容」を初期値として持たせ、入力を最小化する。
- **Excel(xlsm)テンプレートをそのまま活用** — ネット上で配布されている療養計画書のExcelテンプレートを流用可能。印刷・電子カルテへのPDF保存といった後処理はExcelマクロ側にボタンで足せる（[設計ノート参照](#1-pdf直接生成ではなくexcelxlsmを採用した理由)）。
- **バーコードを画像として焼き込み** — Excelアドイン型のバーコードに依存しない。アドインはExcelの更新で表示できなくなるリスクがあるため、`python-barcode`で生成した画像をセルに配置する（[設計ノート参照](#3-バーコードはアドインではなく画像として配置)）。
- **サーバーレスなSQLite** — DBは実体がファイル1つ。院内ファイルサーバーに置けば、各電子カルテ端末から参照できる（[設計ノート参照](#2-postgresqlではなくsqliteを使い続ける理由)）。
- **pat.csv の自動監視** — 電子カルテが出力する患者データCSVを watchdog で監視し、更新を自動でUIへ反映。

## 動作環境

- Windows 10 64bit 以上
- Python 3.11 以上
- メモリ 4GB 以上推奨

## インストール方法

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

4. `utils/config.ini` を自院の環境に合わせて編集（特にテンプレートパス・出力パス・pat.csvのパス。詳細は[設定](#設定configini)）

5. アプリケーションを起動
   ```bash
   python main.py
   ```
   起動時に pat.csv の存在を確認し、データベースを自動初期化します。

## 使い方

### 基本的なワークフロー

1. **起動** — `python main.py`
2. **患者を選択** — 患者IDを入力・検索すると、対象患者の情報（前回の計画があれば含む）が自動読み込みされる
3. **計画書を作成** — 主病名を選択 → シート名（目標数値別）を選択 → 目標値・食事/運動処方などを入力。テンプレートのデフォルト値が初期表示されるので、変更点だけ直す
4. **文書を生成** — 「新規登録して印刷」で xlsm を生成
   - ファイル名: `{患者ID}{文書番号}{部門ID}{医師ID}{日付}{時刻}.xlsm`
   - 出力先: `C:\Shinseikai\LDTPapp\temp`
   - バーコードを B2 セルに自動挿入

### テンプレート編集

「テンプレート編集」→ 主病名とシート名を選択 → デフォルト値を編集 → 保存。

### データのエクスポート

「設定」画面のCSVエクスポートで患者情報を出力。出力先は `C:\Shinseikai\LDTPapp\export_data`。

## 設定（config.ini）

`utils/config.ini` で全パス・サイズ設定を一元管理します。

```ini
[Database]
db_url = sqlite:///ldtp_app.db

[settings]
window_width = 1200
window_height = 900

[Paths]
template_path = C:\Shinseikai\LDTPapp\LDTPform.xlsm   # 計画書テンプレート(xlsm)
output_path   = C:\Shinseikai\LDTPapp\temp            # 生成文書の出力先

[FilePaths]
patient_data  = C:\InnoKarte\pat.csv                  # 電子カルテが出力する患者CSV
export_folder = C:\Shinseikai\LDTPapp\export_data
manual_pdf    = C:\Shinseikai\LDTPapp\LDTPapp_manual.pdf

[Barcode]
write_text     = false   # バーコード下のテキスト表記
module_height  = 15      # バーコード高さ
image_position = B2      # バーコード挿入セル
```

## 設計ノート（なぜこの作りなのか）

他施設で似たツールを作る人が、同じ判断で迷わないように残しています。

### 1. PDF直接生成ではなくExcel(xlsm)を採用した理由

- 印刷や「電子カルテへPDF保存」といった**後処理を、Excelマクロにボタンとして簡単に追加できる**。PDFを直接吐く設計だと、この拡張が一気に難しくなる。
- 療養計画書の**テンプレートがExcel形式でネット配布されており**、それをそのまま使うのが最短だった。
- マクロは openpyxl の `keep_vba=True` で保持される。

### 2. PostgreSQLではなくSQLiteを使い続ける理由

PostgreSQLはDBサーバーの構築・運用が必要になる。SQLiteは実体がファイル1つなので、**院内ファイルサーバーに置いて各電子カルテ端末から参照する**運用が、サーバーを立てずに実現できる。院内ツールの配布・保守コストを最小化する判断。

### 3. バーコードはアドインではなく画像として配置

Excelアドイン型のバーコードツール（特に古いもの）は、**Excel本体の更新で新バージョンに対応できず、バーコードが表示されなくなる**ことがある。これを避けるため、`python-barcode`（Code128）で生成した画像を openpyxl でセルに貼り付ける方式にしている。Excelのバージョンに依存しないのが利点。

## アーキテクチャ

三層構造:

| 層 | ディレクトリ | 役割 |
|----|-------------|------|
| UI層 | `app/` | Flet コンポーネント・ルーティング・イベントハンドラ |
| サービス層 | `services/` | Excel生成・患者操作・ファイル監視などのビジネスロジック |
| データ層 | `database/` `models/` | SQLAlchemy ORM・接続管理 |

計画書生成の流れ:

```
入力情報 → TreatmentPlanGenerator.generate_plan()
  → テンプレート読み込み（openpyxl, keep_vba=True）
  → populate_common_sheet() でセルへデータ入力
  → バーコード生成（python-barcode）→ B2セルへ画像配置
  → xlsm をtempへ出力 → DBに登録
```

詳細なディレクトリ構成・開発手順は [CLAUDE.md](./CLAUDE.md) を参照してください。

## 拡張ポイント（フォークして使う方へ）

| やりたいこと | 触る場所 |
|-------------|---------|
| 患者項目を増やす | `models/patient_info.py` にカラム追加 → `alembic revision --autogenerate` → `alembic upgrade head` → サービス層・UI層を更新 |
| Excelの記入セルを変える | `C:\Shinseikai\LDTPapp\LDTPform.xlsm` を編集 → `TreatmentPlanGenerator.populate_common_sheet()` のセル指定を更新 |
| 対応疾病・シートを増やす | `MainDisease` / `SheetName` / `Template` マスタにデータ追加 |
| パス・サイズ設定 | `utils/config.ini`（コード内のマジック文字列は `utils/constants.py` で管理） |

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| 「pat.csvが見つかりません」で起動できない | pat.csv が削除された、またはパス誤り | `config.ini` の `FilePaths.patient_data` を確認・修正 |
| テンプレート読み込みエラー | テンプレートのxlsmが他で開かれている／破損 | Excelを閉じる、ファイル権限とテンプレートを確認 |
| バーコード生成失敗 | 患者ID・文書番号が不正、または出力先に書き込み権限なし | 出力パスの権限と `config.ini` の `[Barcode]` 設定を確認 |
| データベース接続エラー | `ldtp_app.db` の破損、ディスク容量不足 | DBファイルを削除して再初期化、ディスク容量を確認 |

## ライセンス

このプロジェクトのライセンス情報については [LICENSE](./docs/LICENSE) を参照してください。

## 更新履歴

更新履歴は [CHANGELOG.md](./docs/CHANGELOG.md) を参照してください。
