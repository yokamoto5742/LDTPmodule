from typing import Any

import flet as ft


def create_theme_aware_button_style(page: ft.Page) -> dict[str, Any]:
    """テーマ対応ボタンスタイル作成"""
    return {
        "style": ft.ButtonStyle(
            color={  # type: ignore[arg-type]
                ft.MaterialState.HOVERED: ft.colors.ON_PRIMARY,
                ft.MaterialState.FOCUSED: ft.colors.ON_PRIMARY,
                ft.MaterialState.DEFAULT: ft.colors.ON_PRIMARY,
            },
            bgcolor={  # type: ignore[arg-type]
                ft.MaterialState.HOVERED: ft.colors.PRIMARY_CONTAINER,
                ft.MaterialState.FOCUSED: ft.colors.PRIMARY_CONTAINER,
                ft.MaterialState.DEFAULT: ft.colors.PRIMARY,
            },
            padding=10,
        ),
        "elevation": 3,
    }
