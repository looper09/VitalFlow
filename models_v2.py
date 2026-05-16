"""
VitalFlow Models Layer - Production Ready
Includes error handling, input validation, type hints, and logging
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from db_manager import execute_raw_query, execute_with_transaction, get_db_connection, db_config
from security import PasswordSecurity, InputValidator, AuthenticationHelper
from logger_config import logger, db_logger, audit_logger

# ==========================================
# DATA CLASSES (Type Safety)
# ==========================================

@dataclass
class Hospital:
    """Hospital entity"""
    hospital_id: int
    name: str
    location: str
    contact: str
    
@dataclass
class Staff:
    """Staff/User entity"""
    staff_id: int
    username: str
    role_id: int
    hospital_id: Optional[int]
    
@dataclass
class InventoryItem:
    """Inventory item entity"""
    item_id: int
    name: str
    category: str
    unit_type: str
    
@dataclass
class Donor:
    """Blood donor entity"""
    donor_id: int
    name: str
    blood_type: str
    contact: str


# ==========================================
# REPOSITORY PATTERN - STAFF/AUTH
# ==========================================

class StaffRepository:
    """Handle all staff/user database operations"""
    
    @staticmethod
    def add_staff(username: str, password: str, role_id: int, hospital_id: Optional[int], 
                  created_by: str) -> Tuple[bool, str, Optional[int]]:
        """
        Add new staff member with proper validation and password hashing.
        
        Args:
            username: Unique username
            password: Plaintext password (will be hashed)
            role_id: Role ID (1=Admin, 2=Staff)
            hospital_id: Associated hospital
            created_by: Admin username creating this user
            
        Returns:
            Tuple of (success: bool, message: str, staff_id: Optional[int])
        """
        # Input validation
        user_valid, user_err = InputValidator.validate_username(username)
        if not user_valid:
            return False, user_err, None
        
        pwd_valid, pwd_err = InputValidator.validate_password(password)
        if not pwd_valid:
            return False, pwd_err, None
        
        # Hash password
        hashed_pwd = AuthenticationHelper.hash_password_for_storage(password)
        if not hashed_pwd:
            return False, "Failed to hash password", None
        
        conn = None
        try:
            conn = get_db_connection()
            if conn is None:
                return False, "Database error occurred", None

            cur = conn.cursor()
            query = """
                INSERT INTO staff (username, password, role_id, hospital_id, created_by)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING staff_id
            """
            cur.execute(query, (username, hashed_pwd, role_id, hospital_id, created_by))
            row = cur.fetchone()
            staff_id = row[0] if row else None

            conn.commit()
            cur.close()

            audit_logger.log_action(created_by, "CREATE_STAFF", username, "SUCCESS")
            logger.info(f"Staff member added: {username}")
            return True, f"Staff member '{username}' created successfully", staff_id

        except Exception as e:
            logger.error(f"Error adding staff: {e}")
            db_logger.log_error("INSERT", "Staff", str(e), created_by)
            return False, f"Error creating staff member: {str(e)}", None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    @staticmethod
    def get_staff_by_username(username: str) -> Optional[Tuple]:
        """
        Get staff member by username for authentication.
        
        Returns:
            Tuple of (staff_id, username, password_hash, role_id, hospital_id) or None
        """
        try:
            query = "SELECT staff_id, username, password, role_id, hospital_id FROM Staff WHERE username = ?"
            result = execute_raw_query(query, (username,), fetch_one=True)
            
            if result:
                db_logger.log_query("SELECT", "Staff", 1, username)
                return result
            
            audit_logger.log_access(username, "LoginAttempt", False)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching staff by username: {e}")
            db_logger.log_error("SELECT", "Staff", str(e))
            return None
    
    @staticmethod
    def get_all_staff() -> List[Tuple]:
        """Get all staff members"""
        try:
            query = "SELECT staff_id, username, role_id, hospital_id FROM Staff ORDER BY staff_id"
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error fetching all staff: {e}")
            return []
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Authenticate a user by username and password.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Tuple of (is_valid: bool, user_data: Dict or None)
        """
        # Validate credentials format first
        valid, err = AuthenticationHelper.validate_credentials(username, password)
        if not valid:
            return False, None
        
        try:
            staff = StaffRepository.get_staff_by_username(username)
            if not staff:
                audit_logger.log_access(username, "Authentication", False)
                return False, None
            
            # Verify password
            if not PasswordSecurity.verify_password(password, staff[2]):  # staff[2] is password hash
                audit_logger.log_access(username, "Authentication", False)
                logger.warning(f"Failed login attempt for user: {username}")
                return False, None
            
            # Success
            audit_logger.log_access(username, "Authentication", True)
            logger.info(f"User authenticated: {username}")
            
            return True, {
                "staff_id": staff[0],
                "username": staff[1],
                "role_id": staff[3],
                "hospital_id": staff[4]
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None
    
    @staticmethod
    def delete_staff(staff_id: int, deleted_by: str) -> Tuple[bool, str]:
        """Delete a staff member"""
        try:
            staff_valid, staff_err = InputValidator.validate_integer(staff_id, 1, field_name="Staff ID")
            if not staff_valid:
                return False, staff_err
            
            query = "DELETE FROM staff WHERE staff_id = ?"
            execute_raw_query(query, (staff_id,))
            
            audit_logger.log_action(deleted_by, "DELETE_STAFF", f"Staff_{staff_id}", "SUCCESS", "")
            logger.info(f"Staff member deleted: {staff_id}")
            return True, "✅ Staff member deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting staff: {e}")
            db_logger.log_error("DELETE", "Staff", str(e), deleted_by)
            return False, f"Error deleting staff: {str(e)}"
    
    @staticmethod
    def update_staff(staff_id: int, username: Optional[str] = None, password: Optional[str] = None, 
                     role_id: Optional[int] = None, hospital_id: Optional[int] = None,
                     updated_by: str = "System") -> Tuple[bool, str]:
        """Update staff member information"""
        try:
            staff_valid, staff_err = InputValidator.validate_integer(staff_id, 1, field_name="Staff ID")
            if not staff_valid:
                return False, staff_err
            
            # Build update query dynamically based on provided fields
            updates = []
            params = []
            
            if username is not None:
                user_valid, user_err = InputValidator.validate_username(username)
                if not user_valid:
                    return False, user_err
                updates.append("username = ?")
                params.append(username)
            
            if password is not None:
                pwd_valid, pwd_err = InputValidator.validate_password(password)
                if not pwd_valid:
                    return False, pwd_err
                hashed_pwd = PasswordSecurity.hash_password(password)
                updates.append("password = ?")
                params.append(hashed_pwd)
            
            if role_id is not None:
                role_valid, role_err = InputValidator.validate_integer(role_id, 1, field_name="Role ID")
                if not role_valid:
                    return False, role_err
                updates.append("role_id = ?")
                params.append(role_id)
            
            if hospital_id is not None:
                hosp_valid, hosp_err = InputValidator.validate_integer(hospital_id, field_name="Hospital ID")
                if not hosp_valid:
                    return False, hosp_err
                updates.append("hospital_id = ?")
                params.append(hospital_id)
            
            if not updates:
                return False, "No fields to update"
            
            params.append(staff_id)
            query = f"UPDATE staff SET {', '.join(updates)} WHERE staff_id = ?"
            execute_raw_query(query, params)
            
            audit_logger.log_action(updated_by, "UPDATE_STAFF", f"Staff_{staff_id}", "SUCCESS", 
                                   f"Fields_updated: {len(updates)}")
            logger.info(f"Staff member updated: {staff_id}")
            return True, "✅ Staff member updated successfully"
            
        except Exception as e:
            logger.error(f"Error updating staff: {e}")
            db_logger.log_error("UPDATE", "Staff", str(e), updated_by)
            return False, f"Error updating staff: {str(e)}"


