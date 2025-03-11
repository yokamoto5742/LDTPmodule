import os
import csv
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime
import re
from io import BytesIO
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def check_file_exists(file_path: str) -> bool:
    """
    ファイルが存在するかどうかを確認する

    Args:
        file_path: 確認するファイルのパス

    Returns:
        bool: ファイルが存在する場合はTrue
    """
    return os.path.exists(file_path)


def load_csv_file(file_path: str, encoding: str = "shift_jis", header=None,
                  parse_dates=None, nrows: Optional[int] = None) -> Tuple[str, Optional[pd.DataFrame]]:
    """
    CSVファイルを読み込む

    Args:
        file_path: CSVファイルのパス
        encoding: ファイルのエンコーディング
        header: ヘッダーの設定
        parse_dates: 日付として解析する列のリスト
        nrows: 読み込む行数（指定がなければすべての行）

    Returns:
        Tuple[str, Optional[pd.DataFrame]]: エラーメッセージとデータフレーム
    """
    try:
        df = pd.read_csv(
            file_path,
            encoding=encoding,
            header=header,
            parse_dates=parse_dates,
            nrows=nrows
        )
        return "", df
    except Exception as e:
        return f"エラー: {str(e)}", None


def export_to_csv(data, file_path: str, headers: List[str], encoding: str = "shift_jis") -> Tuple[bool, str]:
    """
    データをCSVファイルにエクスポートする

    Args:
        data: エクスポートするデータ
        file_path: 出力先のファイルパス
        headers: CSVヘッダー行
        encoding: ファイルのエンコーディング

    Returns:
        Tuple[bool, str]: 成功したかどうかとメッセージ
    """
    try:
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', newline='', encoding=encoding, errors='ignore') as csvfile:
            writer = csv.writer(csvfile)

            # ヘッダー行を書き込む
            writer.writerow(headers)

            # データ行を書き込む
            for row in data:
                writer.writerow(row)

        return True, f"データがCSVファイル '{os.path.basename(file_path)}' にエクスポートされました"
    except Exception as e:
        return False, f"エクスポート中にエラーが発生しました: {str(e)}"


def import_from_csv(file_path: str, encoding: str = "shift_jis") -> Tuple[bool, str, List[Dict[str, Any]]]:
    """
    CSVファイルからデータをインポートする

    Args:
        file_path: インポートするCSVファイルのパス
        encoding: ファイルのエンコーディング

    Returns:
        Tuple[bool, str, List[Dict[str, Any]]]: 成功したかどうか、メッセージ、インポートしたデータ
    """
    try:
        # ファイル名のパターン確認
        file_name = os.path.basename(file_path)
        if not re.match(r'^patient_info_.*\.csv$', file_name):
            return False, "インポートエラー:このファイルはインポートできません", []

        data = []
        with open(file_path, 'r', encoding=encoding) as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                data.append(row)

        return True, "CSVファイルからデータがインポートされました", data
    except Exception as e:
        return False, f"インポート中にエラーが発生しました: {str(e)}", []


def create_timestamp_filename(prefix: str, extension: str = "csv") -> str:
    """
    タイムスタンプを含むファイル名を生成する

    Args:
        prefix: ファイル名の接頭辞
        extension: ファイルの拡張子（ドットなし）

    Returns:
        str: 生成されたファイル名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def ensure_directory_exists(directory_path: str) -> bool:
    """
    ディレクトリが存在することを確認し、存在しない場合は作成する

    Args:
        directory_path: 確認/作成するディレクトリのパス

    Returns:
        bool: 成功した場合はTrue
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception:
        return False


def create_file_monitor(file_path: str, on_deleted=None) -> Optional[Observer]:
    """
    ファイルの変更を監視するモニターを作成する

    Args:
        file_path: 監視するファイルのパス
        on_deleted: ファイルが削除された時に呼び出される関数

    Returns:
        Optional[Observer]: 監視オブジェクト、または失敗した場合はNone
    """
    try:
        class FileHandler(FileSystemEventHandler):
            def on_deleted(self, event):
                if event.src_path == file_path and on_deleted:
                    on_deleted()

        event_handler = FileHandler()
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(file_path), recursive=False)
        observer.start()
        return observer
    except Exception:
        return None


def open_file(file_path: str) -> bool:
    """
    OSのデフォルトアプリケーションでファイルを開く

    Args:
        file_path: 開くファイルのパス

    Returns:
        bool: 成功した場合はTrue
    """
    try:
        if os.path.exists(file_path):
            os.startfile(file_path)
            return True
        return False
    except Exception:
        return False


def read_binary_file(file_path: str) -> Optional[BytesIO]:
    """
    バイナリファイルを読み込む

    Args:
        file_path: 読み込むファイルのパス

    Returns:
        Optional[BytesIO]: ファイルの内容、または失敗した場合はNone
    """
    try:
        with open(file_path, 'rb') as f:
            return BytesIO(f.read())
    except Exception:
        return None


def write_binary_file(file_path: str, data: bytes) -> bool:
    """
    バイナリデータをファイルに書き込む

    Args:
        file_path: 書き込み先のファイルパス
        data: 書き込むバイナリデータ

    Returns:
        bool: 成功した場合はTrue
    """
    try:
        # 出力ディレクトリが存在しない場合は作成
        ensure_directory_exists(os.path.dirname(file_path))

        with open(file_path, 'wb') as f:
            f.write(data)
        return True
    except Exception:
        return False


def get_file_extension(file_path: str) -> str:
    """
    ファイルの拡張子を取得する

    Args:
        file_path: ファイルパス

    Returns:
        str: 拡張子（ドットなし）
    """
    return os.path.splitext(file_path)[1][1:]


def combine_path(directory: str, filename: str) -> str:
    """
    ディレクトリとファイル名を結合してパスを作成する

    Args:
        directory: ディレクトリパス
        filename: ファイル名

    Returns:
        str: 結合されたパス
    """
    return os.path.join(directory, filename)


def get_application_directory() -> str:
    """
    アプリケーションディレクトリを取得する
    特に実行ファイル（exe）の場合は専用ディレクトリを返す

    Returns:
        str: アプリケーションディレクトリ
    """
    import sys
    if getattr(sys, 'frozen', False):
        return r"C:\Shinseikai\LDTPapp"
    return os.getcwd()
