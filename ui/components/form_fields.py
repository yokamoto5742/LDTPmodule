import configparser
import flet as ft
from ...services.treatment_plan import DropdownItems

# 設定ファイルの読み込み
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
input_height = config.getint('UI', 'input_height', fallback=50)
text_height = config.getint('UI', 'text_height', fallback=40)


def create_form_fields(dropdown_items=None):
    """
    治療計画書フォームの入力フィールド群を作成する

    Args:
        dropdown_items (DropdownItems, optional): ドロップダウンの選択肢を管理するオブジェクト

    Returns:
        tuple: 作成された入力フィールドのタプル
    """
    if dropdown_items is None:
        dropdown_items = DropdownItems()

    # 目標達成状況のドロップダウン
    target_achievement = create_blue_outlined_dropdown(
        dropdown_items,
        'target_achievement',
        "目標達成状況(2回目以降)",
        400
    )

    # 食事関連のドロップダウン
    diet1 = dropdown_items.create_dropdown('diet', "食事1", 400)
    diet2 = dropdown_items.create_dropdown('diet', "食事2", 400)
    diet3 = dropdown_items.create_dropdown('diet', "食事3", 400)
    diet4 = dropdown_items.create_dropdown('diet', "食事4", 400)

    # 運動関連のドロップダウン
    exercise_prescription = dropdown_items.create_dropdown('exercise_prescription', "運動処方", 200)
    exercise_time = dropdown_items.create_dropdown('exercise_time', "時間", 200)
    exercise_frequency = dropdown_items.create_dropdown('exercise_frequency', "頻度", 200)
    exercise_intensity = dropdown_items.create_dropdown('exercise_intensity', "強度", 200)
    daily_activity = dropdown_items.create_dropdown('daily_activity', "日常生活の活動量", 300)

    # 高さの設定
    for dropdown in [target_achievement, diet1, diet2, diet3, diet4, exercise_prescription,
                     exercise_time, exercise_frequency, exercise_intensity, daily_activity]:
        dropdown.height = input_height

    # フォーカス移動のハンドラを設定
    def create_focus_handler(next_field):
        return lambda _: next_field.focus()

    target_achievement.on_change = create_focus_handler(diet1)
    diet1.on_change = create_focus_handler(diet2)
    diet2.on_change = create_focus_handler(diet3)
    diet3.on_change = create_focus_handler(diet4)
    diet4.on_change = create_focus_handler(exercise_prescription)
    exercise_prescription.on_change = create_focus_handler(exercise_time)
    exercise_time.on_change = create_focus_handler(exercise_frequency)
    exercise_frequency.on_change = create_focus_handler(exercise_intensity)
    exercise_intensity.on_change = create_focus_handler(daily_activity)

    return (exercise_prescription, exercise_time, exercise_frequency, exercise_intensity,
            daily_activity, target_achievement, diet1, diet2, diet3, diet4)


def create_blue_outlined_dropdown(dropdown_items, key, label, width):
    """
    青い枠線のドロップダウンフィールドを作成する

    Args:
        dropdown_items (DropdownItems): ドロップダウンの選択肢を管理するオブジェクト
        key (str): 選択肢のカテゴリキー
        label (str): ドロップダウンのラベル
        width (int): ドロップダウンの幅

    Returns:
        ft.Dropdown: 作成されたドロップダウンオブジェクト
    """
    return ft.Dropdown(
        label=label,
        width=width,
        options=dropdown_items.get_options(key),
        border_color=ft.colors.BLUE,
        border_width=3,
        focused_border_color=ft.colors.BLUE,
        focused_border_width=3,
        text_style=ft.TextStyle(size=13),
        color=ft.colors.ON_SURFACE,
    )


def create_datepicker_row(date_value_field, on_date_picker_open=None):
    """
    日付選択用の行を作成する（テキストフィールドと日付選択ボタンの組み合わせ）

    Args:
        date_value_field (ft.TextField): 日付表示用テキストフィールド
        on_date_picker_open (callable, optional): 日付選択ボタンクリック時のコールバック

    Returns:
        ft.Row: 日付選択用の行
    """
    date_button = ft.ElevatedButton(
        "日付選択",
        icon=ft.icons.CALENDAR_TODAY,
        on_click=on_date_picker_open,
        style=ft.ButtonStyle(
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
        elevation=3
    )

    return ft.Row([date_value_field, date_button])


def create_text_field(label, width=150, read_only=False, value="", on_change=None):
    """
    テキスト入力フィールドを作成する

    Args:
        label (str): フィールドのラベル
        width (int, optional): フィールドの幅
        read_only (bool, optional): 読み取り専用かどうか
        value (str, optional): 初期値
        on_change (callable, optional): 値変更時のコールバック

    Returns:
        ft.TextField: 作成されたテキストフィールド
    """
    return ft.TextField(
        label=label,
        width=width,
        read_only=read_only,
        value=value,
        on_change=on_change,
        height=input_height,
        text_style=ft.TextStyle(size=13),
        border_color=ft.colors.ON_SURFACE_VARIANT,
        focused_border_color=ft.colors.PRIMARY,
        color=ft.colors.ON_SURFACE,
    )


def create_long_text_field(label, width=800, value="", on_submit=None):
    """
    長いテキスト入力用のフィールドを作成する

    Args:
        label (str): フィールドのラベル
        width (int, optional): フィールドの幅
        value (str, optional): 初期値
        on_submit (callable, optional): 送信時のコールバック

    Returns:
        ft.TextField: 作成された長いテキストフィールド
    """
    return ft.TextField(
        label=label,
        width=width,
        value=value,
        on_submit=on_submit,
        text_style=ft.TextStyle(size=13),
        height=text_height,
        border_color=ft.colors.ON_SURFACE_VARIANT,
        focused_border_color=ft.colors.PRIMARY,
        color=ft.colors.ON_SURFACE,
    )


def create_checkbox(label, value=False, on_change=None):
    """
    チェックボックスを作成する

    Args:
        label (str): チェックボックスのラベル
        value (bool, optional): 初期値
        on_change (callable, optional): 値変更時のコールバック

    Returns:
        ft.Checkbox: 作成されたチェックボックス
    """
    return ft.Checkbox(
        label=label,
        value=value,
        on_change=on_change,
        height=text_height,
    )


def create_button(text, on_click=None, icon=None, **button_style):
    """
    ボタンを作成する

    Args:
        text (str): ボタンのテキスト
        on_click (callable, optional): クリック時のコールバック
        icon (str, optional): ボタンのアイコン
        **button_style: ボタンのスタイル設定

    Returns:
        ft.ElevatedButton: 作成されたボタン
    """
    if not button_style:
        button_style = {
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

    return ft.ElevatedButton(
        text,
        on_click=on_click,
        icon=icon,
        **button_style
    )