# ===========================
# REPOSITORY PATTERN - HOSPITALS
# ==========================================

class HospitalRepository:
    """Handle all hospital database operations"""
    
    
    @staticmethod
    def add_hospital(name: str, location: str, contact: str, created_by_id: int) -> Tuple[bool, str]:
        """Add new hospital and record database audit log"""
        # 1. Validate inputs using existing security logic
        name_valid, name_err = InputValidator.validate_text(name, 3, 100, "Hospital name")
        if not name_valid:
            return False, name_err
        
        loc_valid, loc_err = InputValidator.validate_text(location, 3, 150, "Location")
        if not loc_valid:
            return False, loc_err
        
        contact_valid, contact_err = InputValidator.validate_phone(contact)
        if not contact_valid:
            return False, contact_err
        
        try:
            # 2. Insert the hospital into the database
            query = "INSERT INTO hospitals (name, location, contact) VALUES (?, ?, ?)"
            execute_raw_query(query, (name, location, contact))
            
            # 3. CRITICAL: Insert a physical row into the Audit_Logs table
            # This ensures the "Activity Logs" tab in your UI actually has data to show
            log_query = "INSERT INTO Audit_Logs (Staff_ID, Action, Table_Affected) VALUES (?, ?, ?)"
            execute_raw_query(log_query, (created_by_id, f"Registered new hospital: {name}", "Hospitals"))
            
            # 4. Keep Python-level logging for debugging
            audit_logger.log_action(str(created_by_id), "CREATE_HOSPITAL", name, "SUCCESS")
            logger.info(f"Hospital added: {name}")
            
            return True, f"Hospital '{name}' added successfully"
            
        except Exception as e:
            logger.error(f"Error adding hospital: {e}")
            db_logger.log_error("INSERT", "Hospitals", str(e), str(created_by_id))
            return False, f"Error adding hospital: {str(e)}"
    
    @staticmethod
    def get_all_hospitals() -> List[Tuple]:
        """Get all hospitals"""
        try:
            query = "SELECT hospital_id, name, location, contact FROM Hospitals ORDER BY name"
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error fetching hospitals: {e}")
            return []
    
    @staticmethod
    def update_hospital(h_id: int, name: str = None, location: str = None, 
                       contact: str = None, updated_by: str = "System") -> Tuple[bool, str]:
        """Update hospital details"""
        try:
            updates = []
            params = []
            
            if name:
                name_valid, name_err = InputValidator.validate_text(name, 3, 100, "Hospital name")
                if not name_valid:
                    return False, name_err
                updates.append("name = ?")
                params.append(name)
            
            if location:
                loc_valid, loc_err = InputValidator.validate_text(location, 3, 150, "Location")
                if not loc_valid:
                    return False, loc_err
                updates.append("location = ?")
                params.append(location)
            
            if contact:
                contact_valid, contact_err = InputValidator.validate_phone(contact)
                if not contact_valid:
                    return False, contact_err
                updates.append("contact = ?")
                params.append(contact)
            
            if not updates:
                return False, "No fields to update"
            
            params.append(h_id)
            query = f"UPDATE hospitals SET {', '.join(updates)} WHERE hospital_id = ?"
            execute_raw_query(query, tuple(params))
            
            audit_logger.log_action(updated_by, "UPDATE_HOSPITAL", f"Hospital_{h_id}", "SUCCESS")
            return True, "Hospital updated successfully"
            
        except Exception as e:
            logger.error(f"Error updating hospital: {e}")
            db_logger.log_error("UPDATE", "Hospitals", str(e), updated_by)
            return False, f"Error updating hospital: {str(e)}"
    
    @staticmethod
    def delete_hospital(h_id: int, deleted_by: str = "System") -> Tuple[bool, str]:
        """Delete hospital"""
        try:
            h_id_valid, h_id_err = InputValidator.validate_integer(h_id, 1, field_name="Hospital ID")
            if not h_id_valid:
                return False, h_id_err

            dependency_checks = [
                ("Staff", "SELECT COUNT(*) FROM Staff WHERE hospital_id = ?", (h_id,), "staff accounts"),
                ("Hospital_Inventory", "SELECT COUNT(*) FROM Hospital_Inventory WHERE hospital_id = ?", (h_id,), "inventory allocations"),
                ("Blood_Bank", "SELECT COUNT(*) FROM Blood_Bank WHERE hospital_id = ?", (h_id,), "blood units"),
                ("Donation_Records", "SELECT COUNT(*) FROM Donation_Records WHERE hospital_id = ?", (h_id,), "donation records"),
                (
                    "Transfer_Requests",
                    "SELECT COUNT(*) FROM Transfer_Requests WHERE origin_hospital_id = ? OR dest_hospital_id = ?",
                    (h_id, h_id),
                    "transfer requests",
                ),
            ]

            for table_name, check_query, params, label in dependency_checks:
                result = execute_raw_query(check_query, params, fetch_one=True)
                count = result[0] if result else 0
                if count > 0:
                    logger.warning(
                        f"Blocked hospital deletion for {h_id}: {count} {label} still linked"
                    )
                    return False, (
                        f"Cannot delete hospital while {count} {label} exist. "
                        f"Remove related {label} first."
                    )
            
            query = "DELETE FROM Hospitals WHERE hospital_id = ?"
            execute_raw_query(query, (h_id,))
            
            audit_logger.log_action(deleted_by, "DELETE_HOSPITAL", f"Hospital_{h_id}", "SUCCESS")
            logger.info(f"Hospital deleted: ID {h_id}")
            return True, f"Hospital ID {h_id} deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting hospital: {e}")
            db_logger.log_error("DELETE", "Hospitals", str(e), deleted_by)
            return False, f"Error deleting hospital: {str(e)}"


