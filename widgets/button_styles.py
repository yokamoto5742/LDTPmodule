import flet as ft


def create_theme_aware_button_style(page: ft.Page):
    """テーマ対応ボタンスタイル作成"""
    return {
        "style": ft.ButtonStyle(
            color={
                ft.MaterialState.HOVERED: ft.colors.ON_PRIMARY,  # type: ignore[attr-defined]
                ft.MaterialState.FOCUSED: ft.colors.ON_PRIMARY,  # type: ignore[attr-defined]
                ft.MaterialState.DEFAULT: ft.colors.ON_PRIMARY,  # type: ignore[attr-defined]
            },
            bgcolor={
                ft.MaterialState.HOVERED: ft.colors.PRIMARY_CONTAINER,  # type: ignore[attr-defined]
                ft.MaterialState.FOCUSED: ft.colors.PRIMARY_CONTAINER,  # type: ignore[attr-defined]
                ft.MaterialState.DEFAULT: ft.colors.PRIMARY,  # type: ignore[attr-defined]
            },
            padding=10,
        ),
        "elevation": 3,
    }
