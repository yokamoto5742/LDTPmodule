"""Service layer import test"""

try:
    print("Testing services import...")
    from services import (
        TreatmentPlanGenerator,
        TemplateManager,
        load_patient_data,
        load_main_diseases,
        load_sheet_names,
        fetch_patient_history,
        start_file_monitoring,
        check_file_exists,
        export_to_csv,
        import_from_csv,
    )
    print("OK: services import succeeded")

    print("\nTesting main.py import...")
    import main
    print("OK: main.py import succeeded")

    print("\nAll service imports succeeded!")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
