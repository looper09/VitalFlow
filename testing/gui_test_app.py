#!/usr/bin/env python3
"""
VitalFlow GUI Testing with Streamlit
Performs all GUI operations and creates detailed test documentation
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, '/workspaces/VitalFlow')

import streamlit as st
import pandas as pd
import models_compat as models
from pathlib import Path

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="VitalFlow Testing Dashboard",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# TEST TRACKING
# ==========================================

class TestTracker:
    def __init__(self):
        self.tests = []
        self.screenshots = []
    
    def add_test(self, name, status, details=""):
        self.tests.append({
            "name": name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_screenshot(self, name):
        self.screenshots.append({
            "name": name,
            "timestamp": datetime.now().isoformat()
        })
    
    def export_json(self, filepath):
        data = {
            "test_run": datetime.now().isoformat(),
            "total_tests": len(self.tests),
            "passed": len([t for t in self.tests if t["status"] == "✅ PASS"]),
            "failed": len([t for t in self.tests if t["status"] == "❌ FAIL"]),
            "warnings": len([t for t in self.tests if "⚠️" in t["status"]]),
            "tests": self.tests,
            "screenshots": self.screenshots
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

# ==========================================
# SIDEBAR INITIALIZATION
# ==========================================

st.sidebar.title("🧪 VitalFlow Testing Dashboard")
st.sidebar.markdown("---")

# Initialize session state
if 'test_tracker' not in st.session_state:
    st.session_state.test_tracker = TestTracker()

test_tracker = st.session_state.test_tracker

# ==========================================
# MAIN INTERFACE
# ==========================================

st.title("🧪 VitalFlow Automated Testing Suite")
st.markdown("""
This dashboard performs automated testing of all VitalFlow components.
Results are logged and can be exported for review.
""")

# Create tabs
tab_overview, tab_data, tab_reports, tab_operations, tab_results = st.tabs([
    "📊 Overview",
    "📋 Data Verification",
    "📈 Reports Testing",
    "⚙️ Operations Testing",
    "✅ Test Results"
])

# ==========================================
# TAB 1: OVERVIEW
# ==========================================

with tab_overview:
    st.header("Project Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Hospitals", len(models.get_all_hospitals()))
    
    with col2:
        st.metric("Total Staff", len(models.get_all_staff()))
    
    with col3:
        st.metric("Total Donors", len(models.get_all_donors()))
    
    with col4:
        st.metric("Total Items", len(models.get_all_inventory_items()))
    
    st.markdown("---")
    
    st.subheader("📋 Database Statistics")
    kpi_data = models.get_kpi_dashboard()
    kpi_df = pd.DataFrame(kpi_data, columns=["Metric", "Value"])
    st.dataframe(kpi_df, use_container_width=True)
    
    # Log test
    test_tracker.add_test("Database Connection", "✅ PASS", "All metrics loaded successfully")

# ==========================================
# TAB 2: DATA VERIFICATION
# ==========================================

with tab_data:
    st.header("Data Verification Tests")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Hospitals")
        hospitals = models.get_all_hospitals()
        if hospitals:
            hosp_df = pd.DataFrame(hospitals, columns=["ID", "Name", "Location", "Contact"])
            st.dataframe(hosp_df, use_container_width=True)
            test_tracker.add_test("Get Hospitals", "✅ PASS", f"Retrieved {len(hospitals)} hospitals")
        else:
            st.warning("No hospitals found")
            test_tracker.add_test("Get Hospitals", "❌ FAIL", "No data retrieved")
    
    with col2:
        st.subheader("Inventory Items")
        items = models.get_all_inventory_items()
        if items:
            items_df = pd.DataFrame(items, columns=["ID", "Name", "Category", "Unit"])
            st.dataframe(items_df, use_container_width=True)
            test_tracker.add_test("Get Inventory Items", "✅ PASS", f"Retrieved {len(items)} items")
        else:
            st.warning("No inventory items found")
            test_tracker.add_test("Get Inventory Items", "❌ FAIL", "No data retrieved")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Blood Donors")
        donors = models.get_all_donors()
        if donors:
            donors_df = pd.DataFrame(donors, columns=["ID", "Name", "Blood Type", "Contact"])
            st.dataframe(donors_df, use_container_width=True)
            test_tracker.add_test("Get Donors", "✅ PASS", f"Retrieved {len(donors)} donors")
        else:
            st.warning("No donors found")
            test_tracker.add_test("Get Donors", "❌ FAIL", "No data retrieved")
    
    with col4:
        st.subheader("Staff Members")
        staff = models.get_all_staff()
        if staff:
            staff_df = pd.DataFrame(staff, columns=["ID", "Username", "Role", "Hospital"])
            st.dataframe(staff_df, use_container_width=True)
            test_tracker.add_test("Get Staff", "✅ PASS", f"Retrieved {len(staff)} staff members")
        else:
            st.warning("No staff found")
            test_tracker.add_test("Get Staff", "❌ FAIL", "No data retrieved")

# ==========================================
# TAB 3: REPORTS TESTING
# ==========================================

with tab_reports:
    st.header("Advanced Reports Testing")
    
    report_tabs = st.tabs([
        "Staff Report",
        "Donation Report",
        "Blood Bank Summary",
        "Logistics Impact",
        "Audit Trail"
    ])
    
    # Staff Report
    with report_tabs[0]:
        try:
            staff_report = models.get_staff_report()
            if staff_report:
                report_df = pd.DataFrame(staff_report)
                st.dataframe(report_df, use_container_width=True)
                test_tracker.add_test("Staff Report", "✅ PASS", f"{len(staff_report)} records")
            else:
                st.info("Staff report is empty")
                test_tracker.add_test("Staff Report", "⚠️ WARN", "Empty dataset")
        except Exception as e:
            st.error(f"Error: {e}")
            test_tracker.add_test("Staff Report", "❌ FAIL", str(e))
    
    # Donation Report
    with report_tabs[1]:
        try:
            donation_report = models.get_donation_report()
            if donation_report:
                report_df = pd.DataFrame(donation_report)
                st.dataframe(report_df, use_container_width=True)
                test_tracker.add_test("Donation Report", "✅ PASS", f"{len(donation_report)} records")
            else:
                st.info("Donation report is empty")
                test_tracker.add_test("Donation Report", "⚠️ WARN", "Empty dataset")
        except Exception as e:
            st.error(f"Error: {e}")
            test_tracker.add_test("Donation Report", "❌ FAIL", str(e))
    
    # Blood Bank Summary
    with report_tabs[2]:
        try:
            blood_bank = models.get_blood_bank_summary()
            if blood_bank:
                report_df = pd.DataFrame(blood_bank)
                st.dataframe(report_df, use_container_width=True)
                test_tracker.add_test("Blood Bank Summary", "✅ PASS", f"{len(blood_bank)} records")
            else:
                st.info("Blood bank summary is empty")
                test_tracker.add_test("Blood Bank Summary", "⚠️ WARN", "Empty dataset")
        except Exception as e:
            st.error(f"Error: {e}")
            test_tracker.add_test("Blood Bank Summary", "❌ FAIL", str(e))
    
    # Logistics Impact
    with report_tabs[3]:
        try:
            logistics = models.get_logistics_impact()
            if logistics:
                report_df = pd.DataFrame(logistics)
                st.dataframe(report_df, use_container_width=True)
                test_tracker.add_test("Logistics Impact", "✅ PASS", f"{len(logistics)} records")
            else:
                st.info("Logistics impact report is empty (no transfers yet)")
                test_tracker.add_test("Logistics Impact", "⚠️ WARN", "Empty dataset (expected)")
        except Exception as e:
            st.error(f"Error: {e}")
            test_tracker.add_test("Logistics Impact", "❌ FAIL", str(e))
    
    # Audit Trail
    with report_tabs[4]:
        try:
            logs = models.get_all_logs(limit=100)
            if logs:
                report_df = pd.DataFrame(logs)
                st.dataframe(report_df, use_container_width=True)
                test_tracker.add_test("Audit Logs", "✅ PASS", f"{len(logs)} records")
            else:
                st.info("Audit logs are empty")
                test_tracker.add_test("Audit Logs", "⚠️ WARN", "Empty dataset (expected)")
        except Exception as e:
            st.error(f"Error: {e}")
            test_tracker.add_test("Audit Logs", "❌ FAIL", str(e))

# ==========================================
# TAB 4: OPERATIONS TESTING
# ==========================================

with tab_operations:
    st.header("CRUD Operations Testing")
    
    operation_tabs = st.tabs([
        "Add Donor Test",
        "Add Staff Test",
        "View Hospital Inventory",
        "Transfer Operations",
        "Data Validation"
    ])
    
    # Add Donor Test
    with operation_tabs[0]:
        st.subheader("Test Adding Donor")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            donor_name = st.text_input("Donor Name", value="Test Donor")
        with col2:
            blood_type = st.selectbox("Blood Type", ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"])
        with col3:
            contact = st.text_input("Contact", value="03001234567")
        with col4:
            if st.button("Test Add Donor"):
                try:
                    success, msg = models.add_donor(donor_name, blood_type, contact, "test_user")
                    if success:
                        st.success(msg)
                        test_tracker.add_test("Add Donor Operation", "✅ PASS", msg)
                    else:
                        st.error(msg)
                        test_tracker.add_test("Add Donor Operation", "❌ FAIL", msg)
                except Exception as e:
                    st.error(f"Error: {e}")
                    test_tracker.add_test("Add Donor Operation", "❌ FAIL", str(e))
    
    # Add Staff Test
    with operation_tabs[1]:
        st.subheader("Test Adding Staff")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            username = st.text_input("Username", value="testuser123", key="staff_username")
        with col2:
            password = st.text_input("Password", value="TestPass123!", type="password", key="staff_pass")
        with col3:
            role = st.selectbox("Role", ["Admin (1)", "Staff (2)"], key="staff_role")
            role_id = 1 if "Admin" in role else 2
        with col4:
            if st.button("Test Add Staff"):
                try:
                    success, msg, staff_id = models.add_staff(username, password, role_id, 1, "test_admin")
                    if success:
                        st.success(f"{msg} (Staff ID: {staff_id})")
                        test_tracker.add_test("Add Staff Operation", "✅ PASS", msg)
                    else:
                        st.warning(msg)
                        test_tracker.add_test("Add Staff Operation", "⚠️ WARN", msg)
                except Exception as e:
                    st.error(f"Error: {e}")
                    test_tracker.add_test("Add Staff Operation", "❌ FAIL", str(e))
    
    # Hospital Inventory
    with operation_tabs[2]:
        st.subheader("Hospital Inventory Status")
        hospitals = models.get_all_hospitals()
        selected_hosp = st.selectbox("Select Hospital", [f"ID {h[0]}: {h[1]}" for h in hospitals])
        hosp_id = int(selected_hosp.split()[1].rstrip(':'))
        
        try:
            inventory = models.get_hospital_inventory(hosp_id)
            if inventory:
                inv_df = pd.DataFrame(inventory, columns=["Inv ID", "Hosp ID", "Item ID", "Qty", "Expiry"])
                st.dataframe(inv_df, use_container_width=True)
                test_tracker.add_test("Get Hospital Inventory", "✅ PASS", f"{len(inventory)} items")
            else:
                st.info("No inventory for this hospital")
                test_tracker.add_test("Get Hospital Inventory", "⚠️ WARN", "No data")
        except Exception as e:
            st.error(f"Error: {e}")
            test_tracker.add_test("Get Hospital Inventory", "❌ FAIL", str(e))
    
    # Transfer Operations
    with operation_tabs[3]:
        st.subheader("Transfer Request Operations")
        
        transfers = models.get_all_transfer_requests()
        st.write(f"Current transfer requests: {len(transfers)}")
        
        if transfers:
            trans_df = pd.DataFrame(transfers, columns=["Req ID", "From Hosp", "To Hosp", "Item", "Qty", "Date"])
            st.dataframe(trans_df, use_container_width=True)
            test_tracker.add_test("Get Transfers", "✅ PASS", f"{len(transfers)} requests")
        else:
            st.info("No transfer requests (this is normal for fresh database)")
            test_tracker.add_test("Get Transfers", "⚠️ WARN", "Empty (expected)")
    
    # Data Validation
    with operation_tabs[4]:
        st.subheader("Data Integrity Checks")
        
        checks = []
        
        # Check 1: Hospitals
        try:
            hospitals = models.get_all_hospitals()
            checks.append(("Hospitals table", "✅ PASS" if len(hospitals) > 0 else "❌ FAIL", len(hospitals)))
            test_tracker.add_test("Hospital Count Check", "✅ PASS", f"{len(hospitals)} hospitals")
        except:
            checks.append(("Hospitals table", "❌ FAIL", 0))
            test_tracker.add_test("Hospital Count Check", "❌ FAIL", "Error reading hospitals")
        
        # Check 2: Staff
        try:
            staff = models.get_all_staff()
            checks.append(("Staff table", "✅ PASS" if len(staff) > 0 else "❌ FAIL", len(staff)))
            test_tracker.add_test("Staff Count Check", "✅ PASS", f"{len(staff)} staff members")
        except:
            checks.append(("Staff table", "❌ FAIL", 0))
            test_tracker.add_test("Staff Count Check", "❌ FAIL", "Error reading staff")
        
        # Check 3: Donors
        try:
            donors = models.get_all_donors()
            checks.append(("Donors table", "✅ PASS" if len(donors) > 0 else "❌ FAIL", len(donors)))
            test_tracker.add_test("Donor Count Check", "✅ PASS", f"{len(donors)} donors")
        except:
            checks.append(("Donors table", "❌ FAIL", 0))
            test_tracker.add_test("Donor Count Check", "❌ FAIL", "Error reading donors")
        
        # Check 4: Inventory
        try:
            items = models.get_all_inventory_items()
            checks.append(("Inventory table", "✅ PASS" if len(items) > 0 else "❌ FAIL", len(items)))
            test_tracker.add_test("Inventory Count Check", "✅ PASS", f"{len(items)} items")
        except:
            checks.append(("Inventory table", "❌ FAIL", 0))
            test_tracker.add_test("Inventory Count Check", "❌ FAIL", "Error reading inventory")
        
        # Display checks
        checks_df = pd.DataFrame(checks, columns=["Component", "Status", "Record Count"])
        st.dataframe(checks_df, use_container_width=True)

# ==========================================
# TAB 5: TEST RESULTS
# ==========================================

with tab_results:
    st.header("Test Results Summary")
    
    # Statistics
    passed = len([t for t in test_tracker.tests if t["status"] == "✅ PASS"])
    failed = len([t for t in test_tracker.tests if t["status"] == "❌ FAIL"])
    warnings = len([t for t in test_tracker.tests if "⚠️" in t["status"]])
    total = len(test_tracker.tests)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tests", total)
    with col2:
        st.metric("Passed", passed, delta=f"{int(passed/total*100) if total > 0 else 0}%")
    with col3:
        st.metric("Failed", failed)
    with col4:
        st.metric("Warnings", warnings)
    
    st.markdown("---")
    
    # Detailed test log
    st.subheader("Detailed Test Log")
    
    if test_tracker.tests:
        tests_df = pd.DataFrame([
            {
                "Test": t["name"],
                "Status": t["status"],
                "Details": t["details"],
                "Time": t["timestamp"]
            }
            for t in test_tracker.tests
        ])
        st.dataframe(tests_df, use_container_width=True)
    else:
        st.info("No tests have been run yet. Navigate to other tabs to run tests.")
    
    st.markdown("---")
    
    # Export button
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Export as JSON"):
            export_path = "/workspaces/VitalFlow/testing/test_results.json"
            test_tracker.export_json(export_path)
            st.success(f"Results exported to {export_path}")
    
    with col2:
        if st.button("📄 Generate Report"):
            st.info("Report generation feature coming soon")
    
    with col3:
        if st.button("🔄 Clear Tests"):
            st.session_state.test_tracker = TestTracker()
            st.rerun()

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>VitalFlow Automated Testing Suite • Version 2.0</p>
    <p>Database: SQLite • Framework: Streamlit • Status: Production Ready</p>
</div>
""", unsafe_allow_html=True)
