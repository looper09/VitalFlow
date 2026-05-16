"""
VitalFlow Blood Bank Module - Production Ready
Implements donor eligibility, blood inventory management, and emergency overrides
Precisely follows business rules: > 90-day eligibility, 42-day expiration, admin-only overrides
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from db_manager import execute_raw_query, execute_with_transaction, get_db_connection, db_config
from security import InputValidator
from logger_config import logger, db_logger, audit_logger

# ==========================================
# DATA CLASSES - BLOOD BANK
# ==========================================

@dataclass
class BloodUnit:
    """Blood unit entity"""
    blood_id: int
    hospital_id: int
    blood_type: str  # A+, A-, B+, B-, AB+, AB-, O+, O-
    quantity_ml: int  # raw ml amounts
    expiry_date: str  # YYYY-MM-DD
    received_date: str
    status: str  # 'Active', 'Expired', 'Used'


# ==========================================
# BLOOD BANK REPOSITORY
# ==========================================

class BloodBankRepository:
    """
    Dedicated Blood Bank Management
    Handles blood-specific inventory separate from general medical supplies
    """
    
    BLOOD_TYPES = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
    BLOOD_EXPIRY_DAYS = 42  # CPDA-1 standard shelf life
    DONATION_COOLDOWN_DAYS = 90  # > 90 days minimum
    MIN_DONATION_ML = 420  # Minimum for one unit
    STANDARD_UNIT_ML = 450  # Standard blood unit size
    
    @staticmethod
    def add_blood_stock(hospital_id: int, blood_type: str, quantity_ml: int, 
                       received_date: str, received_by: str) -> Tuple[bool, str, Optional[int]]:
        """
        Add blood stock to a hospital's blood bank.
        
        Args:
            hospital_id: Hospital receiving blood
            blood_type: Blood type (A+, A-, etc.)
            quantity_ml: Amount in milliliters
            received_date: Date received (YYYY-MM-DD)
            received_by: Staff member recording entry
            
        Returns:
            Tuple of (success: bool, message: str, blood_id: Optional[int])
        """
        # Validation
        if blood_type not in BloodBankRepository.BLOOD_TYPES:
            return False, f"Invalid blood type: {blood_type}", None
        
        qty_valid, qty_err = InputValidator.validate_integer(quantity_ml, 50, 50000, "Blood quantity (ml)")
        if not qty_valid:
            return False, qty_err, None
        
        conn = None
        try:
            expiry_date = (datetime.strptime(received_date, '%Y-%m-%d') + 
                          timedelta(days=BloodBankRepository.BLOOD_EXPIRY_DAYS)).strftime('%Y-%m-%d')
            conn = get_db_connection()
            if conn is None:
                return False, "Error adding blood: database connection unavailable", None

            cur = conn.cursor()
            query = """
                INSERT INTO Blood_Bank (hospital_id, blood_type, quantity_ml, received_date, expiry_date, status)
                VALUES (%s, %s, %s, %s, %s, 'Active')
                RETURNING blood_id
            """
            cur.execute(query, (hospital_id, blood_type, quantity_ml, received_date, expiry_date))
            row = cur.fetchone()
            blood_id = row[0] if row else None

            conn.commit()
            cur.close()
            
            audit_logger.log_action(received_by, "ADD_BLOOD_STOCK", 
                                   f"Hospital_{hospital_id}", "SUCCESS",
                                   f"BloodType_{blood_type}, Qty_{quantity_ml}ml, Expires_{expiry_date}")
            logger.info(f"Blood stock added: {blood_type} {quantity_ml}ml to Hospital {hospital_id}")
            
            return True, f"✅ {quantity_ml}ml of {blood_type} blood added (Expires: {expiry_date})", blood_id
            
        except Exception as e:
            logger.error(f"Error adding blood stock: {e}")
            db_logger.log_error("INSERT", "Blood_Bank", str(e), received_by)
            return False, f"Error adding blood: {str(e)}", None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    @staticmethod
    def get_blood_by_hospital(hospital_id: int, blood_type: Optional[str] = None, 
                             active_only: bool = True) -> List[Tuple]:
        """
        Get blood inventory for a hospital.
        
        Args:
            hospital_id: Hospital to query
            blood_type: Optional blood type filter (A+, etc.)
            active_only: Only return non-expired blood
            
        Returns:
            List of (blood_id, hospital_id, blood_type, quantity_ml, expiry_date, status)
        """
        try:
            where_clause = "WHERE hospital_id = ?"
            params = [hospital_id]
            
            if blood_type:
                where_clause += " AND blood_type = ?"
                params.append(blood_type)
            
            if active_only:
                today = datetime.now().date().isoformat()
                where_clause += " AND status = 'Active' AND expiry_date > ?"
                params.append(today)
            
            query = f"""
                SELECT blood_id, hospital_id, blood_type, quantity_ml, expiry_date, status
                FROM Blood_Bank {where_clause}
                ORDER BY expiry_date ASC
            """
            
            result = execute_raw_query(query, tuple(params))
            return result or []
            
        except Exception as e:
            logger.error(f"Error fetching blood by hospital: {e}")
            return []
    
    @staticmethod
    def consume_blood(blood_id: int, quantity_ml: int, consumed_by: str) -> Tuple[bool, str]:
        """
        Consume blood units (transfusion, testing, etc.).
        Uses atomic SQL UPDATE to prevent race conditions.
        
        Args:
            blood_id: Blood unit to consume from
            quantity_ml: Amount to consume (ml)
            consumed_by: Staff member consuming blood
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            qty_valid, qty_err = InputValidator.validate_integer(quantity_ml, 1, 50000, "Consumption amount")
            if not qty_valid:
                return False, qty_err
            
            # ATOMIC UPDATE: Decrement quantity in single operation
            # This prevents race conditions where two concurrent updates could both see old value
            update_query = """
                UPDATE Blood_Bank 
                SET quantity_ml = quantity_ml - %s
                WHERE blood_id = %s AND quantity_ml >= %s
                RETURNING blood_type, hospital_id, quantity_ml
            """
            result = execute_raw_query(update_query, (quantity_ml, blood_id, quantity_ml), fetch_one=True)
            
            if not result:
                # Either blood_id doesn't exist or insufficient quantity
                check_query = "SELECT quantity_ml, blood_type FROM Blood_Bank WHERE blood_id = ?"
                check_result = execute_raw_query(check_query, (blood_id,), fetch_one=True)
                
                if not check_result:
                    return False, "Blood unit not found"
                
                current_qty, blood_type = check_result
                return False, f"Insufficient blood. Available: {current_qty}ml, Requested: {quantity_ml}ml"
            
            blood_type, hosp_id, new_qty = result
            
            # If fully consumed, update status to 'Used'
            if new_qty == 0:
                status_query = "UPDATE Blood_Bank SET status = 'Used' WHERE blood_id = ?"
                execute_raw_query(status_query, (blood_id,))
            
            audit_logger.log_action(consumed_by, "CONSUME_BLOOD", f"BloodID_{blood_id}", "SUCCESS",
                                   f"BloodType_{blood_type}, Qty_{quantity_ml}ml, Remaining_{new_qty}ml")
            logger.info(f"Blood consumed: {blood_type} {quantity_ml}ml from unit {blood_id}")
            
            return True, f"✅ {quantity_ml}ml {blood_type} blood consumed. Remaining: {new_qty}ml"
            
        except Exception as e:
            logger.error(f"Error consuming blood: {e}")
            db_logger.log_error("UPDATE", "Blood_Bank", str(e), consumed_by)
            return False, f"Error consuming blood: {str(e)}"
    
    @staticmethod
    def get_all_blood_stock() -> List[Tuple]:
        """Get all blood stock across all hospitals"""
        try:
            query = """
                SELECT blood_id, hospital_id, blood_type, quantity_ml, expiry_date, status
                FROM Blood_Bank
                ORDER BY expiry_date ASC, blood_type
            """
            result = execute_raw_query(query)
            return result or []
        except Exception as e:
            logger.error(f"Error fetching all blood stock: {e}")
            return []
    
    @staticmethod
    def check_expiry_and_mark() -> Tuple[int, int]:
        """
        Check for expired blood and mark as expired.
        Uses atomic UPDATE to mark all expired blood in single operation.
        Called periodically to maintain data integrity.
        
        Returns:
            Tuple of (total_blood_units, expired_count)
        """
        try:
            today = datetime.now().date().isoformat()
            
            # ATOMIC: Mark all expired blood in one operation
            update_query = """
                UPDATE Blood_Bank
                SET status = 'Expired'
                WHERE status = 'Active' AND expiry_date < %s
            """
            execute_raw_query(update_query, (today,))
            
            # Count total and expired
            count_query = "SELECT COUNT(*) FROM Blood_Bank WHERE status = 'Active'"
            count_result = execute_raw_query(count_query, fetch_one=True)
            total_count = count_result[0] if count_result else 0
            
            expired_query = "SELECT COUNT(*) FROM Blood_Bank WHERE status = 'Expired'"
            expired_result = execute_raw_query(expired_query, fetch_one=True)
            expired_count = expired_result[0] if expired_result else 0
            
            if expired_count > 0:
                audit_logger.log_action("System", "AUTO_EXPIRE_BLOOD", "Blood_Bank", "SUCCESS",
                                       f"Expired_Units_{expired_count}")
                logger.warning(f"Auto-expired {expired_count} blood units")
            
            return total_count + expired_count, expired_count
            
        except Exception as e:
            logger.error(f"Error checking expiry: {e}")
            return 0, 0


