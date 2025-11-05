import flet as ft


class DropdownItems:
    def __init__(self):
        self.items = {
            'target_achievement': ['概ね達成', '概ね70%達成', '概ね50%達成', '未達成', '(空欄)'],
            'diet': ['食事量を適正にする', "塩分量を適正にする", '水分摂取量を増やす', '食物繊維の摂取量を増やす',
                     'ゆっくり食べる','間食を減らす', 'アルコールを控える', '脂肪の多い食品や甘い物を控える',
                     '揚げ物や炒め物などを減らす', '1日3食を規則正しくとる', '今回は指導の必要なし', '(空欄)'],
            'exercise_prescription': ['ウォーキング', 'ストレッチ体操', '筋力トレーニング', '自転車', '畑仕事',
                                      '今回は指導の必要なし', '(空欄)'],
            'exercise_time': ['10分', '20分', '30分', '60分', '(空欄)'],
            'exercise_frequency': ['毎日', '週に5日', '週に3日', '週に2日', '(空欄)'],
            'exercise_intensity': ['息が弾む程度', 'ニコニコペース', '少し汗をかく程度', '息切れしない程度', '(空欄)'],
            'daily_activity': ['3000歩', '5000歩', '6000歩', '8000歩', '10000歩', 'ストレッチ運動を主に行う', '(空欄)'],
        }

    def get_options(self, key):
        return [ft.dropdown.Option(option) for option in self.items.get(key, [])]

    def add_item(self, key, options):
        self.items[key] = options

    def create_dropdown(self, key, label, width, on_change=None, font_size=13):
        return ft.Dropdown(
            label=label,
            width=width,
            options=self.get_options(key),
            on_change=on_change,
            text_style=ft.TextStyle(size=font_size),
            border_color=ft.colors.ON_SURFACE_VARIANT,
            focused_border_color=ft.colors.PRIMARY,
            color=ft.colors.ON_SURFACE,
        )
