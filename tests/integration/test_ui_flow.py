from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from app.dialogs import DialogManager
from app.event_handlers import EventHandlers
from app.routes import RouteManager


@pytest.fixture
def mock_page():
    """Fletページのモック"""
    page = MagicMock()
    page.window.width = 1200
    page.window.height = 900
    page.route = "/"
    page.views = []
    page.overlay = []
    page.scroll = "auto"
    return page


@pytest.fixture
def sample_fields():
    """テスト用フィールド辞書"""
    fields = {
        'patient_id': Mock(value='1001'),
        'issue_date_value': Mock(value='2025/01/15'),
        'name_value': Mock(value='田中太郎'),
        'kana_value': Mock(value='タナカタロウ'),
        'gender_value': Mock(value='男性'),
        'birthdate_value': Mock(value='1985/04/10'),
        'doctor_id_value': Mock(value='101'),
        'doctor_name_value': Mock(value='山田医師'),
        'department_id_value': Mock(value='10'),
        'department_value': Mock(value='内科'),
        'main_diagnosis': Mock(value='糖尿病', options=[]),
        'sheet_name_dropdown': Mock(value='糖尿病用', options=[]),
        'creation_count': Mock(value='1'),
        'target_weight': Mock(value='70.0'),
        'target_bp': Mock(value='130/80'),
        'target_hba1c': Mock(value='7.0'),
        'goal1': Mock(value='目標1'),
        'goal2': Mock(value='目標2'),
        'target_achievement': Mock(value='達成目標'),
        'diet1': Mock(value='食事1'),
        'diet2': Mock(value='食事2'),
        'diet3': Mock(value='食事3'),
        'diet4': Mock(value='食事4'),
        'diet_comment': Mock(value='食事コメント'),
        'exercise_prescription': Mock(value='運動処方'),
        'exercise_time': Mock(value='30分'),
        'exercise_frequency': Mock(value='週3回'),
        'exercise_intensity': Mock(value='中等度'),
        'daily_activity': Mock(value='日常活動'),
        'exercise_comment': Mock(value='運動コメント'),
        'nonsmoker': Mock(value=True),
        'smoking_cessation': Mock(value=False),
        'other1': Mock(value='その他1'),
        'other2': Mock(value='その他2'),
        'ophthalmology': Mock(value=False),
        'dental': Mock(value=False),
        'cancer_screening': Mock(value=False),
        'history': Mock(rows=[]),
    }
    return fields


@pytest.fixture
def sample_df_patients():
    """テスト用患者DataFrameを作成"""
    data = {
        0: [1],
        1: ['田中'],
        2: [1001],
        3: ['田中太郎'],
        4: ['タナカタロウ'],
        5: [1],
        6: [date(1985, 4, 10)],
        7: ['123-4567'],
        8: ['東京都'],
        9: [101],
        10: ['山田医師'],
        11: [''],
        12: [''],
        13: [10],
        14: ['内科'],
    }
    return pd.DataFrame(data)


class TestDialogManager:
    """DialogManagerの統合テスト"""

    def test_init_dialog_manager(self, mock_page, sample_fields):
        """DialogManagerの初期化テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)

        assert dialog_manager.page == mock_page
        assert dialog_manager.fields == sample_fields
        assert dialog_manager.file_picker is not None

    def test_show_error_message(self, mock_page, sample_fields):
        """エラーメッセージ表示テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)

        dialog_manager.show_error_message("テストエラー")

        # overlay にSnackBarが追加されたか確認
        assert len(mock_page.overlay) > 0
        mock_page.update.assert_called()

    def test_show_info_message(self, mock_page, sample_fields):
        """情報メッセージ表示テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)

        dialog_manager.show_info_message("テスト情報")

        assert len(mock_page.overlay) > 0
        mock_page.update.assert_called()

    def test_check_required_fields_success(self, mock_page, sample_fields):
        """必須フィールドチェック成功テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)

        result = dialog_manager.check_required_fields()

        assert result is True

    def test_check_required_fields_missing_main_diagnosis(self, mock_page, sample_fields):
        """主病名未選択時の必須フィールドチェックテスト"""
        sample_fields['main_diagnosis'].value = None
        dialog_manager = DialogManager(mock_page, sample_fields)

        result = dialog_manager.check_required_fields()

        assert result is False

    def test_check_required_fields_missing_sheet_name(self, mock_page, sample_fields):
        """シート名未選択時の必須フィールドチェックテスト"""
        sample_fields['sheet_name_dropdown'].value = None
        dialog_manager = DialogManager(mock_page, sample_fields)

        result = dialog_manager.check_required_fields()

        assert result is False


