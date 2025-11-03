import flet as ft


def create_blue_outlined_dropdown(dropdown_items, key, label, width):
    """青枠ドロップダウン作成"""
    return ft.Dropdown(
        label=label,
        width=width,
        options=dropdown_items.get_options(key),
        border_color=ft.colors.BLUE,  # type: ignore[attr-defined]
        border_width=3,
        focused_border_color=ft.colors.BLUE,  # type: ignore[attr-defined]
        focused_border_width=3,
        text_style=ft.TextStyle(size=13),
        color=ft.colors.ON_SURFACE,  # type: ignore[attr-defined]
    )


def create_form_fields(dropdown_items, input_height):
    """フォームフィールド作成"""
    target_achievement = create_blue_outlined_dropdown(
        dropdown_items,
        'target_achievement',
        "目標達成状況(2回目以降)",
        400
    )
    diet1 = dropdown_items.create_dropdown('diet', "食事1", 400)
    diet2 = dropdown_items.create_dropdown('diet', "食事2", 400)
    diet3 = dropdown_items.create_dropdown('diet', "食事3", 400)
    diet4 = dropdown_items.create_dropdown('diet', "食事4", 400)
    exercise_prescription = dropdown_items.create_dropdown('exercise_prescription', "運動処方", 200)
    exercise_time = dropdown_items.create_dropdown('exercise_time', "時間", 200)
    exercise_frequency = dropdown_items.create_dropdown('exercise_frequency', "頻度", 200)
    exercise_intensity = dropdown_items.create_dropdown('exercise_intensity', "強度", 200)
    daily_activity = dropdown_items.create_dropdown('daily_activity', "日常生活の活動量", 300)

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
