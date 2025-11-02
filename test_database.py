"""Database initialization test"""

import os
from database import get_session_factory
from database.initializer import initialize_database, seed_initial_data
from models import MainDisease, SheetName, Template

# テスト用データベースファイル
test_db = "test_ldtp.db"

# 既存のテストDBを削除
if os.path.exists(test_db):
    os.remove(test_db)
    print(f"Removed existing test database: {test_db}")

try:
    print("\nStep 1: Initialize database...")
    initialize_database()
    print("OK: Database initialized")

    print("\nStep 2: Seed initial data...")
    seed_initial_data()
    print("OK: Initial data seeded")

    print("\nStep 3: Verify data...")
    Session = get_session_factory()
    session = Session()

    main_disease_count = session.query(MainDisease).count()
    sheet_name_count = session.query(SheetName).count()
    template_count = session.query(Template).count()

    print(f"  MainDisease records: {main_disease_count}")
    print(f"  SheetName records: {sheet_name_count}")
    print(f"  Template records: {template_count}")

    session.close()

    if main_disease_count == 3 and sheet_name_count == 9 and template_count == 9:
        print("\nOK: All data verification passed!")
    else:
        print("\nERROR: Data verification failed!")
        print(f"  Expected: MainDisease=3, SheetName=9, Template=9")
        print(f"  Got: MainDisease={main_disease_count}, SheetName={sheet_name_count}, Template={template_count}")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
