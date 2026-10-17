"""
TchaDomains Filter Engine
Filters out 99% of deadweight candidates (hyphens, digits, spam strings, excessive length).
"""

import re
from typing import Tuple, Optional

# Supported TLDs with commercial demand
ALLOWED_TLDS = {"com", "net", "ai", "io", "co", "org", "app", "dev"}

# Rejection patterns: digits, hyphens, consecutive 3+ identical letters
DIGIT_PATTERN = re.compile(r"\d")
HYPHEN_PATTERN = re.compile(r"-")
CONSECUTIVE_REPEAT = re.compile(r"([a-z])\1{2,}")
INVALID_CHARS = re.compile(r"[^a-z0-9\.-]")

class FilterEngine:
    def __init__(self, max_length: int = 10, min_length: int = 3, allowed_tlds: set = None):
        self.max_length = max_length
        self.min_length = min_length
        self.allowed_tlds = allowed_tlds or ALLOWED_TLDS

    def parse_domain(self, domain: str) -> Optional[Tuple[str, str]]:
        """Splits domain into (sld, tld). E.g. 'cloudpulse.com' -> ('cloudpulse', 'com')"""
        domain = domain.strip().lower()
        parts = domain.split(".")
        if len(parts) < 2:
            return None
        sld = parts[0]
        tld = ".".join(parts[1:])
        return sld, tld

    def is_candidate(self, domain: str) -> Tuple[bool, str]:
        """
        Validates if domain qualifies as a high-alpha candidate.
        Returns (is_valid, rejection_reason).
        """
        parsed = self.parse_domain(domain)
        if not parsed:
            return False, "INVALID_FORMAT"

        sld, tld = parsed

        if tld not in self.allowed_tlds:
            return False, f"UNSUPPORTED_TLD_{tld.upper()}"

        if len(sld) < self.min_length:
            return False, "TOO_SHORT"

        if len(sld) > self.max_length:
            return False, "EXCEEDS_MAX_LENGTH"

        if HYPHEN_PATTERN.search(sld):
            return False, "CONTAINS_HYPHEN"

        if DIGIT_PATTERN.search(sld):
            return False, "CONTAINS_DIGITS"

        if INVALID_CHARS.search(sld):
            return False, "INVALID_CHARACTERS"

        if CONSECUTIVE_REPEAT.search(sld):
            return False, "EXCESSIVE_REPEATED_LETTERS"

        return True, "PASSED"