class TestEventHandlers:
    """EventHandlersの統合テスト"""

    def test_init_event_handlers(self, mock_page, sample_fields, sample_df_patients):
        """EventHandlersの初期化テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, sample_df_patients, dialog_manager)

        assert event_handlers.page == mock_page
        assert event_handlers.fields == sample_fields
        assert event_handlers.df_patients is not None
        assert event_handlers.selected_row is None

    def test_load_patient_info_success(self, mock_page, sample_fields, sample_df_patients):
        """患者情報読み込み成功テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, sample_df_patients, dialog_manager)

        event_handlers.load_patient_info(1001)

        assert sample_fields['patient_id'].value == '1001'
        assert sample_fields['name_value'].value == '田中太郎'
        assert sample_fields['kana_value'].value == 'タナカタロウ'
        assert sample_fields['gender_value'].value == '男性'

    def test_load_patient_info_not_found(self, mock_page, sample_fields, sample_df_patients):
        """患者情報が見つからない場合のテスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, sample_df_patients, dialog_manager)

        event_handlers.load_patient_info(9999)

        # 患者が見つからない場合は空文字列が設定される
        assert sample_fields['issue_date_value'].value == ''
        assert sample_fields['name_value'].value == ''

    def test_on_tobacco_checkbox_change_nonsmoker(self, mock_page, sample_fields, sample_df_patients):
        """非喫煙者チェックボックス変更テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, sample_df_patients, dialog_manager)

        # 非喫煙者をチェック
        sample_fields['nonsmoker'].value = True
        mock_event = Mock()
        mock_event.control = sample_fields['nonsmoker']

        event_handlers.on_tobacco_checkbox_change(mock_event)

        # 禁煙の実施方法がFalseになることを確認
        assert sample_fields['smoking_cessation'].value is False

    def test_on_tobacco_checkbox_change_smoking_cessation(self, mock_page, sample_fields, sample_df_patients):
        """禁煙の実施方法チェックボックス変更テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, sample_df_patients, dialog_manager)

        # 禁煙の実施方法をチェック
        sample_fields['smoking_cessation'].value = True
        mock_event = Mock()
        mock_event.control = sample_fields['smoking_cessation']

        event_handlers.on_tobacco_checkbox_change(mock_event)

        # 非喫煙者がFalseになることを確認
        assert sample_fields['nonsmoker'].value is False

    @patch('app.event_handlers.treatment_plan_operations.Session')
    def test_create_treatment_plan_object(self, mock_session_class, mock_page, sample_fields, sample_df_patients):
        """療養計画書オブジェクト作成テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, sample_df_patients, dialog_manager)

        patient_info = event_handlers.create_treatment_plan_object(
            1001, 101, '山田医師', '内科', 10, sample_df_patients
        )

        assert patient_info.patient_id == 1001
        assert patient_info.patient_name == '田中太郎'
        assert patient_info.doctor_name == '山田医師'
        assert patient_info.main_diagnosis == '糖尿病'

    @patch('app.event_handlers.treatment_plan_operations.Session')
    def test_create_treatment_plan_object_patient_not_found(
        self, mock_session_class, mock_page, sample_fields, sample_df_patients
    ):
        """患者が見つからない場合の療養計画書オブジェクト作成テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, sample_df_patients, dialog_manager)

        with pytest.raises(ValueError, match="患者ID 9999 が見つかりません"):
            event_handlers.create_treatment_plan_object(
                9999, 101, '山田医師', '内科', 10, sample_df_patients
            )


class TestRouteManager:
    """RouteManagerの統合テスト"""

    def test_init_route_manager(self, mock_page, sample_fields):
        """RouteManagerの初期化テスト"""
        ui_elements = {
            'buttons': Mock(),
            'create_buttons': Mock(),
            'edit_buttons': Mock(),
            'template_buttons': Mock(),
            'settings_button': Mock(),
            'manual_button': Mock(),
            'issue_date_button': Mock(),
            'issue_date_row': Mock(),
            'history_scrollable': Mock(),
            'guidance_items': Mock(),
            'guidance_items_template': Mock(),
            'issue_date_picker': Mock(),
        }
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, pd.DataFrame(), dialog_manager)

        route_manager = RouteManager(
            mock_page, sample_fields, ui_elements, event_handlers, "manual.pdf"
        )

        assert route_manager.page == mock_page
        assert route_manager.fields == sample_fields
        assert route_manager.ui_elements == ui_elements
        assert route_manager.manual_pdf_path == "manual.pdf"

    def test_open_create(self, mock_page, sample_fields):
        """新規作成画面を開くテスト"""
        ui_elements = {
            'buttons': Mock(),
            'create_buttons': Mock(),
            'edit_buttons': Mock(),
            'template_buttons': Mock(),
            'settings_button': Mock(),
            'manual_button': Mock(),
            'issue_date_button': Mock(),
            'issue_date_row': Mock(),
            'history_scrollable': Mock(),
            'guidance_items': Mock(),
            'guidance_items_template': Mock(),
            'issue_date_picker': Mock(),
        }
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, pd.DataFrame(), dialog_manager)
        route_manager = RouteManager(
            mock_page, sample_fields, ui_elements, event_handlers, "manual.pdf"
        )

        route_manager.open_create(None)

        mock_page.go.assert_called_with("/create")

    def test_open_edit(self, mock_page, sample_fields):
        """編集画面を開くテスト"""
        ui_elements = {
            'buttons': Mock(),
            'create_buttons': Mock(),
            'edit_buttons': Mock(),
            'template_buttons': Mock(),
            'settings_button': Mock(),
            'manual_button': Mock(),
            'issue_date_button': Mock(),
            'issue_date_row': Mock(),
            'history_scrollable': Mock(),
            'guidance_items': Mock(),
            'guidance_items_template': Mock(),
            'issue_date_picker': Mock(),
        }
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, pd.DataFrame(), dialog_manager)
        route_manager = RouteManager(
            mock_page, sample_fields, ui_elements, event_handlers, "manual.pdf"
        )

        route_manager.open_edit(None)

        mock_page.go.assert_called_with("/edit")

    def test_open_template(self, mock_page, sample_fields):
        """テンプレート画面を開くテスト"""
        ui_elements = {
            'buttons': Mock(),
            'create_buttons': Mock(),
            'edit_buttons': Mock(),
            'template_buttons': Mock(),
            'settings_button': Mock(),
            'manual_button': Mock(),
            'issue_date_button': Mock(),
            'issue_date_row': Mock(),
            'history_scrollable': Mock(),
            'guidance_items': Mock(),
            'guidance_items_template': Mock(),
            'issue_date_picker': Mock(),
        }
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, pd.DataFrame(), dialog_manager)
        route_manager = RouteManager(
            mock_page, sample_fields, ui_elements, event_handlers, "manual.pdf"
        )

        route_manager.open_template(None)

        mock_page.go.assert_called_with("/template")

    def test_open_route_resets_fields(self, mock_page, sample_fields):
        """ホーム画面を開くときにフィールドがリセットされるテスト"""
        ui_elements = {
            'buttons': Mock(),
            'create_buttons': Mock(),
            'edit_buttons': Mock(),
            'template_buttons': Mock(),
            'settings_button': Mock(),
            'manual_button': Mock(),
            'issue_date_button': Mock(),
            'issue_date_row': Mock(),
            'history_scrollable': Mock(),
            'guidance_items': Mock(),
            'guidance_items_template': Mock(),
            'issue_date_picker': Mock(),
        }
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, pd.DataFrame(), dialog_manager)
        event_handlers.update_history = Mock()

        route_manager = RouteManager(
            mock_page, sample_fields, ui_elements, event_handlers, "manual.pdf"
        )

        route_manager.open_route(None)

        # フィールドがクリアされていることを確認
        assert sample_fields['target_weight'].value == ''
        assert sample_fields['goal1'].value == ''
        assert sample_fields['main_diagnosis'].value == ''
        assert sample_fields['nonsmoker'].value is False
        mock_page.go.assert_called_with("/")

    def test_on_close(self, mock_page, sample_fields):
        """ウィンドウを閉じるテスト"""
        ui_elements = {
            'buttons': Mock(),
            'create_buttons': Mock(),
            'edit_buttons': Mock(),
            'template_buttons': Mock(),
            'settings_button': Mock(),
            'manual_button': Mock(),
            'issue_date_button': Mock(),
            'issue_date_row': Mock(),
            'history_scrollable': Mock(),
            'guidance_items': Mock(),
            'guidance_items_template': Mock(),
            'issue_date_picker': Mock(),
        }
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, pd.DataFrame(), dialog_manager)
        route_manager = RouteManager(
            mock_page, sample_fields, ui_elements, event_handlers, "manual.pdf"
        )

        route_manager.on_close(None)

        mock_page.window.close.assert_called_once()


class TestUIFlowIntegration:
    """UIフロー全体の統合テスト"""

    def test_dialog_and_event_handler_integration(self, mock_page, sample_fields, sample_df_patients):
        """DialogManagerとEventHandlersの連携テスト"""
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, sample_df_patients, dialog_manager)

        # DialogManagerを経由してエラーメッセージを表示
        dialog_manager.show_error_message("統合テストエラー")

        # メッセージが表示されたことを確認
        assert len(mock_page.overlay) > 0

    def test_route_and_event_handler_integration(self, mock_page, sample_fields):
        """RouteManagerとEventHandlersの連携テスト"""
        ui_elements = {
            'buttons': Mock(),
            'create_buttons': Mock(),
            'edit_buttons': Mock(),
            'template_buttons': Mock(),
            'settings_button': Mock(),
            'manual_button': Mock(),
            'issue_date_button': Mock(),
            'issue_date_row': Mock(),
            'history_scrollable': Mock(),
            'guidance_items': Mock(),
            'guidance_items_template': Mock(),
            'issue_date_picker': Mock(),
        }
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, pd.DataFrame(), dialog_manager)
        event_handlers.update_history = Mock()

        route_manager = RouteManager(
            mock_page, sample_fields, ui_elements, event_handlers, "manual.pdf"
        )

        # 新規作成画面を開く
        route_manager.open_create(None)
        mock_page.go.assert_called_with("/create")

        # ホームに戻る
        route_manager.open_route(None)
        mock_page.go.assert_called_with("/")

    def test_full_ui_flow_create_and_save(self, mock_page, sample_fields, sample_df_patients):
        """新規作成から保存までのフルフローテスト"""
        ui_elements = {
            'buttons': Mock(),
            'create_buttons': Mock(),
            'edit_buttons': Mock(),
            'template_buttons': Mock(),
            'settings_button': Mock(),
            'manual_button': Mock(),
            'issue_date_button': Mock(),
            'issue_date_row': Mock(),
            'history_scrollable': Mock(),
            'guidance_items': Mock(),
            'guidance_items_template': Mock(),
            'issue_date_picker': Mock(),
        }

        # 全コンポーネントの初期化
        dialog_manager = DialogManager(mock_page, sample_fields)
        event_handlers = EventHandlers(mock_page, sample_fields, sample_df_patients, dialog_manager)
        route_manager = RouteManager(
            mock_page, sample_fields, ui_elements, event_handlers, "manual.pdf"
        )

        # 患者情報読み込み
        event_handlers.load_patient_info(1001)
        assert sample_fields['name_value'].value == '田中太郎'

        # 新規作成画面へ遷移
        route_manager.open_create(None)
        mock_page.go.assert_called_with("/create")

        # 必須フィールドチェック
        result = dialog_manager.check_required_fields()
        assert result is True

        # ホームに戻る
        route_manager.open_route(None)
        mock_page.go.assert_called_with("/")
