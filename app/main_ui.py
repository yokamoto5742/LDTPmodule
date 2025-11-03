from datetime import datetime

import flet as ft
from database import get_session_factory
from services.patient_service import load_patient_data, load_main_diseases, load_sheet_names
from widgets import DropdownItems, create_form_fields, create_theme_aware_button_style
from app.dialogs import DialogManager
from app.event_handlers import EventHandlers
from app.routes import RouteManager
from app.ui_builder import (
    fetch_data, create_data_rows, build_history_table,
    build_buttons, build_create_buttons, build_edit_buttons,
    build_template_buttons, build_guidance_items, build_guidance_items_template
)
from utils.config_manager import load_config

Session = get_session_factory()


def create_ui(page: ft.Page):
    """メインUIを作成"""
    # 設定読み込み
    config = load_config()
    input_height = config.getint("UI", "input_height", fallback=60)
    text_height = config.getint("UI", "text_height", fallback=60)
    table_width = config.getint("DataTable", "width", fallback=1200)
    export_folder = config.get("FilePaths", "export_folder")
    manual_pdf_path = config.get("FilePaths", "manual_pdf", fallback="")

    page.title = "LDTPapp"
    page.window.width = config.getint("settings", "window_width", fallback=1200)
    page.window.height = config.getint("settings", "window_height", fallback=900)
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.SYSTEM

    # スタートアップハンドラ
    def on_startup(e):
        if page.window.width < 1000:
            snack_bar = ft.SnackBar(
                content=ft.Text("ウィンドウサイズが小さすぎます。幅を1000ピクセル以上にしてください。")
            )
            snack_bar.open = True
            page.overlay.append(snack_bar)
            page.update()

    # 患者データ読み込み
    error_message, df_patients = load_patient_data()
    initial_patient_id = ""
    if error_message:
        error_message, df_patients = "", None
    elif not df_patients.empty:
        initial_patient_id = str(df_patients.iloc[0, 2])

    # ドロップダウンアイテムの作成
    dropdown_items = DropdownItems()

    # 患者情報フィールドの作成
    patient_id = ft.TextField(
        label="患者ID",
        value=initial_patient_id,
        width=150,
        height=input_height
    )
    issue_date_value = ft.TextField(label="発行日", width=150, read_only=True, height=input_height)
    name_value = ft.TextField(label="氏名", read_only=True, width=150, height=input_height)
    kana_value = ft.TextField(label="カナ", read_only=True, width=150, height=input_height)
    gender_value = ft.TextField(label="性別", read_only=True, width=100, height=input_height)
    birthdate_value = ft.TextField(label="生年月日", read_only=True, width=150, height=input_height)
    doctor_id_value = ft.TextField(label="医師ID", read_only=True, width=100, height=input_height)
    doctor_name_value = ft.TextField(label="医師名", read_only=True, width=150, height=input_height)
    department_id_value = ft.TextField(label="診療科ID", read_only=True, width=100, height=input_height)
    department_value = ft.TextField(label="診療科", read_only=True, width=150, height=input_height)

    # 主病名・シート名フィールドの作成
    main_disease_options = load_main_diseases()
    main_diagnosis = ft.Dropdown(
        label="主病名",
        options=main_disease_options,
        width=350,
        height=input_height,
        border_color=ft.colors.BLUE,
        border_width=2,
    )

    sheet_name_options = load_sheet_names()
    sheet_name_dropdown = ft.Dropdown(
        label="シート名",
        options=sheet_name_options,
        width=350,
        height=input_height,
        border_color=ft.colors.BLUE,
        border_width=2,
    )

    creation_count = ft.TextField(label="作成回数", value="1", width=80, text_size=13, height=text_height)

    # 目標フィールドの作成
    target_weight = ft.TextField(label="目標体重", width=150, value="", text_size=13, height=input_height)
    target_bp = ft.TextField(label="目標血圧", width=150, text_size=13, height=input_height)
    target_hba1c = ft.TextField(label="目標HbA1c", width=150, text_size=13, height=input_height)
    goal1 = ft.TextField(
        label="①達成目標：患者と相談した目標",
        width=800,
        value="主病名とシート名を選択してください",
        text_size=13,
        height=text_height
    )
    goal2 = ft.TextField(
        label="②行動目標：患者と相談した目標",
        width=800,
        text_size=13,
        height=text_height
    )

    # フォームフィールドの作成
    (exercise_prescription, exercise_time, exercise_frequency, exercise_intensity,
     daily_activity, target_achievement, diet1, diet2, diet3, diet4) = create_form_fields(dropdown_items, input_height)

    diet_comment = ft.TextField(
        label="食事フリーコメント",
        width=800,
        text_size=13,
        height=text_height
    )
    exercise_comment = ft.TextField(
        label="運動フリーコメント",
        width=800,
        text_size=13,
        height=text_height
    )

    nonsmoker = ft.Checkbox(label="非喫煙者である", height=text_height)
    smoking_cessation = ft.Checkbox(label="禁煙の実施方法等を指示", height=text_height)
    other1 = ft.TextField(label="その他1", value="", width=400, text_size=13, height=text_height)
    other2 = ft.TextField(label="その他2", value="", width=400, text_size=13, height=text_height)
    ophthalmology = ft.Checkbox(label="眼科", height=text_height)
    dental = ft.Checkbox(label="歯科", height=text_height)
    cancer_screening = ft.Checkbox(label="がん検診", height=text_height)

    # フィールド辞書の作成
    fields = {
        'patient_id': patient_id,
        'issue_date_value': issue_date_value,
        'name_value': name_value,
        'kana_value': kana_value,
        'gender_value': gender_value,
        'birthdate_value': birthdate_value,
        'doctor_id_value': doctor_id_value,
        'doctor_name_value': doctor_name_value,
        'department_id_value': department_id_value,
        'department_value': department_value,
        'main_diagnosis': main_diagnosis,
        'sheet_name_dropdown': sheet_name_dropdown,
        'creation_count': creation_count,
        'target_weight': target_weight,
        'target_bp': target_bp,
        'target_hba1c': target_hba1c,
        'goal1': goal1,
        'goal2': goal2,
        'target_achievement': target_achievement,
        'diet1': diet1,
        'diet2': diet2,
        'diet3': diet3,
        'diet4': diet4,
        'diet_comment': diet_comment,
        'exercise_prescription': exercise_prescription,
        'exercise_time': exercise_time,
        'exercise_frequency': exercise_frequency,
        'exercise_intensity': exercise_intensity,
        'daily_activity': daily_activity,
        'exercise_comment': exercise_comment,
        'nonsmoker': nonsmoker,
        'smoking_cessation': smoking_cessation,
        'other1': other1,
        'other2': other2,
        'ophthalmology': ophthalmology,
        'dental': dental,
        'cancer_screening': cancer_screening,
    }

    # ダイアログマネージャーの初期化
    dialog_manager = DialogManager(page, fields)

    # イベントハンドラの初期化
    event_handlers = EventHandlers(page, fields, df_patients, dialog_manager)

    # イベントハンドラの設定
    patient_id.on_change = event_handlers.on_patient_id_change
    main_diagnosis.on_change = event_handlers.on_main_diagnosis_change
    sheet_name_dropdown.on_change = event_handlers.on_sheet_name_change
    nonsmoker.on_change = event_handlers.on_tobacco_checkbox_change
    smoking_cessation.on_change = event_handlers.on_tobacco_checkbox_change

    # 日付ピッカーの設定
    issue_date_picker = ft.DatePicker(
        on_change=lambda e: event_handlers.on_issue_date_change(e, issue_date_picker),
        on_dismiss=lambda e: event_handlers.on_date_picker_dismiss(e, issue_date_picker)
    )

    def open_date_picker(e):
        if issue_date_picker not in page.overlay:
            page.overlay.append(issue_date_picker)
        issue_date_picker.open = True
        page.update()

    # 履歴の初期化
    def update_history(filter_patient_id=None):
        data = fetch_data(filter_patient_id)
        history.rows = create_data_rows(data, event_handlers.on_row_selected)
        page.update()

    # EventHandlersにupdate_historyを設定
    event_handlers.update_history = update_history
    event_handlers.fetch_data = fetch_data

    # DialogManagerにupdate_history_callbackを設定
    dialog_manager.update_history_callback = update_history

    data = fetch_data()
    history = build_history_table(table_width)
    history.rows = create_data_rows(data, event_handlers.on_row_selected)

    history_column = ft.Column([history], scroll=ft.ScrollMode.AUTO, width=table_width, height=400)
    history_scrollable = ft.Container(
        content=history_column,
        width=table_width,
        height=400,
        border=ft.border.all(1, ft.colors.BLACK),
        border_radius=5,
        padding=10,
    )

    fields['history'] = history

    # ボタンスタイルの作成
    button_style = create_theme_aware_button_style(page)

    # ルートマネージャーの初期化（ボタン構築前に必要な参照を準備）
    route_manager = None

    # ボタンハンドラ辞書の作成
    button_handlers = {
        'open_create': lambda e: route_manager.open_create(e) if route_manager else None,
        'open_edit': lambda e: route_manager.open_edit(e) if route_manager else None,
        'open_template': lambda e: route_manager.open_template(e) if route_manager else None,
        'open_route': lambda e: route_manager.open_route(e) if route_manager else None,
        'on_close': lambda e: route_manager.on_close(e) if route_manager else None,
        'copy_data': event_handlers.copy_data,
        'delete_data': event_handlers.delete_data,
        'create_new_plan': event_handlers.create_new_plan,
        'save_new_plan': event_handlers.save_new_plan,
        'save_data': event_handlers.save_data,
        'print_plan': event_handlers.print_plan,
        'save_template': event_handlers.save_template,
    }

    # ボタンの作成
    buttons = build_buttons(page, button_handlers, button_style)
    create_buttons = build_create_buttons(page, button_handlers, button_style)
    edit_buttons = build_edit_buttons(page, button_handlers, button_style)
    template_buttons = build_template_buttons(page, button_handlers, button_style)

    settings_button = ft.ElevatedButton(
        "設定",
        on_click=lambda e: dialog_manager.open_settings_dialog(e, export_folder),
        **button_style
    )
    manual_button = ft.ElevatedButton(
        "操作マニュアル",
        on_click=lambda e: route_manager.open_manual_pdf(e) if route_manager else None,
        **button_style
    )
    issue_date_button = ft.ElevatedButton(
        "日付選択",
        icon=ft.icons.CALENDAR_TODAY,
        on_click=open_date_picker,
        **button_style
    )

    issue_date_row = ft.Row([issue_date_value, issue_date_button])

    # 指導項目レイアウトの作成
    guidance_items = build_guidance_items(fields, text_height)
    guidance_items_template = build_guidance_items_template(fields, text_height)

    # UI要素辞書の作成
    ui_elements = {
        'buttons': buttons,
        'create_buttons': create_buttons,
        'edit_buttons': edit_buttons,
        'template_buttons': template_buttons,
        'settings_button': settings_button,
        'manual_button': manual_button,
        'issue_date_button': issue_date_button,
        'issue_date_row': issue_date_row,
        'history_scrollable': history_scrollable,
        'guidance_items': guidance_items,
        'guidance_items_template': guidance_items_template,
        'issue_date_picker': issue_date_picker,
    }

    # ルートマネージャーの初期化（完全版）
    route_manager = RouteManager(page, fields, ui_elements, event_handlers, manual_pdf_path)

    # ページレイアウトの設定
    layout = ft.Column([
        ft.Row(controls=[])
    ])

    page.add(layout)
    update_history()

    # 初期患者情報の読み込み
    if initial_patient_id:
        event_handlers.load_patient_info(int(initial_patient_id))
        patient_id.value = initial_patient_id
        update_history(patient_id.value)

    # イベントハンドラの設定
    page.window.on_resized = on_startup
    page.on_route_change = route_manager.route_change
    page.on_view_pop = route_manager.view_pop
    page.go(page.route)
