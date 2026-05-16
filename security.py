"""
Security Module: Password Hashing, Input Validation, and Authentication
Provides cryptographic security and data validation for VitalFlow
"""

import bcrypt
import re
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PasswordSecurity:
    """Handles password hashing and verification using bcrypt"""
    
    SALT_ROUNDS = 12  # Industry standard security level
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plaintext password securely using bcrypt.
        
        Args:
            password: Plaintext password to hash
            
        Returns:
            Hashed password string (can be stored in database)
            
        Raises:
            ValueError: If password is invalid or too short
        """
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        try:
            salt = bcrypt.gensalt(rounds=PasswordSecurity.SALT_ROUNDS)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise ValueError("Failed to hash password")
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a plaintext password against a stored hash.
        
        Args:
            password: Plaintext password to verify
            hashed: Stored hash from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8') if isinstance(hashed, str) else hashed
            )
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False


class InputValidator:
    """Comprehensive input validation for medical data"""
    
    # Blood types allowed in system
    VALID_BLOOD_TYPES = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
    
    # Transfer statuses
    VALID_TRANSFER_STATUSES = {'Pending', 'In Transit', 'Delivered', 'Cancelled'}
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username format (3-20 chars, alphanumeric + underscore).
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 20:
            return False, "Username must not exceed 20 characters"
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            return False, "Username can only contain letters, numbers, and underscores"
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not password:
            return False, "Password cannot be empty"
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        if len(password) > 128:
            return False, "Password must not exceed 128 characters"
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number (basic format: digits, spaces, dashes)"""
        if not phone:
            return False, "Phone number cannot be empty"
        cleaned = re.sub(r'[^\d+\-]', '', phone)
        if len(cleaned) < 10:
            return False, "Phone number must have at least 10 digits"
        if len(cleaned) > 15:
            return False, "Phone number too long"
        return True, ""
    
    @staticmethod
    def validate_blood_type(blood_type: str) -> Tuple[bool, str]:
        """Validate blood type against allowed values"""
        if blood_type not in InputValidator.VALID_BLOOD_TYPES:
            return False, f"Invalid blood type. Must be one of: {', '.join(sorted(InputValidator.VALID_BLOOD_TYPES))}"
        return True, ""
    
    @staticmethod
    def validate_integer(value: any, min_val: int = None, max_val: int = None, 
                         field_name: str = "Value") -> Tuple[bool, str]:
        """
        Validate integer within range.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed (inclusive)
            max_val: Maximum allowed (inclusive)
            field_name: Name of field for error messages
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                return False, f"{field_name} cannot be less than {min_val}"
            if max_val is not None and num > max_val:
                return False, f"{field_name} cannot exceed {max_val}"
            return True, ""
        except (ValueError, TypeError):
            return False, f"{field_name} must be a valid integer"
    
    @staticmethod
    def validate_text(text: str, min_length: int = 1, max_length: int = 255,
                      field_name: str = "Text", allow_empty: bool = False) -> Tuple[bool, str]:
        """
        Validate text string length.
        
        Args:
            text: Text to validate
            min_length: Minimum length
            max_length: Maximum length
            field_name: Name of field for errors
            allow_empty: Whether empty string is allowed
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not text:
            if allow_empty:
                return True, ""
            return False, f"{field_name} cannot be empty"
        
        if len(text) < min_length:
            return False, f"{field_name} must be at least {min_length} characters"
        if len(text) > max_length:
            return False, f"{field_name} cannot exceed {max_length} characters"
        
        # Check for SQL injection and XSS patterns
        dangerous_patterns = [
            # SQL injection patterns
            ';', '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute', 
            'union', 'select', 'drop', 'delete', 'insert', 'update',
            # SQL injection quote patterns
            "' or ", "' and ", '=', 
            # XSS patterns
            '<script', 'javascript:', 'onerror=', 'onload=', 'onclick=', 
            '<iframe', '<img', 'src=', 'href='
        ]
        text_lower = text.lower()
        for pattern in dangerous_patterns:
            if pattern in text_lower:
                logger.warning(f"Potentially dangerous pattern detected in {field_name}: {pattern}")
                return False, f"{field_name} contains invalid characters or patterns"
        
        return True, ""
    
    @staticmethod
    def validate_transfer_status(status: str) -> Tuple[bool, str]:
        """Validate transfer status"""
        if status not in InputValidator.VALID_TRANSFER_STATUSES:
            return False, f"Invalid status. Must be one of: {', '.join(InputValidator.VALID_TRANSFER_STATUSES)}"
        return True, ""
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 255) -> str:
        """
        Sanitize a string by removing/escaping dangerous characters.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not text:
            return ""
        
        # Truncate to max length
        text = text[:max_length]
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text


class AuthenticationHelper:
    """Helper functions for authentication workflows"""
    
    @staticmethod
    def validate_credentials(username: str, password: str) -> Tuple[bool, str]:
        """
        Comprehensive credential validation before authentication.
        
        Args:
            username: Username to validate
            password: Password to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        user_valid, user_err = InputValidator.validate_username(username)
        if not user_valid:
            return False, user_err
        
        pwd_valid, pwd_err = InputValidator.validate_password(password)
        if not pwd_valid:
            return False, pwd_err
        
        return True, ""
    
    @staticmethod
    def hash_password_for_storage(password: str) -> Optional[str]:
        """
        Hash password for storage in database.
        Returns None if validation fails.
        """
        pwd_valid, pwd_err = InputValidator.validate_password(password)
        if not pwd_valid:
            logger.error(f"Password validation failed: {pwd_err}")
            return None
        
        try:
            return PasswordSecurity.hash_password(password)
        except ValueError as e:
            logger.error(f"Password hashing failed: {e}")
            return None