# ==========================================
# REPOSITORY PATTERN - INVENTORY
# ==========================================

class InventoryRepository:
    """Handle all inventory database operations"""
    
    @staticmethod
    def add_item(name: str, category: str, unit_type: str, created_by: str) -> Tuple[bool, str]:
        """Add new inventory item to global catalog"""
        # Validate
        name_valid, name_err = InputValidator.validate_text(name, 2, 100, "Item name")
        if not name_valid:
            return False, name_err
        
        cat_valid, cat_err = InputValidator.validate_text(category, 2, 50, "Category")
        if not cat_valid:
            return False, cat_err
        
        unit_valid, unit_err = InputValidator.validate_text(unit_type, 1, 50, "Unit type")
        if not unit_valid:
            return False, unit_err
        
        try:
            query = "INSERT INTO inventory_items (item_name, category, unit_type) VALUES (?, ?, ?)"
            execute_raw_query(query, (name, category, unit_type))
            
            audit_logger.log_action(created_by, "CREATE_ITEM", name, "SUCCESS")
            logger.info(f"Inventory item added: {name}")
            return True, f"Item '{name}' added to catalog"
            
        except Exception as e:
            logger.error(f"Error adding inventory item: {e}")
            db_logger.log_error("INSERT", "Inventory_Items", str(e), created_by)
            return False, f"Error adding item: {str(e)}"
    
    @staticmethod
    def get_all_items() -> List[Tuple]:
        """Get all inventory items"""
        try:
            query = "SELECT item_id, item_name, category, unit_type FROM Inventory_Items ORDER BY item_name"
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error fetching inventory items: {e}")
            return []
    
    @staticmethod
    def get_inventory_by_hospital(hospital_id: int) -> List[Tuple]:
        """Get all inventory at a specific hospital"""
        try:
            hosp_valid, hosp_err = InputValidator.validate_integer(hospital_id, 1, field_name="Hospital ID")
            if not hosp_valid:
                return []
            
            query = """
                SELECT hi.inventory_id, hi.hospital_id, hi.item_id, hi.quantity, hi.expiry_date
                FROM hospital_inventory hi
                WHERE hi.hospital_id = ?
                ORDER BY hi.expiry_date
            """
            result = execute_raw_query(query, (hospital_id,))
            return result or []
            
        except Exception as e:
            logger.error(f"Error fetching hospital inventory: {e}")
            return []
    
    @staticmethod
    def add_hospital_inventory(hosp_id: int, item_id: int, qty: int, expiry_date: str,
                              created_by: str) -> Tuple[bool, str]:
        """Allocate stock to a hospital warehouse"""
        # Validate all inputs
        hosp_valid, hosp_err = InputValidator.validate_integer(hosp_id, 1, field_name="Hospital ID")
        if not hosp_valid:
            return False, hosp_err
        
        item_valid, item_err = InputValidator.validate_integer(item_id, 1, field_name="Item ID")
        if not item_valid:
            return False, item_err
        
        qty_valid, qty_err = InputValidator.validate_integer(qty, 1, field_name="Quantity")
        if not qty_valid:
            return False, qty_err
        
        try:
            query = """
                INSERT INTO hospital_inventory (hospital_id, item_id, quantity, expiry_date)
                VALUES (?, ?, ?, ?)
            """
            execute_raw_query(query, (hosp_id, item_id, qty, expiry_date))
            
            audit_logger.log_action(created_by, "ALLOCATE_STOCK", f"Hosp_{hosp_id}", "SUCCESS",
                                   f"Item_{item_id}, Qty_{qty}")
            logger.info(f"Stock allocated - Hospital: {hosp_id}, Item: {item_id}, Qty: {qty}")
            return True, f"✅ {qty} units allocated successfully"
            
        except Exception as e:
            logger.error(f"Error allocating inventory: {e}")
            db_logger.log_error("INSERT", "Hospital_Inventory", str(e), created_by)
            return False, f"Error allocating stock: {str(e)}"
    
    @staticmethod
    def consume_inventory(inv_id: int, qty_used: int, consumed_by: str) -> Tuple[bool, str]:
        """Log medical usage (dispense inventory)"""
        try:
            inv_valid, inv_err = InputValidator.validate_integer(inv_id, 1, field_name="Inventory ID")
            if not inv_valid:
                return False, inv_err
            
            qty_valid, qty_err = InputValidator.validate_integer(qty_used, 1, field_name="Quantity used")
            if not qty_valid:
                return False, qty_err
            
            query = """
                UPDATE hospital_inventory
                SET quantity = quantity - ?
                WHERE inventory_id = ? AND quantity >= ?
            """
            execute_raw_query(query, (qty_used, inv_id, qty_used))
            
            audit_logger.log_action(consumed_by, "DISPENSE_INVENTORY", f"InvID_{inv_id}", "SUCCESS",
                                   f"Qty_{qty_used}")
            logger.info(f"Inventory dispensed - ID: {inv_id}, Qty: {qty_used}")
            return True, f"✅ {qty_used} units dispensed and logged"
            
        except Exception as e:
            logger.error(f"Error consuming inventory: {e}")
            db_logger.log_error("UPDATE", "Hospital_Inventory", str(e), consumed_by)
            return False, f"Error dispensing inventory: {str(e)}"


