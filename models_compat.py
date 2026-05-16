"""
Backward compatibility wrapper for gui_app.py
Maps old models.py function calls to new models_v2.py Repository pattern
"""
from models_v2 import (
    StaffRepository, HospitalRepository, InventoryRepository,
    DonorRepository, TransferRepository, ReportingRepository
)

# 🚨 UPDATED: Moved imports to the top for maximum UI performance
from blood_bank_module import (
    BloodBankRepository, 
    DonorEligibilityManager, 
    BloodBankReporting
)

# ==========================================
# STAFF FUNCTIONS
# ==========================================
def get_staff_by_username(username: str):
    """Get staff by username"""
    return StaffRepository.get_staff_by_username(username)

def get_all_staff():
    """Get all staff"""
    return StaffRepository.get_all_staff()

# ==========================================
# HOSPITAL FUNCTIONS
# ==========================================
def get_all_hospitals():
    """Get all hospitals"""
    return HospitalRepository.get_all_hospitals()

def add_hospital(name, location, contact, created_by):
    """Add a hospital"""
    success, msg = HospitalRepository.add_hospital(name, location, contact, created_by)
    return success, msg

def update_hospital(h_id, name=None, location=None, contact=None, updated_by="System"):
    """Update a hospital"""
    success, msg = HospitalRepository.update_hospital(h_id, name, location, contact, updated_by)
    return success, msg

def delete_hospital(h_id, deleted_by="System"):
    """Delete a hospital"""
    success, msg = HospitalRepository.delete_hospital(h_id, deleted_by)
    return success, msg

# ==========================================
# INVENTORY FUNCTIONS
# ==========================================
def get_all_items():
    """Get all inventory items"""
    return InventoryRepository.get_all_items()

def add_item(name, category, unit_type, created_by):
    """Add an inventory item"""
    success, msg = InventoryRepository.add_item(name, category, unit_type, created_by)
    return success, msg

def update_item(item_id, name=None, category=None, unit_type=None, updated_by="System"):
    """Update an inventory item"""
    success, msg = InventoryRepository.update_item(item_id, name, category, unit_type, updated_by)
    return success, msg

def delete_item(item_id, deleted_by="System"):
    """Delete an inventory item"""
    success, msg = InventoryRepository.delete_item(item_id, deleted_by)
    return success, msg

def get_inventory_by_hospital(hospital_id):
    """Get inventory for a specific hospital"""
    return InventoryRepository.get_inventory_by_hospital(hospital_id)

def add_hospital_inventory(hosp_id, item_id, qty, expiry_date, created_by):
    """Add stock to hospital inventory"""
    success, msg = InventoryRepository.add_hospital_inventory(hosp_id, item_id, qty, expiry_date, created_by)
    return success, msg

def consume_hospital_inventory(inventory_id, qty, consumed_by):
    """Consume stock from hospital inventory"""
    success, msg = InventoryRepository.consume_hospital_inventory(inventory_id, qty, consumed_by)
    return success, msg

def update_hospital_inventory(inventory_id, qty=None, expiry_date=None, updated_by="System"):
    """Update hospital inventory"""
    success, msg = InventoryRepository.update_hospital_inventory(inventory_id, qty, expiry_date, updated_by)
    return success, msg

# ==========================================
# DONOR FUNCTIONS
# ==========================================
def get_all_donors():
    """Get all donors"""
    return DonorRepository.get_all_donors()

def add_donor(name, blood_type, contact, created_by):
    """Register a donor"""
    success, msg = DonorRepository.add_donor(name, blood_type, contact, created_by)
    return success, msg

def update_donor(donor_id, name=None, blood_type=None, contact=None, updated_by="System"):
    """Update donor info"""
    success, msg = DonorRepository.update_donor(donor_id, name, blood_type, contact, updated_by)
    return success, msg

