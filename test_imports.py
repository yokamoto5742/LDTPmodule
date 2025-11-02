"""Import test for refactored modules"""

try:
    print("Testing models import...")
    from models import Base, PatientInfo, MainDisease, SheetName, Template
    print("OK: models import succeeded")

    print("\nTesting database.initializer import...")
    from database.initializer import initialize_database, seed_initial_data
    print("OK: database.initializer import succeeded")

    print("\nTesting main import...")
    import main
    print("OK: main.py import succeeded")

    print("\nAll imports succeeded!")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
