import flet as ft
from services.patient_service import fetch_patient_history


def fetch_data(filter_patient_id=None):
    """
    患者履歴データを取得

    Args:
        filter_patient_id: フィルター用の患者ID

    Returns:
        患者履歴データのリスト
    """
    return fetch_patient_history(filter_patient_id)


def create_data_rows(data, on_row_selected):
    """
    データ行を作成

    Args:
        data: 患者履歴データのリスト
        on_row_selected: 行選択時のコールバック関数

    Returns:
        DataRowのリスト
    """
    rows = []
    for item in data:
        row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(item["issue_date"])),
                ft.DataCell(ft.Text(item["department"])),
                ft.DataCell(ft.Text(item["doctor_name"])),
                ft.DataCell(ft.Text(item["main_diagnosis"])),
                ft.DataCell(ft.Text(item["sheet_name"])),
                ft.DataCell(ft.Text(item["count"])),
            ],
            on_select_changed=on_row_selected,
            data=item
        )
        rows.append(row)
    return rows


def build_history_table(table_width):
    """
    計画書一覧テーブルを構築

    Args:
        table_width: テーブルの幅

    Returns:
        DataTableコントロール
    """
    return ft.DataTable(
        width=table_width,
        columns=[
            ft.DataColumn(ft.Text("発行日")),
            ft.DataColumn(ft.Text("診療科")),
            ft.DataColumn(ft.Text("医師")),
            ft.DataColumn(ft.Text("主病名")),
            ft.DataColumn(ft.Text("シート名")),
            ft.DataColumn(ft.Text("回数")),
        ],
        rows=[],
        data_row_max_height=30,
        column_spacing=10,
        horizontal_margin=5,
        heading_row_height=30
    )


def build_buttons(page, handlers, button_style):
    """
    メインボタンを構築

    Args:
        page: Fletのページオブジェクト
        handlers: イベントハンドラの辞書
        button_style: ボタンスタイル

    Returns:
        Rowコントロール
    """
    return ft.Row(
        controls=[
            ft.ElevatedButton(
                "新規作成",
                on_click=handlers['open_create'],
                **button_style
            ),
            ft.ElevatedButton(
                "前回計画コピー",
                on_click=handlers['copy_data'],
                **button_style
            ),
            ft.ElevatedButton(
                "テンプレート編集",
                on_click=handlers['open_template'],
                **button_style
            ),
            ft.ElevatedButton(
                "閉じる",
                on_click=handlers['on_close'],
                **button_style
            ),
        ],
    )


def build_create_buttons(page, handlers, button_style):
    """
    新規作成画面のボタンを構築

    Args:
        page: Fletのページオブジェクト
        handlers: イベントハンドラの辞書
        button_style: ボタンスタイル

    Returns:
        Rowコントロール
    """
    return ft.Row(
        controls=[
            ft.ElevatedButton("新規登録して印刷", on_click=handlers['create_new_plan'], **button_style),
            ft.ElevatedButton("新規登録", on_click=handlers['save_new_plan'], **button_style),
            ft.ElevatedButton("戻る", on_click=handlers['open_route'], **button_style),
        ]
    )


def build_edit_buttons(page, handlers, button_style):
    """
    編集画面のボタンを構築

    Args:
        page: Fletのページオブジェクト
        handlers: イベントハンドラの辞書
        button_style: ボタンスタイル

    Returns:
        Rowコントロール
    """
    return ft.Row(
        controls=[
            ft.ElevatedButton("保存", on_click=handlers['save_data'], **button_style),
            ft.ElevatedButton("印刷", on_click=handlers['print_plan'], **button_style),
            ft.ElevatedButton("削除", on_click=handlers['delete_data'], **button_style),
            ft.ElevatedButton("戻る", on_click=handlers['open_route'], **button_style),
        ]
    )


def build_template_buttons(page, handlers, button_style):
    """
    テンプレート画面のボタンを構築

    Args:
        page: Fletのページオブジェクト
        handlers: イベントハンドラの辞書
        button_style: ボタンスタイル

    Returns:
        Rowコントロール
    """
    return ft.Row(
        controls=[
            ft.ElevatedButton("テンプレート保存", on_click=handlers['save_template'], **button_style),
            ft.ElevatedButton("戻る", on_click=handlers['open_route'], **button_style),
        ]
    )


def build_guidance_items(fields, text_height):
    """
    指導項目のレイアウトを構築

    Args:
        fields: フォームフィールドの辞書
        text_height: テキストフィールドの高さ

    Returns:
        Columnコントロール
    """
    return ft.Column([
        ft.Row([
            fields['target_achievement'],
            fields['target_weight'], ft.Text("kg", size=13),
            fields['target_bp'], ft.Text("mmHg", size=13),
            fields['target_hba1c'], ft.Text("%", size=13),
        ]),
        ft.Row([
            fields['diet1'], fields['diet2'], fields['diet3'], fields['diet4']
        ]),
        fields['diet_comment'],
        ft.Row([
            fields['exercise_prescription'], fields['exercise_time'],
            fields['exercise_frequency'], fields['exercise_intensity'],
            fields['daily_activity']
        ]),
        fields['exercise_comment'],
        ft.Row([
            fields['nonsmoker'], fields['smoking_cessation']
        ]),
        ft.Row([
            fields['other1'], fields['other2']
        ]),
        ft.Row([
            fields['ophthalmology'], fields['dental'], fields['cancer_screening']
        ]),
    ])


def build_guidance_items_template(fields, text_height):
    """
    テンプレート用の指導項目のレイアウトを構築

    Args:
        fields: フォームフィールドの辞書
        text_height: テキストフィールドの高さ

    Returns:
        Columnコントロール
    """
    return ft.Column([
        ft.Row([
            fields['target_achievement'],
            fields['target_weight'], ft.Text("kg", size=13),
            fields['target_bp'], ft.Text("mmHg", size=13),
            fields['target_hba1c'], ft.Text("%", size=13),
        ]),
        ft.Row([
            fields['diet1'], fields['diet2'], fields['diet3'], fields['diet4']
        ]),
        fields['diet_comment'],
        ft.Row([
            fields['exercise_prescription'], fields['exercise_time'],
            fields['exercise_frequency'], fields['exercise_intensity'],
            fields['daily_activity']
        ]),
        fields['exercise_comment'],
        ft.Row([
            fields['nonsmoker'], fields['smoking_cessation']
        ]),
        ft.Row([
            fields['other1'], fields['other2']
        ]),
        ft.Row([
            fields['ophthalmology'], fields['dental'], fields['cancer_screening']
        ]),
    ])