def delete_donor(donor_id, deleted_by="System"):
    """Delete a donor"""
    success, msg = DonorRepository.delete_donor(donor_id, deleted_by)
    return success, msg

def get_all_donations():
    """Get all donation records"""
    return DonorRepository.get_all_donations()

# ==========================================
# TRANSFER FUNCTIONS
# ==========================================
def get_all_transfer_requests():
    """Get all transfer requests"""
    return TransferRepository.get_all_transfer_requests()

def add_transfer_request(origin_hosp_id, dest_hosp_id, item_id, qty, created_by):
    """Create transfer request"""
    success, msg = TransferRepository.add_transfer_request(origin_hosp_id, dest_hosp_id, item_id, qty, created_by)
    return success, msg

def add_transfer_status(req_id, status, updated_by):
    """Update transfer status"""
    success, msg = TransferRepository.add_transfer_status(req_id, status, updated_by)
    return success, msg

# ==========================================
# REPORTING FUNCTIONS
# ==========================================
def get_inventory_report():
    """Get inventory report"""
    return ReportingRepository.get_inventory_report()

def get_full_transfer_history():
    """Get complete transfer history"""
    return ReportingRepository.get_transfer_history()

def get_transfer_history():
    """Alias for get_full_transfer_history"""
    return ReportingRepository.get_transfer_history()

def get_audit_logs(limit=1000):
    """Get audit logs"""
    return ReportingRepository.get_audit_logs(limit)

# ==========================================
# STAFF MANAGEMENT (NEW)
# ==========================================
def add_staff(username, password, role_id, hospital_id, created_by):
    """Add new staff member"""
    success, msg, staff_id = StaffRepository.add_staff(username, password, role_id, hospital_id, created_by)
    return success, msg, staff_id

def delete_staff(staff_id, deleted_by="System"):
    """Delete staff member"""
    success, msg = StaffRepository.delete_staff(staff_id, deleted_by)
    return success, msg

def update_staff(staff_id, username=None, password=None, role_id=None, hospital_id=None, updated_by="System"):
    """Update staff member"""
    success, msg = StaffRepository.update_staff(staff_id, username, password, role_id, hospital_id, updated_by)
    return success, msg

def get_all_logs(limit=1000):
    """Get all audit logs (alias for get_audit_logs)"""
    return ReportingRepository.get_audit_logs(limit)

# ==========================================
# DONATION RECORD MANAGEMENT (NEW)
# ==========================================
def add_donation_record(donor_id, hospital_id, date, amount, recorded_by):
    """Log a donation record"""
    success, msg = DonorRepository.add_donation_record(donor_id, hospital_id, date, amount, recorded_by)
    return success, msg

def delete_donation_record(donation_id, deleted_by="System"):
    """Delete a donation record"""
    success, msg = DonorRepository.delete_donation_record(donation_id, deleted_by)
    return success, msg

def update_donation_amount(donation_id, new_amount, updated_by="System"):
    """Update donation record amount"""
    success, msg = DonorRepository.update_donation_amount(donation_id, new_amount, updated_by)
    return success, msg

# ==========================================
# TRANSFER REQUEST MANAGEMENT (NEW)
# ==========================================
def create_transfer_request(origin_hosp_id, dest_hosp_id, item_id, qty, created_by):
    """Create a transfer request"""
    success, msg = TransferRepository.create_transfer_request(origin_hosp_id, dest_hosp_id, item_id, qty, created_by)
    return success, msg

def delete_transfer_request(request_id, deleted_by="System"):
    """Delete a transfer request"""
    success, msg = TransferRepository.delete_transfer_request(request_id, deleted_by)
    return success, msg

# ==========================================
# ADVANCED REPORTING (NEW)
# ==========================================
def get_donation_report():
    """Get donation statistics report"""
    return ReportingRepository.get_donation_report()

def get_blood_bank_summary():
    """Get blood bank inventory summary"""
    return ReportingRepository.get_blood_bank_summary()