# ==========================================
# REPOSITORY PATTERN - DONORS
# ==========================================

class DonorRepository:
    """Handle all blood donor database operations"""
    
    @staticmethod
    def add_donor(name: str, blood_type: str, contact: str, created_by: str) -> Tuple[bool, str]:
        """Add new blood donor"""
        # Validate inputs
        name_valid, name_err = InputValidator.validate_text(name, 3, 100, "Donor name")
        if not name_valid:
            return False, name_err
        
        blood_valid, blood_err = InputValidator.validate_blood_type(blood_type)
        if not blood_valid:
            return False, blood_err
        
        contact_valid, contact_err = InputValidator.validate_phone(contact)
        if not contact_valid:
            return False, contact_err
        
        try:
            query = "INSERT INTO donors (name, blood_type, contact) VALUES (?, ?, ?)"
            execute_raw_query(query, (name, blood_type, contact))
            
            audit_logger.log_action(created_by, "REGISTER_DONOR", name, "SUCCESS", f"BloodType_{blood_type}")
            logger.info(f"Donor registered: {name} ({blood_type})")
            return True, f"✅ Donor '{name}' registered successfully"
            
        except Exception as e:
            logger.error(f"Error adding donor: {e}")
            db_logger.log_error("INSERT", "Donors", str(e), created_by)
            return False, f"Error registering donor: {str(e)}"
    
    @staticmethod
    def get_all_donors() -> List[Tuple]:
        """Get all blood donors"""
        try:
            query = "SELECT donor_id, name, blood_type, contact FROM Donors ORDER BY name"
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error fetching donors: {e}")
            return []
    
    @staticmethod
    def add_donation_record(donor_id: int, hosp_id: int, date: str, amount: int,
                           recorded_by: str) -> Tuple[bool, str]:
        """Log a blood donation"""
        try:
            donor_valid, donor_err = InputValidator.validate_integer(donor_id, 1, field_name="Donor ID")
            if not donor_valid:
                return False, donor_err
            
            hosp_valid, hosp_err = InputValidator.validate_integer(hosp_id, 1, field_name="Hospital ID")
            if not hosp_valid:
                return False, hosp_err
            
            amount_valid, amount_err = InputValidator.validate_integer(amount, 50, 500, "Donation amount (ml)")
            if not amount_valid:
                return False, amount_err
            
            query = """
                INSERT INTO donation_records (donor_id, hospital_id, date, amount)
                VALUES (?, ?, ?, ?)
            """
            execute_raw_query(query, (donor_id, hosp_id, date, amount))
            
            audit_logger.log_action(recorded_by, "LOG_DONATION", f"Donor_{donor_id}", "SUCCESS",
                                   f"Amount_{amount}ml, Hosp_{hosp_id}")
            logger.info(f"Donation logged - Donor: {donor_id}, Amount: {amount}ml")
            return True, f"✅ Donation logged: {amount}ml"
            
        except Exception as e:
            logger.error(f"Error logging donation: {e}")
            db_logger.log_error("INSERT", "Donation_Records", str(e), recorded_by)
            return False, f"Error logging donation: {str(e)}"
    
    @staticmethod
    def get_all_donations() -> List[Tuple]:
        """Get all donation records"""
        try:
            query = """
                SELECT donation_id, donor_id, hospital_id, date, amount
                FROM donation_records
                ORDER BY date DESC
            """
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error fetching donations: {e}")
            return []
    
    @staticmethod
    def delete_donation_record(donation_id: int, deleted_by: str) -> Tuple[bool, str]:
        """Delete a donation record"""
        try:
            query = "DELETE FROM donation_records WHERE donation_id = ?"
            execute_raw_query(query, (donation_id,))
            
            audit_logger.log_action(deleted_by, "DELETE_DONATION", f"DonationID_{donation_id}", "SUCCESS", "")
            logger.info(f"Donation record deleted: {donation_id}")
            return True, f"✅ Donation record deleted"
            
        except Exception as e:
            logger.error(f"Error deleting donation: {e}")
            db_logger.log_error("DELETE", "Donation_Records", str(e), deleted_by)
            return False, f"Error deleting donation: {str(e)}"
    
    @staticmethod
    def update_donation_amount(donation_id: int, new_amount: int, updated_by: str) -> Tuple[bool, str]:
        """Update donation amount"""
        try:
            amount_valid, amount_err = InputValidator.validate_integer(new_amount, 50, 500, "Donation amount (ml)")
            if not amount_valid:
                return False, amount_err
            
            query = "UPDATE donation_records SET amount = ? WHERE donation_id = ?"
            execute_raw_query(query, (new_amount, donation_id))
            
            audit_logger.log_action(updated_by, "UPDATE_DONATION", f"DonationID_{donation_id}", "SUCCESS", 
                                   f"NewAmount_{new_amount}ml")
            logger.info(f"Donation amount updated: {donation_id} -> {new_amount}ml")
            return True, f"✅ Donation amount updated to {new_amount}ml"
            
        except Exception as e:
            logger.error(f"Error updating donation: {e}")
            db_logger.log_error("UPDATE", "Donation_Records", str(e), updated_by)
            return False, f"Error updating donation: {str(e)}"


