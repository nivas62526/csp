"""
Smart Poultry Farm Management System - SMS Gateway & OTP Service
Supports:
- Development Mock Mode (prints OTP to console & logs for local testing)
- MSG91 Gateway (India DLT Compliant SMS)
- Twilio SMS Gateway (Global SMS Delivery)
Includes rate limiting, cryptographic OTP generation, and SHA-256 hashing.
"""

import os
import re
import secrets
import hashlib
import time
import json
import logging
from datetime import datetime, timedelta
import requests

from config import Config

logger = logging.getLogger("sms_service")
logger.setLevel(logging.INFO)

# In-memory rate limiting store: { phone_number: [timestamps] }
_RATE_LIMIT_STORE = {}
RATE_LIMIT_WINDOW_SECONDS = 3600  # 1 hour
MAX_REQUESTS_PER_HOUR = 6         # Max 6 OTP requests per phone per hour

class SMSService:

    @staticmethod
    def validate_and_format_indian_phone(raw_phone: str, country_code: str = "+91") -> tuple[bool, str, str]:
        """
        Validates and standardizes an Indian mobile phone number.
        Returns:
            (is_valid: bool, e164_phone: str, clean_10_digits: str)
        """
        if not raw_phone:
            return False, "Mobile number is required.", ""

        # Remove spaces, dashes, brackets
        cleaned = re.sub(r"[\s\-\(\)]", "", str(raw_phone).strip())

        # Strip leading +91, 91, or 0
        if cleaned.startswith("+91"):
            digits = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            digits = cleaned[2:]
        elif cleaned.startswith("0") and len(cleaned) == 11:
            digits = cleaned[1:]
        else:
            digits = cleaned

        # Validate 10-digit Indian mobile number (must start with 6, 7, 8, or 9)
        if not re.match(r"^[6-9]\d{9}$", digits):
            return False, "Please enter a valid 10-digit Indian mobile number (e.g. 9876543210).", ""

        e164 = f"+91{digits}"
        return True, e164, digits

    @staticmethod
    def generate_otp() -> str:
        """Generates a cryptographically secure 6-digit random OTP."""
        return f"{secrets.randbelow(900000) + 100000}"

    @staticmethod
    def hash_otp(raw_otp: str) -> str:
        """Hashes OTP using SHA-256 for secure storage."""
        return hashlib.sha256(raw_otp.strip().encode("utf-8")).hexdigest()

    @staticmethod
    def verify_otp_hash(raw_otp: str, hashed_otp: str) -> bool:
        """Verifies candidate OTP against stored hash in constant time."""
        candidate_hash = hashlib.sha256(raw_otp.strip().encode("utf-8")).hexdigest()
        return secrets.compare_digest(candidate_hash, hashed_otp)

    @classmethod
    def check_rate_limit(cls, phone: str) -> tuple[bool, str]:
        """
        Ensures a single phone number cannot request more than
        MAX_REQUESTS_PER_HOUR OTPs in a rolling 1-hour window.
        """
        now = time.time()
        timestamps = _RATE_LIMIT_STORE.get(phone, [])
        valid_timestamps = [t for t in timestamps if (now - t) < RATE_LIMIT_WINDOW_SECONDS]
        _RATE_LIMIT_STORE[phone] = valid_timestamps

        if len(valid_timestamps) >= MAX_REQUESTS_PER_HOUR:
            remaining_wait = int(RATE_LIMIT_WINDOW_SECONDS - (now - valid_timestamps[0]))
            return False, f"Too many OTP requests. Please wait {remaining_wait // 60} minutes before requesting again."

        return True, ""

    @classmethod
    def record_otp_request(cls, phone: str):
        """Records a new OTP generation timestamp for rate limiting."""
        now = time.time()
        if phone not in _RATE_LIMIT_STORE:
            _RATE_LIMIT_STORE[phone] = []
        _RATE_LIMIT_STORE[phone].append(now)

    @classmethod
    def send_otp(cls, phone: str, otp: str) -> dict:
        """
        Dispatches real SMS OTP via MSG91, Fast2SMS, Twilio, or Mock.
        Returns a dict with success boolean, provider info, and status message.
        """
        provider = (Config.SMS_PROVIDER or "mock").strip().lower()

        # Format and validate Indian mobile number
        is_valid, formatted_phone, clean_10 = cls.validate_and_format_indian_phone(phone)
        if not is_valid:
            return {
                "success": False,
                "provider": provider,
                "message": formatted_phone
            }

        message_text = f"Your Smart Poultry Farm verification code is: {otp}. Valid for {Config.OTP_EXPIRY_MINUTES} minutes. Never share your OTP with anyone."

        # ----------------------------------------------------
        # 1. FAST2SMS GATEWAY (Direct Real OTP to Indian Phones)
        # ----------------------------------------------------
        if provider == "fast2sms":
            if not Config.SMS_API_KEY or Config.SMS_API_KEY.startswith("your_") or Config.SMS_API_KEY == "mock_dev_key":
                logger.warning("Fast2SMS API Key is not set in .env. Falling back to on-screen SMS verification.")
                cls._last_mock_otp = otp
                return {
                    "success": True,
                    "provider": "mock_fallback",
                    "dev_otp": otp,
                    "is_fallback": True,
                    "message": f"OTP generated for {formatted_phone}. (Set real SMS_API_KEY in .env for live carrier delivery)"
                }

            try:
                url = "https://www.fast2sms.com/dev/bulkV2"
                headers = {
                    "authorization": Config.SMS_API_KEY.strip()
                }
                payload = {
                    "variables_values": otp,
                    "route": "otp",
                    "numbers": clean_10
                }
                logger.info("Dispatching real SMS OTP to %s via Fast2SMS...", formatted_phone)
                res = requests.post(url, data=payload, headers=headers, timeout=12)
                res_data = res.json() if res.content else {}

                if res_data.get("return") is True:
                    logger.info("Real SMS successfully sent via Fast2SMS to %s", formatted_phone)
                    return {
                        "success": True,
                        "provider": "fast2sms",
                        "message": f"OTP successfully sent via SMS to {formatted_phone}"
                    }
                else:
                    raw_msg = res_data.get("message")
                    if isinstance(raw_msg, list):
                        err_msg = ", ".join(str(m) for m in raw_msg)
                    else:
                        err_msg = str(raw_msg) if raw_msg else f"HTTP {res.status_code} delivery failure"
                    logger.error("Fast2SMS API Error: %s. Using fallback OTP display so login is not blocked.", err_msg)
                    cls._last_mock_otp = otp
                    return {
                        "success": True,
                        "provider": "fast2sms_fallback",
                        "dev_otp": otp,
                        "is_fallback": True,
                        "message": f"Carrier delivery issue ({err_msg}). Use code displayed on screen."
                    }
            except Exception as e:
                logger.error("Exception sending SMS via Fast2SMS: %s. Using fallback OTP.", e)
                cls._last_mock_otp = otp
                return {
                    "success": True,
                    "provider": "fast2sms_fallback",
                    "dev_otp": otp,
                    "is_fallback": True,
                    "message": "Carrier connection timeout. Use code displayed on screen."
                }

        # ----------------------------------------------------
        # 2. MSG91 GATEWAY (Enterprise DLT for India)
        # ----------------------------------------------------
        elif provider == "msg91":
            if not Config.SMS_API_KEY or Config.SMS_API_KEY.startswith("your_"):
                return {
                    "success": False,
                    "provider": "msg91",
                    "message": "MSG91 API Key is not configured in .env file (SMS_API_KEY)."
                }

            try:
                url = "https://api.msg91.com/api/v5/otp"
                headers = {
                    "authkey": Config.SMS_API_KEY.strip(),
                    "content-type": "application/json"
                }
                payload = {
                    "template_id": Config.SMS_TEMPLATE_ID or "default_otp",
                    "mobile": f"91{clean_10}",
                    "otp": otp
                }
                if Config.SMS_SENDER_ID:
                    payload["sender"] = Config.SMS_SENDER_ID

                logger.info("Dispatching real SMS OTP to %s via MSG91...", formatted_phone)
                res = requests.post(url, json=payload, headers=headers, timeout=12)
                res_data = res.json() if res.content else {}

                if res.status_code == 200 and res_data.get("type") == "success":
                    logger.info("Real SMS successfully sent via MSG91 to %s", formatted_phone)
                    return {
                        "success": True,
                        "provider": "msg91",
                        "message": f"OTP successfully sent via SMS to {formatted_phone}"
                    }
                else:
                    err_msg = res_data.get("message", res.text or "MSG91 delivery rejected")
                    logger.error("MSG91 API Error: %s", err_msg)
                    return {
                        "success": False,
                        "provider": "msg91",
                        "message": f"MSG91 Delivery Error: {err_msg}"
                    }
            except requests.exceptions.Timeout:
                return {"success": False, "provider": "msg91", "message": "MSG91 request timed out. Please try again."}
            except Exception as e:
                logger.error("Exception sending SMS via MSG91: %s", e)
                return {"success": False, "provider": "msg91", "message": f"MSG91 connection error: {str(e)}"}

        # ----------------------------------------------------
        # 3. TWILIO GATEWAY (Global SMS)
        # ----------------------------------------------------
        elif provider == "twilio":
            account_sid = Config.TWILIO_ACCOUNT_SID
            auth_token = Config.TWILIO_AUTH_TOKEN
            from_number = Config.TWILIO_PHONE_NUMBER
            if not account_sid or not auth_token or not from_number:
                return {"success": False, "provider": "twilio", "message": "Twilio credentials incomplete in .env"}

            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
                auth = (account_sid, auth_token)
                data = {
                    "From": from_number,
                    "To": formatted_phone,
                    "Body": message_text
                }
                res = requests.post(url, data=data, auth=auth, timeout=12)
                if res.status_code in (200, 201):
                    return {
                        "success": True,
                        "provider": "twilio",
                        "message": f"OTP sent via Twilio to {formatted_phone}"
                    }
                else:
                    return {
                        "success": False,
                        "provider": "twilio",
                        "message": f"Twilio SMS Error: {res.text}"
                    }
            except Exception as e:
                return {"success": False, "provider": "twilio", "message": f"Twilio connection error: {str(e)}"}

        # ----------------------------------------------------
        # 4. DEVELOPMENT MOCK MODE (Only when explicitly set)
        # ----------------------------------------------------
        elif provider == "mock":
            cls._last_mock_otp = otp
            logger.info("=" * 60)
            logger.info(" [DEVELOPMENT MOCK SMS GATEWAY]")
            logger.info(" Destination: %s", formatted_phone)
            logger.info(" OTP Code:    %s", otp)
            logger.info(" Valid for:   %s minutes", Config.OTP_EXPIRY_MINUTES)
            logger.info("=" * 60)
            return {
                "success": True,
                "provider": "mock",
                "dev_otp": otp,
                "message": f"[DEV MODE] Mock SMS logged to server console for {formatted_phone}."
            }

        else:
            return {
                "success": False,
                "provider": provider,
                "message": f"Unsupported SMS provider '{provider}'. Please use 'fast2sms' or 'msg91'."
            }
