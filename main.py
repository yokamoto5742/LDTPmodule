import os
import sys
import flet as ft
from datetime import datetime

from models.patient import PatientInfo
from models.template import MainDisease, SheetName, Template
from database.connection import init_database, get_session
from database.repositories.patient_repo import PatientRepository
from database.repositories.template_repo import TemplateRepository
from services.treatment_plan import TreatmentPlanGenerator
from services.csv_service import CSVService
from services.barcode_service import BarcodeService
from ui.components.form_fields import DropdownItems, create_blue_outlined_dropdown
from ui.components.dialogs import create_settings_dialog, create_error_dialog
from ui.views.patient_form import PatientForm
from ui.views.template_editor import TemplateEditor
from ui.views.main_view import MainView
from ui.controllers.main_controller import MainController
from ui.controllers.form_controller import FormController
from utils.config import ConfigManager
from utils.date_utils import format_date, calculate_issue_date_age
from utils.file_utils import check_file_exists, create_file_monitor

# バージョン情報
VERSION = "1.1.4"
LAST_UPDATED = "2024/09/28"


def main(page: ft.Page):
    """
    アプリケーションのメイン関数

    Args:
        page: Fletページオブジェクト
    """
    # 設定の読み込み
    config = ConfigManager()

    # ファイル監視の開始
    csv_file_path = config.get_value('FilePaths', 'patient_data')
    observer = create_file_monitor(csv_file_path, lambda: page.window.close())

    # ファイルの存在確認
    if not check_file_exists(csv_file_path):
        page.window.close()
        return

    # データベースの初期化
    db_url = config.get_database_url()
    init_database(db_url)

    # アプリケーションの初期化
    initialize_application(page, config)


def initialize_application(page: ft.Page, config: ConfigManager):
    """
    アプリケーションの初期化

    Args:
        page: Fletページオブジェクト
        config: 設定マネージャー
    """
    # ページの設定
    setup_page(page, config)

    # サービスの初期化
    csv_service = CSVService(config)
    barcode_service = BarcodeService(config)
    treatment_plan_generator = TreatmentPlanGenerator(config, barcode_service)

    # リポジトリの初期化
    patient_repo = PatientRepository()
    template_repo = TemplateRepository()

    # 初期データの確認と挿入
    with get_session() as session:
        template_repo.initialize_default_data(session)

    # UI項目の初期化
    ui_settings = config.get_ui_settings()
    dropdown_items = DropdownItems()

    # フォームの初期化
    patient_form = PatientForm(page, ui_settings['input_height'], ui_settings['text_height'], dropdown_items)

    # ビューの初期化
    template_editor = TemplateEditor(page, patient_form, create_button_style(page))
    main_view = MainView(page, patient_form, create_button_style(page))

    # コントローラーの初期化
    form_controller = FormController(
        page=page,
        patient_form=patient_form,
        patient_repo=patient_repo,
        template_repo=template_repo,
        treatment_plan_generator=treatment_plan_generator
    )

    main_controller = MainController(
        page=page,
        main_view=main_view,
        template_editor=template_editor,
        form_controller=form_controller,
        patient_repo=patient_repo,
        template_repo=template_repo,
        csv_service=csv_service,
        config=config,
        version=VERSION,
        last_updated=LAST_UPDATED
    )

    # 初期データの読み込み
    error_message, df_patients = csv_service.load_patient_data()
    if df_patients is not None and not df_patients.empty:
        initial_patient_id = int(df_patients.iloc[0, 2])
        patient_form.patient_id.value = str(initial_patient_id)
        main_controller.load_patient_info(initial_patient_id)
        main_controller.update_history(initial_patient_id)

    # ルート変更時の処理を設定
    page.on_route_change = main_controller.route_change
    page.on_view_pop = main_controller.view_pop

    # スタートアップ時の処理
    page.window.on_resized = lambda _: main_controller.on_startup()

    # 初期ルートに移動
    page.go(page.route)


def setup_page(page: ft.Page, config: ConfigManager):
    """
    Fletページの設定

    Args:
        page: Fletページオブジェクト
        config: 設定マネージャー
    """
    # ウィンドウサイズの設定
    window_settings = config.get_window_settings()
    page.title = "生活習慣病療養計画書"
    page.window.width = window_settings['width']
    page.window.height = window_settings['height']

    # ロケール設定
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[
            ft.Locale("ja", "JP"),
            ft.Locale("en", "US")
        ],
        current_locale=ft.Locale("ja", "JP")
    )

    # テーマの設定
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)


def create_button_style(page: ft.Page):
    """
    ボタンスタイルの作成

    Args:
        page: Fletページオブジェクト

    Returns:
        dict: ボタンスタイル設定
    """
    return {
        "style": ft.ButtonStyle(
            color={
                ft.MaterialState.HOVERED: ft.colors.ON_PRIMARY,
                ft.MaterialState.FOCUSED: ft.colors.ON_PRIMARY,
                ft.MaterialState.DEFAULT: ft.colors.ON_PRIMARY,
            },
            bgcolor={
                ft.MaterialState.HOVERED: ft.colors.PRIMARY_CONTAINER,
                ft.MaterialState.FOCUSED: ft.colors.PRIMARY_CONTAINER,
                ft.MaterialState.DEFAULT: ft.colors.PRIMARY,
            },
            padding=10,
        ),
        "elevation": 3,
    }


if __name__ == "__main__":
    ft.app(target=main)