# ==========================================
# REPOSITORY PATTERN - TRANSFERS
# ==========================================

class TransferRepository:
    """Handle all transfer request database operations"""
    
    @staticmethod
    def create_transfer_request(origin_id: int, dest_id: int, item_id: int, qty: int,
                               requested_by: str) -> Tuple[bool, str]:
        """Create new transfer request"""
        try:
            # Validate
            origin_valid, origin_err = InputValidator.validate_integer(origin_id, 1, field_name="Origin Hospital ID")
            if not origin_valid:
                return False, origin_err
            
            if origin_id == dest_id:
                return False, "Origin and destination hospitals cannot be the same"
            
            dest_valid, dest_err = InputValidator.validate_integer(dest_id, 1, field_name="Destination Hospital ID")
            if not dest_valid:
                return False, dest_err
            
            item_valid, item_err = InputValidator.validate_integer(item_id, 1, field_name="Item ID")
            if not item_valid:
                return False, item_err
            
            qty_valid, qty_err = InputValidator.validate_integer(qty, 1, field_name="Quantity")
            if not qty_valid:
                return False, qty_err
            
            query = """
                INSERT INTO transfer_requests (origin_hospital_id, dest_hospital_id, item_id, quantity)
                VALUES (?, ?, ?, ?)
            """
            execute_raw_query(query, (origin_id, dest_id, item_id, qty))
            
            audit_logger.log_action(requested_by, "CREATE_TRANSFER", f"From_H{origin_id}_to_H{dest_id}",
                                   "SUCCESS", f"Item_{item_id}, Qty_{qty}")
            logger.info(f"Transfer request created - From {origin_id} to {dest_id}, Item {item_id}, Qty {qty}")
            return True, f"✅ Transfer request created successfully"
            
        except Exception as e:
            logger.error(f"Error creating transfer: {e}")
            db_logger.log_error("INSERT", "Transfer_Requests", str(e), requested_by)
            return False, f"Error creating transfer: {str(e)}"
    
    @staticmethod
    def get_all_transfer_requests() -> List[Tuple]:
        """Get all active transfer requests"""
        try:
            query = """
                SELECT request_id, origin_hospital_id, dest_hospital_id, item_id, quantity
                FROM transfer_requests
                ORDER BY created_at DESC
            """
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error fetching transfer requests: {e}")
            return []
    
    @staticmethod
    def add_transfer_status(req_id: int, status: str, updated_by: str) -> Tuple[bool, str]:
        """
        Update transfer status with inventory management.
        When status is "Delivered", automatically transfers inventory.
        """
        try:
            req_valid, req_err = InputValidator.validate_integer(req_id, 1, field_name="Request ID")
            if not req_valid:
                return False, req_err
            
            status_valid, status_err = InputValidator.validate_transfer_status(status)
            if not status_valid:
                return False, status_err
            
            # Perform status update with inventory handling in a transaction
            operations = []
            
            # Add status log
            status_query = "INSERT INTO transfer_status (request_id, status) VALUES (?, ?)"
            operations.append((status_query, (req_id, status)))
            
            # If delivered, move inventory
            if status == "Delivered":
                # Get transfer details
                detail_query = """
                    SELECT origin_hospital_id, dest_hospital_id, item_id, quantity
                    FROM transfer_requests
                    WHERE request_id = ?
                """
                detail_result = execute_raw_query(detail_query, (req_id,), fetch_one=True)
                
                if detail_result:
                    origin_id, dest_id, item_id, qty = detail_result
                    
                    # Subtract from origin
                    subtract_query = """
                        UPDATE hospital_inventory
                        SET quantity = quantity - ?
                        WHERE hospital_id = ? AND item_id = ? AND quantity >= ?
                    """
                    operations.append((subtract_query, (qty, origin_id, item_id, qty)))
                    
                    # Add to destination
                    check_query = "SELECT inventory_id FROM hospital_inventory WHERE hospital_id = ? AND item_id = ?"
                    check_result = execute_raw_query(check_query, (dest_id, item_id), fetch_one=True)
                    
                    if check_result:
                        add_query = """
                            UPDATE hospital_inventory
                            SET quantity = quantity + ?
                            WHERE hospital_id = ? AND item_id = ?
                        """
                        operations.append((add_query, (qty, dest_id, item_id)))
                    else:
                        insert_query = """
                            INSERT INTO hospital_inventory (hospital_id, item_id, quantity, expiry_date)
                            VALUES (?, ?, ?, CURRENT_DATE)
                        """
                        operations.append((insert_query, (dest_id, item_id, qty)))
            
            # Execute transaction
            success = execute_with_transaction(operations, f"Update transfer {req_id} to {status}")
            
            if success:
                audit_logger.log_action(updated_by, "UPDATE_TRANSFER_STATUS", f"Req_{req_id}",
                                       "SUCCESS", f"Status_{status}")
                return True, f"✅ Transfer status updated to {status}"
            else:
                return False, "Failed to update transfer status"
                
        except Exception as e:
            logger.error(f"Error updating transfer status: {e}")
            db_logger.log_error("UPDATE", "Transfer_Status", str(e), updated_by)
            return False, f"Error updating status: {str(e)}"
    
    @staticmethod
    def delete_transfer_request(request_id: int, deleted_by: str) -> Tuple[bool, str]:
        """Delete a transfer request (only if not yet delivered)"""
        try:
            # Check if already delivered
            check_query = """
                SELECT MAX(status) FROM transfer_status
                WHERE request_id = ?
            """
            check_result = execute_raw_query(check_query, (request_id,), fetch_one=True)
            last_status = check_result[0] if check_result else None
            
            if last_status == "Delivered":
                return False, "Cannot delete a delivered transfer request"
            
            query = "DELETE FROM transfer_requests WHERE request_id = ?"
            execute_raw_query(query, (request_id,))
            
            audit_logger.log_action(deleted_by, "DELETE_TRANSFER", f"Req_{request_id}", "SUCCESS", "")
            logger.info(f"Transfer request deleted: {request_id}")
            return True, f"✅ Transfer request cancelled"
            
        except Exception as e:
            logger.error(f"Error deleting transfer: {e}")
            db_logger.log_error("DELETE", "Transfer_Requests", str(e), deleted_by)
            return False, f"Error cancelling transfer: {str(e)}"


