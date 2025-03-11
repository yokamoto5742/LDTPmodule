import flet as ft


class FormFieldFactory:
    """フォームフィールドを生成するファクトリークラス"""

    @staticmethod
    def create_text_field(label, width=None, read_only=False, value="",
                          on_change=None, on_submit=None, height=None,
                          text_size=13, border_color=None):
        """テキストフィールドを生成する"""
        return ft.TextField(
            label=label,
            width=width,
            read_only=read_only,
            value=value,
            on_change=on_change,
            on_submit=on_submit,
            height=height,
            text_style=ft.TextStyle(size=text_size),
            border_color=border_color or ft.colors.ON_SURFACE_VARIANT,
            focused_border_color=ft.colors.PRIMARY,
            color=ft.colors.ON_SURFACE,
        )

    @staticmethod
    def create_dropdown(label, options, width=None, value=None,
                        on_change=None, height=None, text_size=13,
                        border_color=None, border_width=None):
        """ドロップダウンを生成する"""
        return ft.Dropdown(
            label=label,
            width=width,
            options=options,
            value=value,
            on_change=on_change,
            height=height,
            text_style=ft.TextStyle(size=text_size),
            border_color=border_color or ft.colors.ON_SURFACE_VARIANT,
            border_width=border_width,
            focused_border_color=ft.colors.PRIMARY,
            focused_border_width=border_width,
            color=ft.colors.ON_SURFACE,
        )

    @staticmethod
    def create_checkbox(label, value=False, on_change=None, height=None):
        """チェックボックスを生成する"""
        return ft.Checkbox(
            label=label,
            value=value,
            on_change=on_change,
            height=height,
        )

    @staticmethod
    def create_button(text, on_click, style=None, elevation=None, icon=None):
        """ボタンを生成する"""
        return ft.ElevatedButton(
            text=text,
            on_click=on_click,
            style=style,
            elevation=elevation,
            icon=icon
        )

    @staticmethod
    def create_date_picker(on_change=None, on_dismiss=None):
        """日付選択ピッカーを生成する"""
        return ft.DatePicker(
            on_change=on_change,
            on_dismiss=on_dismiss
        )


class ThemeAwareButtonStyle:
    """テーマに応じたボタンスタイルを提供するクラス"""

    @staticmethod
    def get_style(page: ft.Page):
        """ページのテーマに合わせたボタンスタイルを取得する"""
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
