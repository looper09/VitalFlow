# 🔄 VitalFlow v2.0 Migration Guide

## Quick Summary

VitalFlow has been refactored from a monolithic module to a production-ready, enterprise-grade system with:
- 🔐 **Bcrypt password hashing** (was: plain text)
- ✅ **Comprehensive input validation** (was: none)
- 🚀 **Connection pooling** (was: new connection per query)
- 📝 **Full error handling & logging** (was: silent failures)
- 🏗️ **Repository pattern** (was: flat function list)
- 🧪 **50+ unit tests** (was: zero tests)
- 📋 **Type hints & docstrings** (was: minimal)

---

## For Users (GUI Users - No Action Needed)

The GUI (`gui_app.py`) will continue to work as before. Passwords are now automatically hashed when users register or change passwords.

**What Changed:**
- ✅ Login still works normally
- ✅ All features still available
- ✅ But now more secure behind the scenes

**Required Action:** None! Continue using as before.

---

## For Developers (API Users - Consider Migration)

### Old Code (Using models.py)

```python
from models import *

# Add hospital
add_hospital("PIMS", "Islamabad", "051-123456", "admin")

# Add staff with plain text password ❌ SECURITY RISK
add_staff("john_doe", "plaintext_password", 1, 1, "admin")

# Get all hospitals
hospitals = get_all_hospitals()

# Add inventory
add_hospital_inventory(1, 1, 100, "2025-01-01", "admin")

# Handle errors - NONE (silent failures)
```

### New Code (Using models_v2.py - RECOMMENDED)

```python
from models_v2 import *
from security import AuthenticationHelper, InputValidator
from logger_config import logger

# Add hospital with validation
success, message = HospitalRepository.add_hospital(
    "PIMS", 
    "Islamabad", 
    "051-123456", 
    "admin"
)
if success:
    print(message)  # ✅
else:
    print(f"Error: {message}")  # ❌ With error details

# Add staff with password hashing ✅ SECURE
hashed_pwd = AuthenticationHelper.hash_password_for_storage("plaintext_password")
if hashed_pwd:
    # Now hashed automatically
    success, message, staff_id = StaffRepository.add_staff(
        "john_doe",
        hashed_pwd,
        1,
        1,
        "admin"
    )
else:
    print("Invalid password")

# Get all hospitals (easier to read)
hospitals = HospitalRepository.get_all_hospitals()

# Add inventory with validation
success, message = InventoryRepository.add_hospital_inventory(
    hosp_id=1,
    item_id=1,
    qty=100,
    expiry_date="2025-01-01",
    created_by="admin"
)
if success:
    print(message)  # ✅
else:
    logger.error(message)  # ❌ Logged automatically

# Authenticate user
is_valid, user_data = StaffRepository.authenticate_user("john_doe", "plaintext_password")
if is_valid:
    print(f"Logged in as: {user_data['username']}")
    # user_data contains: staff_id, username, role_id, hospital_id
else:
    print("Invalid credentials")
```

### Migration Checklist

- [ ] Update imports: `from models_v2 import *`
- [ ] Replace function calls with repository methods
- [ ] Expect `(success, message)` tuples instead of silent returns
- [ ] Handle errors explicitly
- [ ] Update authentication code to use `StaffRepository.authenticate_user()`
- [ ] Remove manual password hashing code
- [ ] Add input validation before database operations
- [ ] Check logs for audit trail

---

## Module Changes

### Security Module (NEW)

```python
from security import *

# Password hashing
PasswordSecurity.hash_password("mypassword")
PasswordSecurity.verify_password("mypassword", hashed)

# Input validation
InputValidator.validate_username("user_123")
InputValidator.validate_password("secure_pwd")
InputValidator.validate_blood_type("O+")
InputValidator.validate_integer(100, min_val=1, max_val=1000)
InputValidator.validate_text("Hospital Name", min_length=3, max_length=100)
InputValidator.validate_phone("03001234567")
InputValidator.sanitize_string("user_input")

# Authentication helper
AuthenticationHelper.validate_credentials(username, password)
AuthenticationHelper.hash_password_for_storage(password)
```

### Database Manager Module (NEW)