# ==========================================
# REPORTS & ANALYTICS
# ==========================================

class ReportingRepository:
    """Handle all reporting and analytics queries"""
    
    @staticmethod
    def get_inventory_report() -> List[Tuple]:
        """Get comprehensive inventory report"""
        try:
            query = """
                SELECT
                    hi.inventory_id,
                    h.name as hospital_name,
                    ii.item_name,
                    ii.category,
                    hi.quantity,
                    hi.expiry_date
                FROM hospital_inventory hi
                JOIN hospitals h ON hi.hospital_id = h.hospital_id
                JOIN inventory_items ii ON hi.item_id = ii.item_id
                ORDER BY h.name, ii.item_name
            """
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error fetching inventory report: {e}")
            return []
    
    @staticmethod
    def get_transfer_history() -> List[Tuple]:
        """Get complete transfer history"""
        try:
            query = """
                SELECT
                    ts.status_id,
                    h1.name as origin,
                    h2.name as destination,
                    ii.item_name,
                    tr.quantity,
                    ts.status,
                    ts.timestamp
                FROM transfer_status ts
                JOIN transfer_requests tr ON ts.request_id = tr.request_id
                JOIN hospitals h1 ON tr.origin_hospital_id = h1.hospital_id
                JOIN hospitals h2 ON tr.dest_hospital_id = h2.hospital_id
                JOIN inventory_items ii ON tr.item_id = ii.item_id
                ORDER BY ts.timestamp DESC
            """
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error fetching transfer history: {e}")
            return []
    
    @staticmethod
    def get_audit_logs(limit: int = 1000) -> List[Tuple]:
        """Get audit trail logs"""
        try:
            query = """
                SELECT log_id, staff_id, action, table_affected, timestamp
                FROM audit_logs
                ORDER BY timestamp DESC
                LIMIT ?
            """
            result = execute_raw_query(query, (limit,))
            return result or []
        except Exception as e:
            logger.error(f"Error fetching audit logs: {e}")
            return []
    
    @staticmethod
    def get_donation_report() -> List[Tuple]:
        """Get donation statistics report"""
        try:
            query = """
                SELECT 
                    d.donor_id, d.name, d.blood_type,
                    COUNT(dr.donation_id) as total_donations,
                    SUM(dr.amount) as total_amount_ml,
                    MAX(dr.date) as last_donation_date
                FROM donors d
                LEFT JOIN donation_records dr ON d.donor_id = dr.donor_id
                GROUP BY d.donor_id, d.name, d.blood_type
                ORDER BY total_amount_ml DESC
            """
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error generating donation report: {e}")
            return []
    
    @staticmethod
    def get_blood_bank_summary() -> List[Tuple]:
        """Get blood bank inventory summary by hospital and blood type"""
        try:
            query = """
                SELECT 
                    h.hospital_id, h.name as hospital_name,
                    ii.item_name as blood_type,
                    SUM(hi.quantity) as total_units,
                    MIN(hi.expiry_date) as earliest_expiry,
                    MAX(hi.expiry_date) as latest_expiry
                FROM hospitals h
                LEFT JOIN hospital_inventory hi ON h.hospital_id = hi.hospital_id
                LEFT JOIN inventory_items ii ON hi.item_id = ii.item_id
                WHERE ii.category = 'Blood Products' OR hi.item_id IS NULL
                GROUP BY h.hospital_id, h.name, ii.item_name
                ORDER BY h.name, total_units DESC
            """
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error generating blood bank summary: {e}")
            return []
    
    @staticmethod
    def get_staff_report() -> List[Tuple]:
        """Get staff activity and access report"""
        try:
            query = """
                SELECT 
                    s.staff_id, s.username,
                    r.role_name as role,
                    h.name as hospital_name,
                    COUNT(al.log_id) as total_actions,
                    MAX(al.timestamp) as last_activity
                FROM staff s
                LEFT JOIN roles r ON s.role_id = r.role_id
                LEFT JOIN hospitals h ON s.hospital_id = h.hospital_id
                LEFT JOIN audit_logs al ON s.staff_id = al.staff_id
                GROUP BY s.staff_id, s.username, r.role_name, h.name
                ORDER BY last_activity DESC
            """
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error generating staff report: {e}")
            return []
    
    @staticmethod
    def get_logistics_impact() -> List[Tuple]:
        """Get logistics impact analysis - transfers by status"""
        try:
            query = """
                SELECT 
                    tr.request_id,
                    h1.name as origin_hospital,
                    h2.name as destination_hospital,
                    ii.item_name as resource,
                    tr.quantity,
                    ts.status,
                    ts.timestamp as status_update_time
                FROM transfer_requests tr
                LEFT JOIN transfer_status ts ON tr.request_id = ts.request_id
                LEFT JOIN hospitals h1 ON tr.origin_hospital_id = h1.hospital_id
                LEFT JOIN hospitals h2 ON tr.dest_hospital_id = h2.hospital_id
                LEFT JOIN inventory_items ii ON tr.item_id = ii.item_id
                ORDER BY ts.timestamp DESC
            """
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error generating logistics impact: {e}")
            return []
    
    @staticmethod
    def get_deep_audit_report() -> List[Tuple]:
        """Get comprehensive audit trail with context"""
        try:
            query = """
                SELECT 
                    al.log_id,
                    al.staff_id,
                    al.action,
                    al.table_affected,
                    al.timestamp
                FROM audit_logs al
                ORDER BY al.timestamp DESC
            """
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error generating deep audit report: {e}")
            return []
