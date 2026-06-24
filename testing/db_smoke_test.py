"""
Simple DB smoke tests for VitalFlow.
Creates a temporary staff user, adds blood stock, consumes some blood, and reports results.
Run with: python testing/db_smoke_test.py
"""

from datetime import datetime
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import models_compat as models


def main():
    print("DB Smoke Test: VitalFlow")
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    # Generate a short username within 20 chars (DB constraint)
    suffix = now[-6:]
    smoke_user = f"smoketest_{suffix}"  # e.g. smoketest_130037 -> length <= 20
    if len(smoke_user) > 20:
        smoke_user = smoke_user[:20]
    password = "Smok3t!"
    role_id = 2
    hospital_id = 1

    print(f"Creating staff user: {smoke_user}")
    try:
        success, msg, staff_id = models.add_staff(smoke_user, password, role_id, hospital_id, "smoke_test")
        print("add_staff ->", success, msg, staff_id)
    except Exception as e:
        print("add_staff raised:", e)
        staff_id = None

    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Adding blood stock (O+ 450ml) to hospital {hospital_id}")
    try:
        success, msg, blood_id = models.add_blood_stock(hospital_id, 'O+', 450, today, 'smoke_test')
        print("add_blood_stock ->", success, msg, blood_id)
    except Exception as e:
        print("add_blood_stock raised:", e)
        blood_id = None

    print(f"Fetching blood for hospital {hospital_id}")
    try:
        stock = models.get_blood_by_hospital(hospital_id)
        print(f"Found {len(stock) if stock else 0} blood units")
        if stock:
            print("Sample row:", stock[0])
    except Exception as e:
        print("get_blood_by_hospital raised:", e)

    if blood_id:
        print(f"Consuming 100ml from blood id {blood_id}")
        try:
            success, msg = models.consume_blood(blood_id, 100, 'smoke_test')
            print("consume_blood ->", success, msg)
        except Exception as e:
            print("consume_blood raised:", e)

    # Cleanup: attempt to delete created staff (best-effort)
    if staff_id:
        try:
            success, msg = models.delete_staff(staff_id, 'smoke_test_cleanup')
            print("delete_staff ->", success, msg)
        except Exception as e:
            print("delete_staff raised:", e)

    print("DB smoke test completed.")


if __name__ == '__main__':
    main()