def get_staff_report():
    """Get staff activity report"""
    return ReportingRepository.get_staff_report()

def get_logistics_impact():
    """Get logistics impact analysis"""
    return ReportingRepository.get_logistics_impact()

def get_deep_audit_report():
    """Get comprehensive audit trail"""
    return ReportingRepository.get_deep_audit_report()

# ==========================================
# ALIAS FUNCTIONS FOR COMPATIBILITY
# ==========================================
def get_all_inventory_items():
    """Alias for get_all_items()"""
    return InventoryRepository.get_all_items()

def get_hospital_inventory(hospital_id):
    """Alias for get_inventory_by_hospital()"""
    return InventoryRepository.get_inventory_by_hospital(hospital_id)

def get_all_donation_records():
    """Alias for get_all_donations()"""
    return DonorRepository.get_all_donations()

def get_kpi_dashboard():
    """Get KPI dashboard data"""
    try:
        hospitals = HospitalRepository.get_all_hospitals()
        staff = StaffRepository.get_all_staff()
        donors = DonorRepository.get_all_donors()
        transfers = TransferRepository.get_all_transfer_requests()
        donations = DonorRepository.get_all_donations()
        
        return [
            ("Total Hospitals", len(hospitals)),
            ("Total Staff", len(staff)),
            ("Total Donors", len(donors)),
            ("Transfer Requests", len(transfers)),
            ("Total Donations", len(donations))
        ]
    except Exception as e:
        return [("Error Loading KPIs", 0)]

# ==========================================
# BLOOD BANK MODULE WRAPPERS
# ==========================================

def add_blood_stock(hospital_id: int, blood_type: str, quantity_ml: int, received_date: str, received_by: str):
    """Add blood stock to hospital blood bank"""
    return BloodBankRepository.add_blood_stock(hospital_id, blood_type, quantity_ml, received_date, received_by)

def get_blood_by_hospital(hospital_id: int, blood_type=None, active_only=True):
    """Get blood stock at a hospital"""
    return BloodBankRepository.get_blood_by_hospital(hospital_id, blood_type, active_only)

def consume_blood(blood_id: int, quantity_ml: int, consumed_by: str):
    """Consume blood units for transfusion/testing"""
    return BloodBankRepository.consume_blood(blood_id, quantity_ml, consumed_by)

def get_all_blood_stock():
    """Get all blood stock across all hospitals"""
    return BloodBankRepository.get_all_blood_stock()

def check_donor_eligibility(donor_id: int):
    """Check if donor is eligible to donate (>90 days since last donation)"""
    return DonorEligibilityManager.check_donor_eligibility(donor_id)

def override_donation_eligibility(donor_id: int, override_reason: str, staff_id: int):
    """ADMIN ONLY: Override donation eligibility for emergency transfusion"""
    return DonorEligibilityManager.override_donation_eligibility(donor_id, override_reason, staff_id)

def record_donation_completed(donor_id: int, hospital_id: int, amount_ml: int, donation_date: str, recorded_by: str):
    """Record completed donation and update donor eligibility"""
    return DonorEligibilityManager.record_donation_completed(donor_id, hospital_id, amount_ml, donation_date, recorded_by)

def get_blood_bank_summary_by_type():
    """Get blood bank summary grouped by blood type"""
    return BloodBankReporting.get_blood_bank_summary_by_type()

def get_blood_by_hospital_summary(hospital_id: int):
    """Get blood inventory summary with expiry warnings"""
    return BloodBankReporting.get_blood_by_hospital_summary(hospital_id)

def get_donor_eligibility_report():
    """Get donor eligibility status report"""
    return BloodBankReporting.get_donor_eligibility_report()

def check_blood_expiry():
    """Check and auto-expire old blood. Call this periodically or on app startup."""
    total, expired = BloodBankRepository.check_expiry_and_mark()
    return total, expired