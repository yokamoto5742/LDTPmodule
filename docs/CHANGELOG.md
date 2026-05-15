# 変更履歴

すべての重要な変更はこのファイルに記録されます。

このプロジェクトは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に従い、[セマンティック バージョニング](https://semver.org/lang/ja/) を使用しています。

## [Unreleased]

## [1.0.1] - 2026-05-15

### 変更
- `treatment_plan_service.py`をクラスベースから関数ベースにリファクタリング。イベントハンドラーの呼び出しをシンプル化
- `TemplateManager`クラスを削除し、テンプレート処理を`treatment_plan_service`・`patient_service`・`data_export_service`に統合。機能を維持しながらコード複雑度を低減
- 配置ドキュメント番号（`document_number`）を`config.ini`から読み込むように変更。設定の一元管理を強化

### 修正
- `patient_service.py`のテンプレート参照処理を修正し、リファクタリング後の統合ロジックに対応

## [1.0.0] - 2026-05-12

安定版初回リリース
