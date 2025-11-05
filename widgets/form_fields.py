import flet as ft


def create_blue_outlined_dropdown(dropdown_items, key, label, width, font_size=13):
    """青枠ドロップダウン作成"""
    return ft.Dropdown(
        label=label,
        width=width,
        options=dropdown_items.get_options(key),
        border_color=ft.colors.BLUE,
        border_width=3,
        focused_border_color=ft.colors.BLUE,
        focused_border_width=3,
        text_style=ft.TextStyle(size=font_size),
        color=ft.colors.ON_SURFACE,
    )


def create_form_fields(dropdown_items, input_height, font_size=13):
    """フォームフィールド作成"""
    target_achievement = create_blue_outlined_dropdown(
        dropdown_items,
        'target_achievement',
        "目標達成状況(2回目以降)",
        300,
        font_size
    )
    diet1 = dropdown_items.create_dropdown('diet', "食事1", 250, font_size=font_size)
    diet2 = dropdown_items.create_dropdown('diet', "食事2", 250, font_size=font_size)
    diet3 = dropdown_items.create_dropdown('diet', "食事3", 250, font_size=font_size)
    diet4 = dropdown_items.create_dropdown('diet', "食事4", 250, font_size=font_size)
    exercise_prescription = dropdown_items.create_dropdown('exercise_prescription', "運動処方", 200, font_size=font_size)
    exercise_time = dropdown_items.create_dropdown('exercise_time', "時間", 200, font_size=font_size)
    exercise_frequency = dropdown_items.create_dropdown('exercise_frequency', "頻度", 200, font_size=font_size)
    exercise_intensity = dropdown_items.create_dropdown('exercise_intensity', "強度", 200, font_size=font_size)
    daily_activity = dropdown_items.create_dropdown('daily_activity', "日常生活の活動量", 200, font_size=font_size)

    for dropdown in [target_achievement, diet1, diet2, diet3, diet4, exercise_prescription,
                     exercise_time, exercise_frequency, exercise_intensity, daily_activity]:
        dropdown.height = input_height

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
