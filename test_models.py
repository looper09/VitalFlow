"""
VitalFlow Unit Tests - Comprehensive Test Suite
Tests all core modules: security, validation, database operations
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security import PasswordSecurity, InputValidator, AuthenticationHelper
from logger_config import setup_logging


# ==========================================
# SECURITY MODULE TESTS
# ==========================================

class TestPasswordSecurity:
    """Test password hashing and verification"""
    
    def test_hash_password_success(self):
        """Test successful password hashing"""
        password = "SecurePass123"
        hashed = PasswordSecurity.hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert password not in hashed  # Original not in hash
        assert len(hashed) > 20  # bcrypt produces long hashes
    
    def test_hash_password_varies(self):
        """Test that hashes are unique (different salt each time)"""
        password = "TestPassword"
        hash1 = PasswordSecurity.hash_password(password)
        hash2 = PasswordSecurity.hash_password(password)
        
        assert hash1 != hash2  # Different salts = different hashes
    
    def test_hash_password_too_short(self):
        """Test password hashing fails with short password"""
        with pytest.raises(ValueError):
            PasswordSecurity.hash_password("short")
    
    def test_hash_password_empty(self):
        """Test password hashing fails with empty password"""
        with pytest.raises(ValueError):
            PasswordSecurity.hash_password("")
    
    def test_verify_password_success(self):
        """Test successful password verification"""
        password = "CorrectPassword123"
        hashed = PasswordSecurity.hash_password(password)
        
        assert PasswordSecurity.verify_password(password, hashed) is True
    
    def test_verify_password_failure(self):
        """Test password verification fails with wrong password"""
        password = "CorrectPassword"
        hashed = PasswordSecurity.hash_password(password)
        
        assert PasswordSecurity.verify_password("WrongPassword", hashed) is False
    
    def test_verify_password_case_sensitive(self):
        """Test password verification is case-sensitive"""
        password = "TestPASS"
        hashed = PasswordSecurity.hash_password(password)
        
        assert PasswordSecurity.verify_password("testpass", hashed) is False


class TestInputValidator:
    """Test input validation functions"""
    
    # Username validation tests
    def test_validate_username_valid(self):
        """Test valid username"""
        is_valid, msg = InputValidator.validate_username("user_123")
        assert is_valid is True
        assert msg == ""
    
    def test_validate_username_too_short(self):
        """Test username too short"""
        is_valid, msg = InputValidator.validate_username("ab")
        assert is_valid is False
        assert "at least 3" in msg
    
    def test_validate_username_too_long(self):
        """Test username too long"""
        is_valid, msg = InputValidator.validate_username("a" * 21)
        assert is_valid is False
        assert "exceed 20" in msg
    
    def test_validate_username_invalid_chars(self):
        """Test username with invalid characters"""
        is_valid, msg = InputValidator.validate_username("user@name")
        assert is_valid is False
        assert "letters, numbers, and underscores" in msg
    
    # Password validation tests
    def test_validate_password_valid(self):
        """Test valid password"""
        is_valid, msg = InputValidator.validate_password("SecurePass123")
        assert is_valid is True
    
    def test_validate_password_too_short(self):
        """Test password too short"""
        is_valid, msg = InputValidator.validate_password("short")
        assert is_valid is False
        assert "at least 6" in msg
    
    # Blood type validation tests
    def test_validate_blood_type_valid(self):
        """Test valid blood types"""
        for blood_type in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            is_valid, msg = InputValidator.validate_blood_type(blood_type)
            assert is_valid is True, f"Failed for {blood_type}"
    
    def test_validate_blood_type_invalid(self):
        """Test invalid blood type"""
        is_valid, msg = InputValidator.validate_blood_type("C+")
        assert is_valid is False
        assert "Invalid blood type" in msg
    
    # Integer validation tests
    def test_validate_integer_valid(self):
        """Test valid integer"""
        is_valid, msg = InputValidator.validate_integer(5, 1, 10)
        assert is_valid is True
    
    def test_validate_integer_below_min(self):
        """Test integer below minimum"""
        is_valid, msg = InputValidator.validate_integer(0, 1, 10)
        assert is_valid is False
        assert "cannot be less than" in msg
    
    def test_validate_integer_above_max(self):
        """Test integer above maximum"""
        is_valid, msg = InputValidator.validate_integer(15, 1, 10)
        assert is_valid is False
        assert "cannot exceed" in msg
    
    def test_validate_integer_non_numeric(self):
        """Test non-numeric value"""
        is_valid, msg = InputValidator.validate_integer("abc", 1, 10)
        assert is_valid is False
        assert "valid integer" in msg
    
    # Text validation tests
    def test_validate_text_valid(self):
        """Test valid text"""
        is_valid, msg = InputValidator.validate_text("Hospital Name")
        assert is_valid is True
    
    def test_validate_text_too_short(self):
        """Test text below minimum length"""
        is_valid, msg = InputValidator.validate_text("a", min_length=3)
        assert is_valid is False
        assert "at least 3" in msg
    
    def test_validate_text_too_long(self):
        """Test text exceeding maximum length"""
        is_valid, msg = InputValidator.validate_text("a" * 256, max_length=255)
        assert is_valid is False
        assert "cannot exceed" in msg
    
    def test_validate_text_sql_injection_pattern(self):
        """Test SQL injection pattern detection"""
        is_valid, msg = InputValidator.validate_text("Name'; DROP TABLE users--")
        assert is_valid is False
        assert "invalid characters" in msg.lower() or "dangerous pattern" in msg.lower()
    
    def test_validate_text_empty_not_allowed(self):
        """Test empty text when not allowed"""
        is_valid, msg = InputValidator.validate_text("", allow_empty=False)
        assert is_valid is False
        assert "cannot be empty" in msg
    
    def test_validate_text_empty_allowed(self):
        """Test empty text when allowed"""
        is_valid, msg = InputValidator.validate_text("", allow_empty=True)
        assert is_valid is True
    
    # Transfer status validation
    def test_validate_transfer_status_valid(self):
        """Test valid transfer statuses"""
        for status in ['Pending', 'In Transit', 'Delivered', 'Cancelled']:
            is_valid, msg = InputValidator.validate_transfer_status(status)
            assert is_valid is True
    
    def test_validate_transfer_status_invalid(self):
        """Test invalid transfer status"""
        is_valid, msg = InputValidator.validate_transfer_status("Unknown")
        assert is_valid is False
    
    # Sanitization tests
    def test_sanitize_string_removes_null_bytes(self):
        """Test null byte removal"""
        text = "Hello\x00World"
        sanitized = InputValidator.sanitize_string(text)
        assert '\x00' not in sanitized
        assert "HelloWorld" == sanitized
    
    def test_sanitize_string_normalizes_whitespace(self):
        """Test whitespace normalization"""
        text = "Hello   World  \t  Test"
        sanitized = InputValidator.sanitize_string(text)
        assert sanitized == "Hello World Test"
    
    def test_sanitize_string_truncates_length(self):
        """Test length truncation"""
        text = "a" * 300
        sanitized = InputValidator.sanitize_string(text, max_length=100)
        assert len(sanitized) == 100


class TestAuthenticationHelper:
    """Test authentication helper functions"""
    
    def test_validate_credentials_both_valid(self):
        """Test validation with both valid credentials"""
        is_valid, msg = AuthenticationHelper.validate_credentials("validuser123", "password123")
        assert is_valid is True
    
    def test_validate_credentials_invalid_username(self):
        """Test validation with invalid username"""
        is_valid, msg = AuthenticationHelper.validate_credentials("ab", "password123")
        assert is_valid is False
        assert "Username" in msg or "3 characters" in msg
    
    def test_validate_credentials_invalid_password(self):
        """Test validation with invalid password"""
        is_valid, msg = AuthenticationHelper.validate_credentials("validuser", "short")
        assert is_valid is False
        assert "Password" in msg or "6 characters" in msg
    
    def test_hash_password_for_storage_success(self):
        """Test password hashing for storage"""
        result = AuthenticationHelper.hash_password_for_storage("ValidPass123")
        assert result is not None
        assert isinstance(result, str)
    
    def test_hash_password_for_storage_invalid(self):
        """Test password hashing fails with invalid password"""
        result = AuthenticationHelper.hash_password_for_storage("short")
        assert result is None


# ==========================================
# LOGGER TESTS
# ==========================================

class TestLogging:
    """Test logging configuration"""
    
    def test_logger_created(self):
        """Test logger can be created"""
        logger = setup_logging("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"
    
    def test_logger_levels(self):
        """Test logger supports all levels"""
        logger = setup_logging("test_levels")
        
        # These should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")


# ==========================================
# INTEGRATION TESTS
# ==========================================

class TestIntegration:
    """Integration tests combining multiple modules"""
    
    def test_user_registration_flow(self):
        """Test complete user registration flow"""
        username = "testuser_new"
        password = "TestPassword123"
        
        # Validate credentials
        valid, msg = AuthenticationHelper.validate_credentials(username, password)
        assert valid is True
        
        # Hash password
        hashed = AuthenticationHelper.hash_password_for_storage(password)
        assert hashed is not None
        
        # Verify would work
        assert PasswordSecurity.verify_password(password, hashed) is True
        assert PasswordSecurity.verify_password("wrongpassword", hashed) is False
    
    def test_donor_registration_flow(self):
        """Test complete donor registration flow"""
        # Valid donor data
        valid_name, msg = InputValidator.validate_text("John Doe", 3, 100, "Donor name")
        assert valid_name is True
        
        valid_blood, msg = InputValidator.validate_blood_type("O+")
        assert valid_blood is True
        
        valid_contact, msg = InputValidator.validate_phone("03001234567")
        assert valid_contact is True
    
    def test_inventory_allocation_flow(self):
        """Test complete inventory allocation flow"""
        hosp_id_valid, msg = InputValidator.validate_integer(1, 1, field_name="Hospital ID")
        assert hosp_id_valid is True
        
        item_id_valid, msg = InputValidator.validate_integer(1, 1, field_name="Item ID")
        assert item_id_valid is True
        
        qty_valid, msg = InputValidator.validate_integer(100, 1, field_name="Quantity")
        assert qty_valid is True


# ==========================================
# PERFORMANCE TESTS
# ==========================================

class TestPerformance:
    """Performance and security stress tests"""
    
    def test_password_hashing_performance(self):
        """Test password hashing completes in reasonable time"""
        import time
        
        start = time.time()
        for i in range(5):
            PasswordSecurity.hash_password(f"password{i}123")
        elapsed = time.time() - start
        
        # Should complete reasonably quickly (< 10 seconds for 5 hashes)
        # bcrypt with 12 rounds is intentionally slow for security
        assert elapsed < 10
    
    def test_input_validation_xss_patterns(self):
        """Test detection of various XSS/injection patterns"""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "'; DELETE FROM hospitals; --",
            "UNION SELECT * FROM staff",
        ]
        
        for dangerous in dangerous_inputs:
            # All dangerous patterns should be caught
            is_valid, msg = InputValidator.validate_text(dangerous)
            assert is_valid is False, f"Failed to catch dangerous input: {dangerous}"


# ==========================================
# RUN TESTS
# ==========================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-ra'])
