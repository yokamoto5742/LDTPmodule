"""Widget layer import test"""

try:
    print("Testing widgets import...")
    from widgets import (
        DropdownItems,
        create_blue_outlined_dropdown,
        create_form_fields,
        create_theme_aware_button_style,
    )
    print("OK: widgets import succeeded")

    print("\nTesting main.py import...")
    import main
    print("OK: main.py import succeeded")

    print("\nAll widget imports succeeded!")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
