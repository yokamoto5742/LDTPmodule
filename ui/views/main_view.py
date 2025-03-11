import os
import re
from datetime import datetime
import csv
import flet as ft
from io import BytesIO

from models.patient import PatientInfo
from models.template import MainDisease, SheetName, Template
from database.connection import get_session, Session
from services.treatment_plan import TreatmentPlanGenerator
from services.csv_service import load_patient_data
from ui.components.form_fields import DropdownItems, create_blue_outlined_dropdown, create_form_fields


def create_theme_aware_button_style(page: ft.Page):
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


def create_ui(page, initial_patient_id, df_patients, VERSION, LAST_UPDATED):
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    # UI設定の読み込み
    input_height = config.getint('UI', 'input_height', fallback=50)
    text_height = config.getint('UI', 'text_height', fallback=40)
    table_width = config.getint('DataTable', 'width')
    export_folder = config.get('FilePaths', 'export_folder')
    manual_pdf_path = config.get('FilePaths', 'manual_pdf')
    csv_file_path = config.get('FilePaths', 'patient_data')

    # ウィンドウ設定
    page.title = "生活習慣病療養計画書"
    page.window.width = config.getint('settings', 'window_width', fallback=1200)
    page.window.height = config.getint('settings', 'window_height', fallback=800)
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[
            ft.Locale("ja", "JP"),
            ft.Locale("en", "US")
        ],
        current_locale=ft.Locale("ja", "JP")
    )

    # テーマの設定
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)

    dropdown_items = DropdownItems()

    # 治療計画書の履歴の選択を空欄にする(初期値)
    selected_row = None

    def on_startup(e):
        error_message_start, df_patients_data = load_patient_data()
        if error_message_start:
            snack_bar = ft.SnackBar(
                content=ft.Text(error_message_start),
                duration=1000
            )
            snack_bar.open = True
            page.overlay.append(snack_bar)
            page.update()

    def open_settings_dialog(e):
        def close_dialog(e):
            dialog.open = False
            page.update()

        def csv_export(e):
            export_to_csv(e)
            close_dialog(e)

        content = ft.Container(
            content=ft.Column([
                ft.Text(f"LDTPapp\nバージョン: {VERSION}\n最終更新日: {LAST_UPDATED}"),
                ft.ElevatedButton("CSV出力", on_click=csv_export),
                ft.ElevatedButton("CSV取込", on_click=lambda _: file_picker.pick_files(allow_multiple=False)),
            ]),
            height=page.window.height * 0.3,
        )

        dialog = ft.AlertDialog(
            title=ft.Text("設定"),
            content=content,
            actions=[
                ft.TextButton("閉じる", on_click=close_dialog)
            ]
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            import_csv(file_path)

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    def import_csv(file_path):
        file_name = os.path.basename(file_path)
        if not re.match(r'^patient_info_.*\.csv$', file_name):
            error_snack_bar = ft.SnackBar(
                content=ft.Text("インポートエラー:このファイルはインポートできません"),
                duration=1000
            )
            error_snack_bar.open = True
            page.overlay.append(error_snack_bar)
            page.update()
            return

        try:
            with open(file_path, 'r', encoding='shift_jis') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                session = Session()
                for row in csv_reader:
                    patient_info = PatientInfo(
                        patient_id=int(row['patient_id']),
                        patient_name=row['patient_name'],
                        kana=row['kana'],
                        gender=row['gender'],
                        birthdate=datetime.strptime(row['birthdate'], '%Y-%m-%d').date(),
                        issue_date=datetime.strptime(row['issue_date'], '%Y-%m-%d').date(),
                        issue_date_age=int(row['issue_date_age']),
                        doctor_id=int(row['doctor_id']),
                        doctor_name=row['doctor_name'],
                        department=row['department'],
                        department_id=int(row['department_id']),
                        main_diagnosis=row['main_diagnosis'],
                        sheet_name=row['sheet_name'],
                        creation_count=int(row['creation_count']),
                        target_weight=float(row['target_weight']) if row['target_weight'] else None,
                        target_bp=row['target_bp'],
                        target_hba1c=row['target_hba1c'],
                        goal1=row['goal1'],
                        goal2=row['goal2'],
                        target_achievement=row['target_achievement'],
                        diet1=row['diet1'],
                        diet2=row['diet2'],
                        diet3=row['diet3'],
                        diet4=row['diet4'],
                        diet_comment=row['diet_comment'],
                        exercise_prescription=row['exercise_prescription'],
                        exercise_time=row['exercise_time'],
                        exercise_frequency=row['exercise_frequency'],
                        exercise_intensity=row['exercise_intensity'],
                        daily_activity=row['daily_activity'],
                        exercise_comment=row['exercise_comment'],
                        nonsmoker=row['nonsmoker'] == 'True',
                        smoking_cessation=row['smoking_cessation'] == 'True',
                        other1=row['other1'],
                        other2=row['other2'],
                        ophthalmology=row['ophthalmology'] == 'True',
                        dental=row['dental'] == 'True',
                        cancer_screening=row['cancer_screening'] == 'True'
                    )
                    session.add(patient_info)
                session.commit()
                session.close()

            snack_bar = ft.SnackBar(
                content=ft.Text("CSVファイルからデータがインポートされました"),
                duration=1000
            )
            snack_bar.open = True
            page.overlay.append(snack_bar)
            update_history(int(patient_id.value))
            page.update()

        except Exception as e:
            error_snack_bar = ft.SnackBar(
                content=ft.Text(f"インポート中にエラーが発生しました: {str(e)}"),
                duration=3000
            )
            error_snack_bar.open = True
            page.overlay.append(error_snack_bar)
            page.update()

    def export_to_csv(e):
        try:
            # CSVファイル名を現在の日時で生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"patient_info_export_{timestamp}.csv"
            csv_path = os.path.join(export_folder, csv_filename)

            # エクスポートフォルダが存在しない場合は作成
            os.makedirs(export_folder, exist_ok=True)

            # セッションを開始
            session = Session()

            # PatientInfoテーブルからすべてのデータを取得
            patient_data = session.query(PatientInfo).all()

            # CSVファイルを書き込みモードで開く
            with open(csv_path, 'w', newline='', encoding='shift_jis', errors='ignore') as csvfile:
                writer = csv.writer(csvfile)

                # ヘッダー行を書き込む
                writer.writerow([column.name for column in PatientInfo.__table__.columns])

                # データ行を書き込む
                for patient in patient_data:
                    writer.writerow([getattr(patient, column.name) for column in PatientInfo.__table__.columns])

            session.close()

            snack_bar = ft.SnackBar(
                content=ft.Text(f"データがCSVファイル '{csv_filename}' にエクスポートされました"),
                duration=1000
            )
            snack_bar.open = True
            page.overlay.append(snack_bar)
            page.update()

            os.startfile(export_folder)

        except Exception as e:
            # エラーメッセージを表示
            error_snack_bar = ft.SnackBar(
                content=ft.Text(f"エクスポート中にエラーが発生しました: {str(e)}"),
                duration=1000
            )
            error_snack_bar.open = True
            page.overlay.append(error_snack_bar)
            page.update()

    def on_issue_date_change(e):
        if issue_date_picker.value:
            issue_date_value.value = issue_date_picker.value.strftime("%Y/%m/%d")
            page.update()

    def on_date_picker_dismiss(e):
        if issue_date_picker.value:
            issue_date_value.value = issue_date_picker.value.strftime("%Y/%m/%d")
        page.overlay.remove(issue_date_picker)
        page.update()

    issue_date_picker = ft.DatePicker(
        on_change=on_issue_date_change,
        on_dismiss=on_date_picker_dismiss
    )

    def open_date_picker(e):
        if issue_date_picker not in page.overlay:
            page.overlay.append(issue_date_picker)
        issue_date_picker.open = True
        page.update()

    def load_main_diseases():
        with get_session() as session:
            main_diseases = session.query(MainDisease).all()
            return [ft.dropdown.Option(str(disease.name)) for disease in main_diseases]

    def load_sheet_names(main_disease=None):
        with get_session() as session:
            if main_disease:
                sheet_names = session.query(SheetName).filter(SheetName.main_disease_id == main_disease).all()
            else:
                sheet_names = session.query(SheetName).all()
            return [ft.dropdown.Option(str(sheet.name)) for sheet in sheet_names]

    def on_main_diagnosis_change(e):
        selected_main_disease = main_diagnosis.value
        apply_template()

        with Session() as session:
            if selected_main_disease:
                main_disease = session.query(MainDisease).filter_by(
                    name=selected_main_disease).first()
                sheet_name_options = load_sheet_names(main_disease.id) if main_disease else []
            else:
                sheet_name_options = load_sheet_names(None)

        sheet_name_dropdown.options = sheet_name_options
        sheet_name_dropdown.value = ""
        page.update()

    def on_sheet_name_change(e):
        apply_template()
        page.update()

    def format_date(date_str):
        if pd.isna(date_str):  # pd.isna()で欠損値かどうかを判定
            return ""
        return pd.to_datetime(date_str).strftime("%Y/%m/%d")

    def load_patient_info(patient_id_arg):
        patient_info = df_patients[df_patients.iloc[:, 2] == patient_id_arg]
        if not patient_info.empty:
            patient_info = patient_info.iloc[0]
            patient_id.value = str(patient_id_arg)
            issue_date_value.value = datetime.now().date().strftime("%Y/%m/%d")
            name_value.value = patient_info.iloc[3]
            kana_value.value = patient_info.iloc[4]
            gender_value.value = "男性" if patient_info.iloc[5] == 1 else "女性"
            birthdate = patient_info.iloc[6]
            birthdate_value.value = format_date(birthdate)
            doctor_id_value.value = str(patient_info.iloc[9])
            doctor_name_value.value = patient_info.iloc[10]
            department_value.value = patient_info.iloc[14]
            department_id_value.value = str(patient_info.iloc[13])
        else:
            # patient_infoが空の場合は空文字列を設定
            issue_date_value.value = ""
            name_value.value = ""
            kana_value.value = ""
            gender_value.value = ""
            birthdate_value.value = ""
            doctor_id_value.value = ""
            doctor_name_value.value = ""
            department_value.value = ""
        page.update()

    def calculate_issue_date_age(birth_date, issue_date):
        issue_date_age = issue_date.year - birth_date.year
        if issue_date.month < birth_date.month or (
                issue_date.month == birth_date.month and issue_date.day < birth_date.day):
            issue_date_age -= 1
        return issue_date_age

    def create_treatment_plan_object(p_id, doctor_id, doctor_name, department, department_id, patients_df):
        patient_info_csv = patients_df.loc[patients_df.iloc[:, 2] == p_id]
        if patient_info_csv.empty:
            raise ValueError(f"患者ID {p_id} が見つかりません。")
        patient_info = patient_info_csv.iloc[0]
        birthdate = patient_info.iloc[6]
        issue_date = datetime.strptime(issue_date_value.value, "%Y/%m/%d").date()
        issue_date_age = calculate_issue_date_age(birthdate, issue_date)
        return PatientInfo(
            patient_id=p_id,
            patient_name=patient_info.iloc[3],
            kana=patient_info.iloc[4],
            gender="男性" if patient_info.iloc[5] == 1 else "女性",
            birthdate=birthdate,
            issue_date=issue_date,
            issue_date_age=issue_date_age,
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            department=department,
            department_id=department_id,
            main_diagnosis=main_diagnosis.value,
            sheet_name=sheet_name_dropdown.value,
            creation_count=int(creation_count.value),
            target_weight=float(target_weight.value) if target_weight.value else None,
            target_bp=target_bp.value,
            target_hba1c=target_hba1c.value,
            goal1=goal1.value,
            goal2=goal2.value,
            target_achievement=target_achievement.value,
            diet1=diet1.value,
            diet2=diet2.value,
            diet3=diet3.value,
            diet4=diet4.value,
            diet_comment=diet_comment.value,
            exercise_prescription=exercise_prescription.value,
            exercise_time=exercise_time.value,
            exercise_frequency=exercise_frequency.value,
            exercise_intensity=exercise_intensity.value,
            daily_activity=daily_activity.value,
            exercise_comment=exercise_comment.value,
            nonsmoker=nonsmoker.value,
            smoking_cessation=smoking_cessation.value,
            other1=other1.value,
            other2=other2.value,
            ophthalmology=ophthalmology.value,
            dental=dental.value,
            cancer_screening=cancer_screening.value
        )

    def create_treatment_plan(p_id, doctor_id, doctor_name, department, department_id, patients_df):
        session = Session()
        try:
            treatment_plan = create_treatment_plan_object(p_id, doctor_id, doctor_name, department, department_id,
                                                          patients_df)
            session.add(treatment_plan)
            session.commit()
            TreatmentPlanGenerator.generate_plan(treatment_plan, "LDTPform")
            open_route(None)
        finally:
            session.close()

    def save_treatment_plan(p_id, doctor_id, doctor_name, department, department_id, patients_df):
        session = Session()
        try:
            treatment_plan = create_treatment_plan_object(p_id, doctor_id, doctor_name, department, department_id,
                                                          patients_df)
            session.add(treatment_plan)
            session.commit()
            open_route(None)
        finally:
            session.close()

    def show_error_message(message):
        snack_bar = ft.SnackBar(content=ft.Text(message), duration=1000)
        snack_bar.open = True
        page.overlay.append(snack_bar)
        page.update()

    def check_required_fields():
        if not main_diagnosis.value:
            show_error_message("主病名を選択してください")
            return False
        if not sheet_name_dropdown.value:
            show_error_message("シート名を選択してください")
            return False
        return True

    def create_new_plan(e):
        if not check_required_fields():
            return
        p_id = patient_id.value
        doctor_id = doctor_id_value.value
        doctor_name = doctor_name_value.value
        department_id = department_id_value.value
        department = department_value.value
        create_treatment_plan(int(p_id), int(doctor_id), doctor_name, department, int(department_id), df_patients)

    def save_new_plan(e):
        if not check_required_fields():
            return
        p_id = patient_id.value
        doctor_id = doctor_id_value.value
        doctor_name = doctor_name_value.value
        department_id = department_id_value.value
        department = department_value.value
        save_treatment_plan(int(p_id), int(doctor_id), doctor_name, department, int(department_id), df_patients)

    def print_plan(e):
        nonlocal selected_row
        session = Session()
        if selected_row is not None:
            patient_info = session.query(PatientInfo).filter(PatientInfo.id == selected_row['id']).first()
            if patient_info:
                patient_info.main_diagnosis = main_diagnosis.value
                patient_info.sheet_name = sheet_name_dropdown.value
                patient_info.creation_count = int(creation_count.value)
                patient_info.issue_date = datetime.strptime(issue_date_value.value, "%Y/%m/%d").date()
                patient_info.issue_date_age = calculate_issue_date_age(patient_info.birthdate, patient_info.issue_date)
                patient_info.target_weight = float(target_weight.value) if target_weight.value else None
                patient_info.target_bp = target_bp.value
                patient_info.target_hba1c = target_hba1c.value
                patient_info.goal1 = goal1.value
                patient_info.goal2 = goal2.value
                patient_info.target_achievement = target_achievement.value
                patient_info.diet1 = diet1.value
                patient_info.diet2 = diet2.value
                patient_info.diet3 = diet3.value
                patient_info.diet4 = diet4.value
                patient_info.diet_comment = diet_comment.value
                patient_info.exercise_prescription = exercise_prescription.value
                patient_info.exercise_time = exercise_time.value
                patient_info.exercise_frequency = exercise_frequency.value
                patient_info.exercise_intensity = exercise_intensity.value
                patient_info.daily_activity = daily_activity.value
                patient_info.exercise_comment = exercise_comment.value
                patient_info.nonsmoker = nonsmoker.value
                patient_info.smoking_cessation = smoking_cessation.value
                patient_info.other1 = other1.value
                patient_info.other2 = other2.value
                patient_info.ophthalmology = ophthalmology.value
                patient_info.dental = dental.value
                patient_info.cancer_screening = cancer_screening.value
                session.commit()

                # 更新後のデータを使用して印刷
                TreatmentPlanGenerator.generate_plan(patient_info, "LDTPform")
        session.close()

    def on_patient_id_change(e):
        p_id = patient_id.value.strip()
        if patient_id:
            load_patient_info(int(p_id))
        update_history(p_id)

    def save_data(e):
        nonlocal selected_row
        session = Session()

        if selected_row is not None and 'id' in selected_row:
            patient_info = session.query(PatientInfo).filter(PatientInfo.id == selected_row['id']).first()
            if patient_info:
                if not check_required_fields():
                    return
                patient_info.patient_id = int(patient_id.value)
                patient_info.patient_name = name_value.value
                patient_info.kana = kana_value.value
                patient_info.gender = gender_value.value
                patient_info.birthdate = datetime.strptime(birthdate_value.value, "%Y/%m/%d").date()
                patient_info.issue_date = datetime.strptime(issue_date_value.value, "%Y/%m/%d").date()
                patient_info.issue_date_age = calculate_issue_date_age(patient_info.birthdate, patient_info.issue_date)
                patient_info.doctor_id = int(doctor_id_value.value)
                patient_info.doctor_name = doctor_name_value.value
                patient_info.department = department_value.value
                patient_info.department_id = int(department_id_value.value)
                patient_info.main_diagnosis = main_diagnosis.value
                patient_info.sheet_name = sheet_name_dropdown.value
                patient_info.creation_count = int(creation_count.value)
                patient_info.target_weight = float(target_weight.value) if target_weight.value else None
                patient_info.target_bp = target_bp.value
                patient_info.target_hba1c = target_hba1c.value
                patient_info.goal1 = goal1.value
                patient_info.goal2 = goal2.value
                patient_info.target_achievement = target_achievement.value
                patient_info.diet1 = diet1.value
                patient_info.diet2 = diet2.value
                patient_info.diet3 = diet3.value
                patient_info.diet4 = diet4.value
                patient_info.diet_comment = diet_comment.value
                patient_info.exercise_prescription = exercise_prescription.value
                patient_info.exercise_time = exercise_time.value
                patient_info.exercise_frequency = exercise_frequency.value
                patient_info.exercise_intensity = exercise_intensity.value
                patient_info.daily_activity = daily_activity.value
                patient_info.exercise_comment = exercise_comment.value
                patient_info.nonsmoker = nonsmoker.value
                patient_info.smoking_cessation = smoking_cessation.value
                patient_info.other1 = other1.value
                patient_info.other2 = other2.value
                patient_info.ophthalmology = ophthalmology.value
                patient_info.dental = dental.value
                patient_info.cancer_screening = cancer_screening.value
                session.commit()

                snack_bar = ft.SnackBar(ft.Text("データが保存されました"), duration=1000)
                snack_bar.open = True
                page.overlay.append(snack_bar)

        session.close()
        page.update()

    def copy_data(e):
        nonlocal selected_row
        session = Session()
        patient_info = session.query(PatientInfo). \
            filter(PatientInfo.patient_id == patient_id.value). \
            order_by(PatientInfo.id.desc()).first()

        if patient_info:
            # pat.csvから最新の情報を取得
            error_message, df_patients = load_patient_data()
            if error_message:
                session.close()
                return

            patient_csv_info = df_patients[df_patients.iloc[:, 2] == int(patient_id.value)]
            if patient_csv_info.empty:
                session.close()
                return

            patient_csv_info = patient_csv_info.iloc[0]

            patient_info_copy = PatientInfo(
                patient_id=patient_info.patient_id,
                patient_name=patient_info.patient_name,
                kana=patient_info.kana,
                gender=patient_info.gender,
                birthdate=patient_info.birthdate,
                issue_date=datetime.now().date(),
                issue_date_age=patient_info.issue_date_age,
                doctor_id=int(patient_csv_info.iloc[9]),
                doctor_name=patient_csv_info.iloc[10],
                department_id=int(patient_csv_info.iloc[13]),
                department=patient_csv_info.iloc[14],
                main_diagnosis=patient_info.main_diagnosis,
                sheet_name=patient_info.sheet_name,
                creation_count=patient_info.creation_count + 1,
                target_weight=patient_info.target_weight,
                target_bp=patient_info.target_bp,
                target_hba1c=patient_info.target_hba1c,
                goal1=patient_info.goal1,
                goal2=patient_info.goal2,
                target_achievement=patient_info.target_achievement,
                diet1=patient_info.diet1,
                diet2=patient_info.diet2,
                diet3=patient_info.diet3,
                diet4=patient_info.diet4,
                diet_comment=patient_info.diet_comment,
                exercise_prescription=patient_info.exercise_prescription,
                exercise_time=patient_info.exercise_time,
                exercise_frequency=patient_info.exercise_frequency,
                exercise_intensity=patient_info.exercise_intensity,
                daily_activity=patient_info.daily_activity,
                exercise_comment=patient_info.exercise_comment,
                nonsmoker=patient_info.nonsmoker,
                smoking_cessation=patient_info.smoking_cessation,
                other1=patient_info.other1,
                other2=patient_info.other2,
                ophthalmology=patient_info.ophthalmology,
                dental=patient_info.dental,
                cancer_screening=patient_info.cancer_screening
            )
            session.add(patient_info_copy)
            session.commit()

            # 新しく作成されたデータのIDを取得
            new_id = patient_info_copy.id

            snack_bar = ft.SnackBar(
                ft.Text("前回の計画内容をコピーしました"),
                duration=1000,
            )
            snack_bar.open = True
            page.overlay.append(snack_bar)

            # 新しく作成されたデータを選択状態にする
            select_copied_data(new_id)

        session.close()
        update_history(int(patient_id.value))
        page.update()

    def select_copied_data(new_id):
        nonlocal selected_row
        session = Session()
        patient_info = session.query(PatientInfo).filter(PatientInfo.id == new_id).first()
        if patient_info:
            selected_row = {
                'id': patient_info.id,
                'issue_date': patient_info.issue_date.strftime("%Y/%m/%d") if patient_info.issue_date else "",
                'department': patient_info.department,
                'doctor_name': patient_info.doctor_name,
                'main_diagnosis': patient_info.main_diagnosis,
                'sheet_name': patient_info.sheet_name,
                'count': patient_info.creation_count
            }
            update_form_with_selected_data(patient_info)
        session.close()

    def update_form_with_selected_data(patient_info):
        patient_id.value = str(patient_info.patient_id)
        issue_date_value.value = patient_info.issue_date.strftime("%Y/%m/%d") if patient_info.issue_date else ""
        name_value.value = patient_info.patient_name
        kana_value.value = patient_info.kana
        gender_value.value = patient_info.gender
        birthdate_value.value = patient_info.birthdate.strftime("%Y/%m/%d") if patient_info.birthdate else ""
        doctor_id_value.value = str(patient_info.doctor_id)
        doctor_name_value.value = patient_info.doctor_name
        department_value.value = patient_info.department
        department_id_value.value = str(patient_info.department_id)
        main_diagnosis.value = patient_info.main_diagnosis
        sheet_name_dropdown.value = patient_info.sheet_name
        creation_count.value = str(patient_info.creation_count)
        target_weight.value = str(patient_info.target_weight) if patient_info.target_weight else ""
        target_bp.value = patient_info.target_bp
        target_hba1c.value = patient_info.target_hba1c
        goal1.value = patient_info.goal1
        goal2.value = patient_info.goal2
        target_achievement.value = patient_info.target_achievement
        diet1.value = patient_info.diet1
        diet2.value = patient_info.diet2
        diet3.value = patient_info.diet3
        diet4.value = patient_info.diet4
        diet_comment.value = patient_info.diet_comment
        exercise_prescription.value = patient_info.exercise_prescription
        exercise_time.value = patient_info.exercise_time
        exercise_frequency.value = patient_info.exercise_frequency
        exercise_intensity.value = patient_info.exercise_intensity
        daily_activity.value = patient_info.daily_activity
        exercise_comment.value = patient_info.exercise_comment
        nonsmoker.value = patient_info.nonsmoker
        smoking_cessation.value = patient_info.smoking_cessation
        other1.value = patient_info.other1
        other2.value = patient_info.other2
        ophthalmology.value = patient_info.ophthalmology
        dental.value = patient_info.dental
        cancer_screening.value = patient_info.cancer_screening
        page.update()

    def delete_data(e):
        nonlocal selected_row
        if selected_row is None:
            snack_bar = ft.SnackBar(
                ft.Text("削除するレコードを選択してください"),
                duration=1000,
            )
            snack_bar.open = True
            page.overlay.append(snack_bar)
            return

        session = Session()
        try:
            patient_info = session.query(PatientInfo).filter(PatientInfo.id == selected_row['id']).first()
            if patient_info:
                session.delete(patient_info)
                session.commit()
                snack_bar = ft.SnackBar(
                    ft.Text("データを削除しました"),
                    duration=1000,
                )
                snack_bar.open = True
                page.overlay.append(snack_bar)
                selected_row = None
            else:
                snack_bar = ft.SnackBar(
                    ft.Text("削除するデータが見つかりませんでした"),
                    duration=1000,
                )
                snack_bar.open = True
                page.overlay.append(snack_bar)
        finally:
            session.close()

        update_history(patient_id.value)
        open_route(e)

    def filter_data(e):
        update_history(patient_id.value)

    def update_history(filter_patient_id=None):
        data = fetch_data(filter_patient_id)
        history.rows = create_data_rows(data)
        page.update()

    def on_row_selected(e):
        nonlocal selected_row
        if e.data == "true":
            row_index = history.rows.index(e.control)
            selected_row = history.rows[row_index].data
            session = Session()
            patient_info = session.query(PatientInfo).filter(PatientInfo.id == selected_row['id']).first()
            if patient_info:
                patient_id.value = patient_info.patient_id

                # 発行日の更新
                issue_date_value.value = patient_info.issue_date.strftime("%Y/%m/%d") if patient_info.issue_date else ""

                # 主病名の更新
                main_diagnosis.options = load_main_diseases()
                main_diagnosis.value = patient_info.main_diagnosis

                # シート名の更新
                main_disease = session.query(MainDisease).filter_by(name=patient_info.main_diagnosis).first()
                if main_disease:
                    sheet_name_dropdown.options = load_sheet_names(main_disease.id)
                else:
                    sheet_name_dropdown.options = load_sheet_names(None)
                sheet_name_dropdown.value = patient_info.sheet_name

                creation_count.value = patient_info.creation_count
                target_weight.value = patient_info.target_weight
                target_bp.value = patient_info.target_bp
                target_hba1c.value = patient_info.target_hba1c
                goal1.value = patient_info.goal1
                goal2.value = patient_info.goal2
                target_achievement.value = patient_info.target_achievement
                diet1.value = patient_info.diet1
                diet2.value = patient_info.diet2
                diet3.value = patient_info.diet3
                diet4.value = patient_info.diet4
                diet_comment.value = patient_info.diet_comment
                exercise_prescription.value = patient_info.exercise_prescription
                exercise_time.value = patient_info.exercise_time
                exercise_frequency.value = patient_info.exercise_frequency
                exercise_intensity.value = patient_info.exercise_intensity
                daily_activity.value = patient_info.daily_activity
                exercise_comment.value = patient_info.exercise_comment
                nonsmoker.value = patient_info.nonsmoker
                smoking_cessation.value = patient_info.smoking_cessation
                other1.value = patient_info.other1
                other2.value = patient_info.other2
                ophthalmology.value = patient_info.ophthalmology
                dental.value = patient_info.dental
                cancer_screening.value = patient_info.cancer_screening
            session.close()
            page.update()

        if e.data == "true":
            row_index = history.rows.index(e.control)
            selected_row = history.rows[row_index].data
            open_edit(e)

    def fetch_data(filter_patient_id=None):
        if not filter_patient_id:
            return []

        session_fetch_data = Session()
        query = session_fetch_data.query(PatientInfo.id, PatientInfo.issue_date, PatientInfo.department,
                                         PatientInfo.doctor_name, PatientInfo.main_diagnosis,
                                         PatientInfo.sheet_name, PatientInfo.creation_count). \
            order_by(PatientInfo.patient_id.asc(), PatientInfo.id.desc())

        query = query.filter(PatientInfo.patient_id == filter_patient_id)

        return ({
            "id": str(info.id),
            "issue_date": info.issue_date.strftime("%Y/%m/%d") if info.issue_date else "",
            "department": info.department,
            "doctor_name": info.doctor_name,
            "main_diagnosis": info.main_diagnosis,
            "sheet_name": info.sheet_name,
            "count": info.creation_count
        } for info in query)

    def create_data_rows(data):
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

    def apply_template(e=None):
        session_apply_template = Session()
        try:
            template = session_apply_template.query(Template).filter(
                Template.main_disease == main_diagnosis.value,
                Template.sheet_name == sheet_name_dropdown.value
            ).first()
            if template:
                goal1.value = template.goal1
                goal2.value = template.goal2
                target_bp.value = template.target_bp
                target_hba1c.value = template.target_hba1c
                diet1.value = template.diet1
                diet2.value = template.diet2
                diet3.value = template.diet3
                diet4.value = template.diet4
                exercise_prescription.value = template.exercise_prescription
                exercise_time.value = template.exercise_time
                exercise_frequency.value = template.exercise_frequency
                exercise_intensity.value = template.exercise_intensity
                daily_activity.value = template.daily_activity
                other1.value = template.other1
                other2.value = template.other2
        finally:
            session_apply_template.close()
        page.update()

    def save_template(e):
        if not main_diagnosis.value:
            snack_bar = ft.SnackBar(content=ft.Text("主病名を選択してください"))
            snack_bar.open = True
            page.overlay.append(snack_bar)
            page.update()
            return
        if not sheet_name_dropdown.value:
            snack_bar = ft.SnackBar(content=ft.Text("シート名を選択してください"))
            snack_bar.open = True
            page.overlay.append(snack_bar)
            page.update()
            return

        session = Session()
        template = session.query(Template).filter(Template.main_disease == main_diagnosis.value,
                                                  Template.sheet_name == sheet_name_dropdown.value).first()
        if template:
            template.goal1 = goal1.value
            template.goal2 = goal2.value
            template.target_bp = target_bp.value
            template.target_hba1c = target_hba1c.value
            template.target_achievement = target_achievement.value
            template.diet1 = diet1.value
            template.diet2 = diet2.value
            template.diet3 = diet3.value
            template.diet4 = diet4.value
            template.exercise_prescription = exercise_prescription.value
            template.exercise_time = exercise_time.value
            template.exercise_frequency = exercise_frequency.value
            template.exercise_intensity = exercise_intensity.value
            template.daily_activity = daily_activity.value
            template.other1 = other1.value
            template.other2 = other2.value
        else:
            template = Template(
                main_disease=main_diagnosis.value,
                sheet_name=sheet_name_dropdown.value,
                goal1=goal1.value,
                goal2=goal2.value,
                target_bp=target_bp.value,
                target_hba1c=target_hba1c.value,
                diet1=diet1.value,
                diet2=diet2.value,
                diet3=diet3.value,
                diet4=diet4.value,
                exercise_prescription=exercise_prescription.value,
                exercise_time=exercise_time.value,
                exercise_frequency=exercise_frequency.value,
                exercise_intensity=exercise_intensity.value,
                daily_activity=daily_activity.value,
                other1=other1.value,
                other2=other2.value
            )
            session.add(template)
        session.commit()
        session.close()

        snack_bar = ft.SnackBar(
            content=ft.Text("テンプレートが保存されました"),
            duration=1000)
        snack_bar.open = True
        page.overlay.append(snack_bar)
        page.update()
        open_route(None)

    def route_change(e):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Row(
                        controls=[
                            patient_id,
                            name_value,
                            kana_value,
                            gender_value,
                            birthdate_value,
                        ]
                    ),
                    ft.Row(
                        controls=[
                            doctor_id_value,
                            doctor_name_value,
                            department_id_value,
                            department_value,
                            settings_button,
                            manual_button,
                        ]
                    ),
                    ft.Row(
                        controls=[
                            buttons,
                            ft.Text("(SOAP画面を閉じるとアプリは終了します)", size=12)
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("計画書一覧", size=16),
                            ft.Text("計画書をクリックすると編集画面が開きます", size=14),
                        ]
                    ),
                    ft.Divider(),
                    history_scrollable,
                ],
            )
        )

        if page.route == "/create":
            page.views.append(
                ft.View(
                    "/create",
                    [
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text("新規作成", size=16, weight=ft.FontWeight.BOLD),
                                    border=ft.border.all(3, ft.colors.BLUE),
                                    padding=5,
                                    border_radius=5,
                                ),
                                main_diagnosis,
                                sheet_name_dropdown,
                                creation_count,
                                ft.Text("回目", size=14),
                                issue_date_row,
                            ]
                        ),
                        goal1,
                        goal2,
                        guidance_items,
                        create_buttons,
                    ],
                )
            )
        page.update()

        if page.route == "/edit":
            page.views.append(
                ft.View(
                    "/edit",
                    [
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text("編集", size=16, weight=ft.FontWeight.BOLD),
                                    border=ft.border.all(3, ft.colors.BLUE),
                                    padding=5,
                                    border_radius=5,
                                ),
                                main_diagnosis,
                                sheet_name_dropdown,
                                creation_count,
                                ft.Text("回目", size=14),
                                issue_date_row,
                            ]
                        ),
                        ft.Row(
                            controls=[
                                goal1,
                            ]
                        ),
                        goal2,
                        guidance_items,
                        edit_buttons,
                    ],
                )
            )
        page.update()

        if page.route == "/template":
            page.views.append(
                ft.View(
                    "/template",
                    [
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text("テンプレート", size=16, weight=ft.FontWeight.BOLD),
                                    border=ft.border.all(3, ft.colors.BLUE),
                                    padding=5,
                                    border_radius=5,
                                ),
                                main_diagnosis,
                                sheet_name_dropdown,
                            ]
                        ),
                        ft.Row(
                            controls=[
                                goal1,
                            ]
                        ),
                        goal2,
                        guidance_items_template,
                        template_buttons,
                    ],
                )
            )
        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def open_create(e):
        page.go("/create")

    def open_edit(e):
        page.go("/edit")

    def open_template(e):
        page.go("/template")
        apply_template()

    def open_route(e):
        for field in [target_weight, target_bp, target_hba1c, goal1, goal2, target_achievement, diet1, diet2, diet3,
                      diet4, diet_comment, exercise_prescription, exercise_time, exercise_frequency, exercise_intensity,
                      daily_activity, exercise_comment, other1, other2, issue_date_value]:
            field.value = ""

        main_diagnosis.value = ""
        sheet_name_dropdown.value = ""
        creation_count.value = 1
        nonsmoker.value = False
        smoking_cessation.value = False
        ophthalmology.value = False
        dental.value = False
        cancer_screening.value = False

        # 発行日を現在の日付で初期化
        current_date = datetime.now().date()
        issue_date_value.value = current_date.strftime("%Y/%m/%d")
        issue_date_picker.value = current_date

        page.go("/")
        update_history(int(patient_id.value))
        page.update()

    def open_manual_pdf(e):
        if manual_pdf_path and os.path.exists(manual_pdf_path):
            try:
                os.startfile(manual_pdf_path)
            except Exception as e:
                error_message = f"PDFを開けませんでした: {str(e)}"
                error_snack_bar = ft.SnackBar(content=ft.Text(error_message), duration=1000)
                error_snack_bar.open = True
                page.overlay.append(error_snack_bar)
                page.update()
        else:
            error_message = "操作マニュアルのパスを確認してください"
            error_snack_bar = ft.SnackBar(content=ft.Text(error_message), duration=1000)
            error_snack_bar.open = True
            page.overlay.append(error_snack_bar)
            page.update()

    def on_close(e):
        page.window.close()

    def on_tobacco_checkbox_change(e):
        if e.control == nonsmoker and nonsmoker.value:
            smoking_cessation.value = False
            smoking_cessation.update()
        elif e.control == smoking_cessation and smoking_cessation.value:
            nonsmoker.value = False
            nonsmoker.update()

    # UIコンポーネントの作成
    # Patient Information
    patient_id = ft.TextField(label="患者ID", on_change=on_patient_id_change, value=initial_patient_id, width=150,
                              height=input_height)
    issue_date_value = ft.TextField(label="発行日", width=150, read_only=True, height=input_height)
    name_value = ft.TextField(label="氏名", read_only=True, width=150, height=input_height)
    kana_value = ft.TextField(label="カナ", read_only=True, width=150, height=input_height)
    gender_value = ft.TextField(label="性別", read_only=True, width=150, height=input_height)
    birthdate_value = ft.TextField(label="生年月日", read_only=True, width=150, height=input_height)
    doctor_id_value = ft.TextField(label="医師ID", read_only=True, width=150, height=input_height)
    doctor_name_value = ft.TextField(label="医師名", read_only=True, width=150, height=input_height)
    department_id_value = ft.TextField(label="診療科ID", read_only=True, width=150, height=input_height)
    department_value = ft.TextField(label="診療科", read_only=True, width=150, height=input_height)

    # ドロップダウンと入力項目
    main_disease_options = load_main_diseases()
    main_diagnosis = ft.Dropdown(
        label="主病名",
        options=main_disease_options,
        width=200, text_size=13, value="",
        on_change=on_main_diagnosis_change,
        autofocus=True,
        height=input_height
    )
    sheet_name_options = load_sheet_names(main_diagnosis.value)
    sheet_name_dropdown = ft.Dropdown(label="シート名", options=sheet_name_options, width=300, text_size=13, value="",
                                      on_change=on_sheet_name_change, height=input_height)
    creation_count = ft.TextField(
        label="作成回数",
        width=100,
        value="1",
        on_submit=lambda _: goal1.focus(),
        text_size=13,
        height=input_height
    )
    target_weight = ft.TextField(label="目標体重", width=150, value="", text_size=13, height=input_height)
    target_bp = ft.TextField(label="目標血圧", width=150, text_size=13, height=input_height)
    target_hba1c = ft.TextField(label="目標HbA1c", width=150, text_size=13, height=input_height)
    goal1 = ft.TextField(label="①達成目標：患者と相談した目標", width=800, value="主病名とシート名を選択してください",
                         on_submit=lambda _: target_weight.focus(), text_size=13, height=text_height)
    goal2 = ft.TextField(label="②行動目標：患者と相談した目標", width=800,
                         on_submit=lambda _: exercise_frequency.focus(), text_size=13, height=text_height)

    # ドロップダウンフィールドの作成
    (exercise_prescription, exercise_time, exercise_frequency, exercise_intensity,
     daily_activity, target_achievement, diet1, diet2, diet3, diet4) = create_form_fields(dropdown_items)

    diet_comment = ft.TextField(label="食事フリーコメント", width=800,
                                on_submit=lambda _: exercise_comment.focus(), text_size=13, height=text_height)
    exercise_comment = ft.TextField(label="運動フリーコメント", width=800,
                                    on_submit=lambda _: other1.focus(), text_size=13, height=text_height)

    nonsmoker = ft.Checkbox(label="非喫煙者である", on_change=on_tobacco_checkbox_change, height=text_height)
    smoking_cessation = ft.Checkbox(label="禁煙の実施方法等を指示", on_change=on_tobacco_checkbox_change,
                                    height=text_height)
    other1 = ft.TextField(label="その他1", value="", width=400, on_submit=lambda _: other2.focus(), text_size=13,
                          height=text_height)
    other2 = ft.TextField(label="その他2", value="", width=400, text_size=13, height=text_height)
    ophthalmology = ft.Checkbox(label="眼科", height=text_height)
    dental = ft.Checkbox(label="歯科", height=text_height)
    cancer_screening = ft.Checkbox(label="がん検診", height=text_height)

    # ガイダンス項目のレイアウト
    guidance_items = ft.Column([
        ft.Row([target_achievement,
                target_weight, ft.Text("kg", size=13),
                target_bp, ft.Text("mmHg", size=13),
                target_hba1c, ft.Text("%", size=13), ]),
        ft.Row([diet1, diet2]),
        ft.Row([diet3, diet4]),
        ft.Row([diet_comment]),
        ft.Row([exercise_prescription, exercise_time, exercise_frequency, exercise_intensity, daily_activity, ]),
        ft.Row([exercise_comment]),
        ft.Row([ft.Text("たばこ", size=14), nonsmoker, smoking_cessation,
                ft.Text("    (チェックボックスを2回選ぶと解除できます)", size=12)]),
        ft.Row([other1, other2]),
        ft.Row([ft.Text("受診勧奨", size=14), ophthalmology, dental, cancer_screening]),
    ])

    guidance_items_template = ft.Column([
        ft.Row([target_bp, ft.Text("mmHg", size=13),
                target_hba1c, ft.Text("%", size=13), ]),
        ft.Row([diet1, diet2]),
        ft.Row([diet3, diet4]),
        ft.Row([exercise_prescription, exercise_time, exercise_frequency, exercise_intensity, daily_activity]),
        ft.Row([other1, other2]),
    ])

    # データテーブル
    history = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("発行日")),
            ft.DataColumn(ft.Text("診療科")),
            ft.DataColumn(ft.Text("医師名")),
            ft.DataColumn(ft.Text("主病名")),
            ft.DataColumn(ft.Text("シート名")),
            ft.DataColumn(ft.Text("作成回数")),
        ],
        rows=[],
        width=1200,
    )

    history_column = ft.Column([history], scroll=ft.ScrollMode.AUTO, width=1200, height=400)
    history_scrollable = ft.Container(
        content=history_column,
        width=1200,
        height=400,
        border=ft.border.all(1, ft.colors.BLACK),
        border_radius=5,
        padding=10,
    )

    # ボタンスタイルの作成
    button_style = create_theme_aware_button_style(page)

    # ボタンの定義
    buttons = ft.Row([
        ft.ElevatedButton("新規作成", on_click=open_create, **button_style),
        ft.ElevatedButton("前回計画コピー", on_click=copy_data, **button_style),
        ft.ElevatedButton("テンプレート編集", on_click=open_template, **button_style),
        ft.ElevatedButton("閉じる", on_click=on_close, **button_style),
    ])

    create_buttons = ft.Row([
        ft.ElevatedButton("新規登録して印刷", on_click=create_new_plan, **button_style),
        ft.ElevatedButton("新規登録", on_click=save_new_plan, **button_style),
        ft.ElevatedButton("戻る", on_click=open_route, **button_style),
    ])

    edit_buttons = ft.Row([
        ft.ElevatedButton("保存", on_click=save_data, **button_style),
        ft.ElevatedButton("印刷", on_click=print_plan, **button_style),
        ft.ElevatedButton("削除", on_click=delete_data, **button_style),
        ft.ElevatedButton("戻る", on_click=open_route, **button_style),
    ])

    template_buttons = ft.Row([
        ft.ElevatedButton("保存", on_click=save_template, **button_style),
        ft.ElevatedButton("戻る", on_click=open_route, **button_style),
    ])

    settings_button = ft.ElevatedButton("設定", on_click=open_settings_dialog, **button_style)
    manual_button = ft.ElevatedButton("操作マニュアル", on_click=open_manual_pdf, **button_style)
    issue_date_button = ft.ElevatedButton(
        "日付選択",
        icon=ft.icons.CALENDAR_TODAY,
        on_click=open_date_picker,
        **button_style
    )

    issue_date_row = ft.Row([issue_date_value, issue_date_button])

    # レイアウト初期化と設定
    layout = ft.Column([
        ft.Row(
            controls=[]
        ),
    ])

    page.add(layout)
    update_history()

    if initial_patient_id:
        load_patient_info(int(initial_patient_id))
        patient_id.value = initial_patient_id
        filter_data(patient_id.value)
        update_history(patient_id.value)

    # イベントハンドラの設定
    page.window.on_resized = on_startup
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)