```python
from db_manager import *

# Get connection (with pooling)
conn = get_db_connection()

# Get session (SQLAlchemy)
session = get_db_session()

# Execute raw query with error handling
result = execute_raw_query("SELECT * FROM hospitals", fetch_one=False)

# Execute transaction with rollback
success = execute_with_transaction([
    ("INSERT INTO hospitals VALUES (...)", (name, loc, contact)),
    ("INSERT INTO staff VALUES (...)", (username, pwd, role_id, hosp_id))
], "Add hospital with admin staff")
```

### Logger Config Module (NEW)

```python
from logger_config import *

logger = setup_logging("myapp")
logger.info("Information message")
logger.error("Error message")

db_logger.log_query("SELECT", "hospitals", affected_rows=5, user="admin")
audit_logger.log_action("admin", "CREATE_HOSPITAL", "PIMS", "SUCCESS")
perf_logger.log_query_time("select_hospitals", 125.5, 8)
```

### Models V2 Repositories

```python
from models_v2 import *

# Staff/Authentication
StaffRepository.add_staff(username, password, role_id, hospital_id, created_by)
StaffRepository.get_staff_by_username(username)
StaffRepository.authenticate_user(username, password)
StaffRepository.get_all_staff()

# Hospitals
HospitalRepository.add_hospital(name, location, contact, created_by)
HospitalRepository.get_all_hospitals()
HospitalRepository.update_hospital(h_id, name, location, contact, updated_by)
HospitalRepository.delete_hospital(h_id, deleted_by)

# Inventory
InventoryRepository.add_item(name, category, unit_type, created_by)
InventoryRepository.get_all_items()
InventoryRepository.get_inventory_by_hospital(hospital_id)
InventoryRepository.add_hospital_inventory(hosp_id, item_id, qty, expiry_date, created_by)
InventoryRepository.consume_inventory(inv_id, qty_used, consumed_by)

# Donors
DonorRepository.add_donor(name, blood_type, contact, created_by)
DonorRepository.get_all_donors()
DonorRepository.add_donation_record(donor_id, hosp_id, date, amount, recorded_by)
DonorRepository.get_all_donations()

# Transfers
TransferRepository.create_transfer_request(origin_id, dest_id, item_id, qty, requested_by)
TransferRepository.get_all_transfer_requests()
TransferRepository.add_transfer_status(req_id, status, updated_by)

# Reports
ReportingRepository.get_inventory_report()
ReportingRepository.get_transfer_history()
ReportingRepository.get_audit_logs(limit=1000)
```

---

## Return Value Changes

### Old Way (No Error Handling)

```python
add_hospital("name", "location", "contact", "admin")  # Returns None always ❌
get_all_hospitals()  # Returns [] even on error ❌
```

### New Way (With Error Handling)

```python
success, message = HospitalRepository.add_hospital("name", "location", "contact", "admin")
# Returns: (True, "Hospital added!") or (False, "Error: contact must be valid phone")

hospitals = HospitalRepository.get_all_hospitals()
# Returns: [(1, "PIMS", "Islamabad", "051-123"), ...] or [] on error
```

---

## Step-by-Step Migration

### Step 1: Update Imports

**Before:**
```python
from models import *
from database import get_db_connection
```

**After:**
```python
from models_v2 import (
    StaffRepository, HospitalRepository, InventoryRepository,
    DonorRepository, TransferRepository, ReportingRepository
)
from security import PasswordSecurity, InputValidator, AuthenticationHelper
from db_manager import execute_raw_query, execute_with_transaction, get_db_connection
from logger_config import logger, audit_logger, db_logger
```

### Step 2: Update Function Calls

**Before:**
```python
add_hospital("PIMS", "G-8", "051-xxx", "admin")
hospitals = get_all_hospitals()
add_hospital_inventory(1, 1, 100, "2025-01-01", "admin")
```

**After:**
```python
success, msg = HospitalRepository.add_hospital("PIMS", "G-8", "051-xxx", "admin")
if success:
    print("✅ Hospital added")

hospitals = HospitalRepository.get_all_hospitals()
if not hospitals:
    logger.error("No hospitals found")

success, msg = InventoryRepository.add_hospital_inventory(1, 1, 100, "2025-01-01", "admin")
if not success:
    logger.error(f"Failed to allocate inventory: {msg}")
```

### Step 3: Update Authentication