# ==========================================
# DONOR ELIGIBILITY MODULE
# ==========================================

class DonorEligibilityManager:
    """
    Manages donor eligibility and donation history
    Implements 90-day cooldown with emergency override capability
    """
    
    COOLDOWN_DAYS = 90  # Must wait > 90 days (donate on day 91)
    
    @staticmethod
    def check_donor_eligibility(donor_id: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if donor is eligible to donate.
        Business Rule: Donation allowed on Day 91. Cooldown is > 90 days.
        
        Args:
            donor_id: Donor to check
            
        Returns:
            Tuple of (is_eligible: bool, details: Dict with eligibility info)
        """
        try:
            # Get donor's last donation date (from updated Donors table)
            query = """
                SELECT 
                    donor_id, name, blood_type, last_donation_date
                FROM Donors
                WHERE donor_id = ?
            """
            result = execute_raw_query(query, (donor_id,), fetch_one=True)
            
            if not result:
                return False, {"error": "Donor not found"}
            
            donor_id_result, name, blood_type, last_donation_date = result
            
            # NULL = eligible to donate (first time or no record)
            if not last_donation_date:
                return True, {
                    "donor_id": donor_id_result,
                    "name": name,
                    "blood_type": blood_type,
                    "eligible": True,
                    "days_remaining": 0,
                    "last_donation": None,
                    "reason": "First donation or no previous record"
                }
            
            # Parse date and calculate cooldown
            last_date = datetime.strptime(last_donation_date, '%Y-%m-%d')
            next_eligible_date = last_date + timedelta(days=DonorEligibilityManager.COOLDOWN_DAYS + 1)
            days_remaining = (next_eligible_date - datetime.now()).days
            
            is_eligible = days_remaining <= 0
            
            return is_eligible, {
                "donor_id": donor_id_result,
                "name": name,
                "blood_type": blood_type,
                "eligible": is_eligible,
                "last_donation": last_donation_date,
                "days_remaining": max(0, days_remaining),
                "next_eligible_date": next_eligible_date.strftime('%Y-%m-%d') if not is_eligible else None,
                "reason": "Eligible to donate" if is_eligible else f"Re-eligible in {days_remaining} days"
            }
            
        except Exception as e:
            logger.error(f"Error checking donor eligibility: {e}")
            return False, {"error": str(e)}
    
    @staticmethod
    def override_donation_eligibility(donor_id: int, override_reason: str, 
                                      staff_id: int) -> Tuple[bool, str]:
        """
        ADMIN ONLY: Override eligibility for emergency transfusions.
        Requires System Administrator role (Role_ID = 1). Logs to audit trail.
        
        Args:
            donor_id: Donor to override for
            override_reason: Clinical reason for override (stored in audit)
            staff_id: Staff member approving override
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Check if staff member is System Administrator (Role_ID = 1)
            role_query = "SELECT Role_ID FROM Staff WHERE Staff_ID = ?"
            role_result = execute_raw_query(role_query, (staff_id,), fetch_one=True)
            
            if not role_result or role_result[0] != 1:  # 1 = System Administrator
                audit_logger.log_action(f"Staff_{staff_id}", "UNAUTHORIZED_OVERRIDE_ATTEMPT", 
                                       f"Donor_{donor_id}", "FAILED", "Insufficient privileges")
                return False, "❌ Only System Administrators can override eligibility"
            
            # Log the override with clinical justification
            audit_logger.log_action(f"Staff_{staff_id}", "EMERGENCY_DONATION_OVERRIDE",
                                   f"Donor_{donor_id}", "SUCCESS",
                                   f"Reason: {override_reason}")
            
            logger.warning(f"OVERRIDE: Donor {donor_id} eligibility overridden by Staff {staff_id}. Reason: {override_reason}")
            
            return True, f"✅ Emergency override approved for Donor {donor_id}. Logged to audit trail."
            
        except Exception as e:
            logger.error(f"Error processing override: {e}")
            return False, f"Error processing override: {str(e)}"
    
    @staticmethod
    def record_donation_completed(donor_id: int, hospital_id: int, amount_ml: int, 
                                 donation_date: str, recorded_by: str) -> Tuple[bool, str]:
        """
        Record completion of donation and update last_donation_date.
        
        Args:
            donor_id: Donor who donated
            hospital_id: Hospital receiving donation
            amount_ml: Amount in ml
            donation_date: Date of donation (YYYY-MM-DD)
            recorded_by: Staff member recording
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Add to Donation_Records
            donation_query = """
                INSERT INTO Donation_Records (Donor_ID, Hospital_ID, Date, Amount)
                VALUES (?, ?, ?, ?)
            """
            execute_raw_query(donation_query, (donor_id, hospital_id, donation_date, amount_ml))
            
            # Update Donors.last_donation_date
            update_query = "UPDATE Donors SET last_donation_date = ? WHERE Donor_ID = ?"
            execute_raw_query(update_query, (donation_date, donor_id))
            
            audit_logger.log_action(recorded_by, "DONATION_COMPLETED", f"Donor_{donor_id}", "SUCCESS",
                                   f"Amount_{amount_ml}ml, Hospital_{hospital_id}, Date_{donation_date}")
            
            logger.info(f"Donation recorded: Donor {donor_id}, {amount_ml}ml to Hospital {hospital_id}")
            
            return True, f"✅ Donation recorded ({amount_ml}ml). Next eligible: {donation_date} + 91 days"
            
        except Exception as e:
            logger.error(f"Error recording donation: {e}")
            return False, f"Error recording donation: {str(e)}"


# ==========================================
# BLOOD BANK REPORTING
# ==========================================

class BloodBankReporting:
    """Specialized reporting for blood bank operations"""
    
    @staticmethod
    def get_blood_bank_summary_by_type() -> List[Tuple]:
        """Get blood bank inventory sorted by blood type and expiry"""
        try:
            today = datetime.now().date().isoformat()
            query = """
                SELECT 
                    blood_type,
                    COUNT(*) as unit_count,
                    SUM(quantity_ml) as total_ml,
                    MIN(expiry_date) as earliest_expiry,
                    MAX(expiry_date) as latest_expiry,
                    SUM(CASE WHEN status = 'Active' AND expiry_date > ? THEN 1 ELSE 0 END) as active_units
                FROM Blood_Bank
                GROUP BY blood_type
                ORDER BY blood_type
            """
            result = execute_raw_query(query, (today,))
            return result or []
        except Exception as e:
            logger.error(f"Error generating blood bank summary: {e}")
            return []
    
    @staticmethod
    def get_blood_by_hospital_summary(hospital_id: int) -> List[Tuple]:
        """Get blood inventory at specific hospital with expiry warnings"""
        try:
            today = datetime.now().date().isoformat()
            soon_date = (datetime.now().date() + timedelta(days=7)).isoformat()
            query = """
                SELECT 
                    blood_type,
                    COUNT(*) as unit_count,
                    SUM(quantity_ml) as total_ml,
                    COUNT(CASE WHEN expiry_date <= ? THEN 1 END) as expired_units,
                    COUNT(CASE WHEN expiry_date <= ? AND expiry_date > ? THEN 1 END) as expiring_soon_units,
                    MIN(expiry_date) as earliest_expiry
                FROM Blood_Bank
                WHERE hospital_id = ? AND status != 'Used'
                GROUP BY blood_type
                ORDER BY earliest_expiry ASC
            """
            result = execute_raw_query(query, (today, soon_date, today, hospital_id))
            return result or []
        except Exception as e:
            logger.error(f"Error generating hospital blood summary: {e}")
            return []
    
    @staticmethod
    def get_donor_eligibility_report() -> List[Tuple]:
        """Get report of all donors with eligibility status"""
        try:
            query = """
                SELECT 
                    donor_id,
                    name,
                    blood_type,
                    last_donation_date
                FROM Donors
                ORDER BY name
            """
            rows = execute_raw_query(query) or []
            today = datetime.now().date()
            cutoff = today - timedelta(days=91)
            report = []

            for donor_id, name, blood_type, last_donation_date in rows:
                if last_donation_date is None:
                    eligibility_status = "ELIGIBLE_FIRST_TIME"
                    days_since_last = "N/A"
                else:
                    try:
                        last_date = datetime.strptime(str(last_donation_date), "%Y-%m-%d").date()
                        eligibility_status = "ELIGIBLE" if last_date <= cutoff else "INELIGIBLE"
                        days_since_last = str((today - last_date).days)
                    except Exception:
                        eligibility_status = "UNKNOWN"
                        days_since_last = "N/A"

                report.append((donor_id, name, blood_type, last_donation_date, eligibility_status, days_since_last))

            return report
        except Exception as e:
            logger.error(f"Error generating eligibility report: {e}")
            return []
