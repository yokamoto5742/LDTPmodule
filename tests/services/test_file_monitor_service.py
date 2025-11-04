import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from watchdog.events import FileSystemEvent
from watchdog.observers import Observer

from services.file_monitor_service import MyHandler, check_file_exists, start_file_monitoring


class TestMyHandler:
    """MyHandlerクラスのテスト"""

    @patch('services.file_monitor_service.csv_file_path', 'C:\\test\\pat.csv')
    def test_MyHandler_on_deleted_closes_window_when_target_file_deleted(self):
        """対象ファイル削除時にwindowがcloseされることを確認"""
        # Arrange
        page_mock = MagicMock()
        handler = MyHandler(page_mock)
        event = Mock(spec=FileSystemEvent)
        event.src_path = 'C:\\test\\pat.csv'

        # Act
        handler.on_deleted(event)

        # Assert
        page_mock.window.close.assert_called_once()

    @patch('services.file_monitor_service.csv_file_path', 'C:\\test\\pat.csv')
    def test_MyHandler_on_deleted_does_not_close_when_other_file_deleted(self):
        """他のファイル削除時はwindowがcloseされないことを確認"""
        # Arrange
        page_mock = MagicMock()
        handler = MyHandler(page_mock)
        event = Mock(spec=FileSystemEvent)
        event.src_path = 'C:\\test\\other.csv'

        # Act
        handler.on_deleted(event)

        # Assert
        page_mock.window.close.assert_not_called()

    def test_MyHandler_stores_page_reference(self):
        """pageオブジェクトが正しく保持されることを確認"""
        # Arrange
        page_mock = MagicMock()

        # Act
        handler = MyHandler(page_mock)

        # Assert
        assert handler.page is page_mock


class TestStartFileMonitoring:
    """start_file_monitoring関数のテスト"""

    @patch('services.file_monitor_service.Observer')
    @patch('services.file_monitor_service.csv_file_path', 'C:\\test\\pat.csv')
    @patch('services.file_monitor_service.os.path.dirname')
    def test_start_file_monitoring_returns_observer(self, mock_dirname, mock_observer_class):
        """Observerオブジェクトが返されることを確認"""
        # Arrange
        page_mock = MagicMock()
        mock_dirname.return_value = 'C:\\test'
        observer_instance = MagicMock(spec=Observer)
        mock_observer_class.return_value = observer_instance

        # Act
        result = start_file_monitoring(page_mock)

        # Assert
        assert result is observer_instance
        observer_instance.start.assert_called_once()

    @patch('services.file_monitor_service.Observer')
    @patch('services.file_monitor_service.csv_file_path', 'C:\\test\\subdir\\pat.csv')
    @patch('services.file_monitor_service.os.path.dirname')
    def test_start_file_monitoring_schedules_correct_path(self, mock_dirname, mock_observer_class):
        """正しいパスで監視がスケジュールされることを確認"""
        # Arrange
        page_mock = MagicMock()
        mock_dirname.return_value = 'C:\\test\\subdir'
        observer_instance = MagicMock(spec=Observer)
        mock_observer_class.return_value = observer_instance

        # Act
        start_file_monitoring(page_mock)

        # Assert
        mock_dirname.assert_called_once_with('C:\\test\\subdir\\pat.csv')
        assert observer_instance.schedule.called
        call_args = observer_instance.schedule.call_args
        assert call_args.kwargs['path'] == 'C:\\test\\subdir'
        assert call_args.kwargs['recursive'] is False

    @patch('services.file_monitor_service.Observer')
    @patch('services.file_monitor_service.csv_file_path', 'C:\\test\\pat.csv')
    @patch('services.file_monitor_service.os.path.dirname')
    def test_start_file_monitoring_creates_handler_with_page(self, mock_dirname, mock_observer_class):
        """MyHandlerがpageを渡されて作成されることを確認"""
        # Arrange
        page_mock = MagicMock()
        mock_dirname.return_value = 'C:\\test'
        observer_instance = MagicMock(spec=Observer)
        mock_observer_class.return_value = observer_instance

        # Act
        start_file_monitoring(page_mock)

        # Assert
        assert observer_instance.schedule.called
        handler_arg = observer_instance.schedule.call_args[0][0]
        assert isinstance(handler_arg, MyHandler)
        assert handler_arg.page is page_mock


class TestCheckFileExists:
    """check_file_exists関数のテスト"""

    @patch('services.file_monitor_service.csv_file_path', 'C:\\test\\pat.csv')
    @patch('services.file_monitor_service.os.path.exists')
    def test_check_file_exists_closes_window_when_file_missing(self, mock_exists):
        """ファイルが存在しない場合にwindowがcloseされることを確認"""
        # Arrange
        page_mock = MagicMock()
        mock_exists.return_value = False

        # Act
        check_file_exists(page_mock)

        # Assert
        mock_exists.assert_called_once_with('C:\\test\\pat.csv')
        page_mock.window.close.assert_called_once()

    @patch('services.file_monitor_service.csv_file_path', 'C:\\test\\pat.csv')
    @patch('services.file_monitor_service.os.path.exists')
    def test_check_file_exists_does_nothing_when_file_exists(self, mock_exists):
        """ファイルが存在する場合は何もしないことを確認"""
        # Arrange
        page_mock = MagicMock()
        mock_exists.return_value = True

        # Act
        check_file_exists(page_mock)

        # Assert
        mock_exists.assert_called_once_with('C:\\test\\pat.csv')
        page_mock.window.close.assert_not_called()

    @patch('services.file_monitor_service.csv_file_path', 'C:\\different\\path\\data.csv')
    @patch('services.file_monitor_service.os.path.exists')
    def test_check_file_exists_uses_correct_path(self, mock_exists):
        """設定された正しいパスが使用されることを確認"""
        # Arrange
        page_mock = MagicMock()
        mock_exists.return_value = True

        # Act
        check_file_exists(page_mock)

        # Assert
        mock_exists.assert_called_once_with('C:\\different\\path\\data.csv')