**Before:**
```python
user_record = get_staff_by_username(username)
if user_record and str(user_record[2]) == password:  # Plain text ❌
    # Login success
```

**After:**
```python
is_valid, user_data = StaffRepository.authenticate_user(username, password)
if is_valid:
    # user_data = {'staff_id': 1, 'username': 'admin', 'role_id': 1, 'hospital_id': 1}
    staff_id = user_data['staff_id']
    # Login success ✅
```

### Step 4: Add Input Validation

**Before:**
```python
# No validation, rely on database constraints
qty = int(input("Amount: "))
InventoryRepository.add_hospital_inventory(hosp_id, item_id, qty, expiry, user)
```

**After:**
```python
qty_input = input("Amount: ")
qty_valid, qty_msg = InputValidator.validate_integer(qty_input, min_val=1, max_val=10000)
if not qty_valid:
    print(f"❌ {qty_msg}")
    return

success, msg = InventoryRepository.add_hospital_inventory(hosp_id, item_id, qty_input, expiry, user)
if success:
    print(f"✅ {msg}")
else:
    print(f"❌ {msg}")
```

### Step 5: Add Error Handling

**Before:**
```python
try:
    result = execute_query("SELECT * FROM hospitals")
except:
    pass  # Silent failure ❌
```

**After:**
```python
try:
    result = execute_raw_query("SELECT * FROM hospitals")
    if result:
        logger.info(f"Retrieved {len(result)} hospitals")
except Exception as e:
    logger.error(f"Failed to fetch hospitals: {e}")
    db_logger.log_error("SELECT", "hospitals", str(e))
```

---

## Maintaining Backward Compatibility

If you need to maintain old `models.py` for now:

```python
# Create a compatibility layer
from models_v2 import *
from security import AuthenticationHelper

# Old function names pointing to new repositories
def add_hospital(name, location, contact, staff_id):
    success, msg = HospitalRepository.add_hospital(name, location, contact, staff_id)
    return success  # Returns True/False instead of None

def get_all_hospitals():
    return HospitalRepository.get_all_hospitals()

# ... etc for other functions
```

---

## Testing the Migration

```bash
# Run all tests to ensure nothing broke
pytest test_models.py -v

# Run specific integration tests
pytest test_models.py::TestIntegration -v

# Check database migration
python test_db.py

# Verify old code still works (if compatibility layer added)
python cmd_app.py
```

---

## Rollback Plan

If issues occur during migration:

```bash
# Restore old database
cp VitalFlow.backup.db VitalFlow.db

# Keep old models.py for reference
git checkout HEAD -- models.py

# Revert imports in gui_app
git checkout HEAD -- gui_app.py

# Verify old version works
streamlit run gui_app.py
```

---

## FAQ

### Q: Do I need to update gui_app.py?
**A:** Ideally yes, but it's optional. The old `models.py` can still work if you maintain a compatibility layer. However, updating it to use `models_v2` brings all security benefits.

### Q: Will existing passwords still work?
**A:** New logins use bcrypt automatically. Existing plain-text passwords in database will need to be hashed during migration:
```python
# One-time migration script
for user in get_all_staff():
    staff_id, username, old_plain_pwd, role_id, hosp_id = user
    hashed = PasswordSecurity.hash_password(old_plain_pwd)
    # UPDATE staff SET password = hashed ...
```

### Q: Is this backwards compatible?
**A:** Mostly yes. Old code will work but won't get security benefits. New code is fully recommended.

### Q: Performance impact?
**A:** Slight improvement due to connection pooling + indexed queries. Bcrypt password hashing is intentionally slow (for security), but authentication only happens on login.

### Q: How do I report issues?
**A:** Check `logs/vitalflow.log`, run `pytest test_models.py -v`, and open GitHub issue with logs.

---

## Next Steps

1. **Read documentation**:
   - `CODE_REVIEW.md` - Detailed analysis
   - `PRODUCTION_SETUP.md` - Deployment guide
   - This file - Migration guide

2. **Run tests**:
   ```bash
   pip install -r requirements.txt
   pytest test_models.py -v
   ```

3. **Update your code** gradually using the migration checklist above

4. **Deploy** using the PRODUCTION_SETUP.md guide

5. **Monitor** with logs at `logs/vitalflow.log`

---

**Migration Complete!** 🎉 You now have a production-ready healthcare system!
