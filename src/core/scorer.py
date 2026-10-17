"""
TchaDomains Alpha Valuation Engine
Calculates the proprietary Tcha Alpha Score (0 - 100) combining length,
linguistic harmony, commercial intent, and TLD prestige.
"""

from typing import Dict
from src.core.tokenizer import Tokenizer, VOWELS

TLD_PRESTIGE = {
    "com": 100.0,
    "ai": 95.0,
    "io": 85.0,
    "co": 75.0,
    "net": 65.0,
    "org": 60.0,
    "app": 55.0,
    "dev": 50.0
}

CATEGORY_COMMERCIAL_SCORES = {
    "AI": 100.0,
    "Fintech": 100.0,
    "Cybersecurity": 95.0,
    "Cloud & Infrastructure": 90.0,
    "DevTools": 85.0,
    "Brandable Power": 85.0,
    "Brandable CVCV": 80.0,
    "General": 35.0
}

class AlphaScorer:
    def __init__(self, tokenizer: Tokenizer = None):
        self.tokenizer = tokenizer or Tokenizer()

    def calculate_length_score(self, length: int, is_clean_compound: bool = False, has_no_vowels: bool = False) -> float:
        """
        Calculates S_len (0 - 100) with heavy rewards for short SLDs.
        Clean 2-word compounds receive a slight length grace bonus.
        Unpronounceable strings without vowels receive a heavy penalty.
        """
        if length <= 4:
            base = 100.0
        elif length == 5:
            base = 92.0
        elif length == 6:
            base = 85.0
        elif length == 7:
            base = 75.0
        elif length == 8:
            base = 65.0
        elif length == 9:
            base = 50.0
        elif length == 10:
            base = 40.0
        else:
            base = max(0.0, 30.0 - 5.0 * (length - 10))

        if is_clean_compound and 8 <= length <= 10:
            base += 10.0

        if has_no_vowels and length >= 4:
            base *= 0.5

        return min(100.0, base)

    def calculate_linguistic_score(self, sld: str, analysis: Dict) -> float:
        """
        Calculates S_ling (0 - 100) based on dictionary match, syllables, and CVCV rhythm.
        Heavily penalizes unpronounceable strings lacking vowels.
        """
        detected_words = analysis["detected_words"]
        word_count = analysis["word_count"]
        is_cvcv = analysis["is_cvcv"]
        syllables = analysis["syllables"]

        # Vowel count check for unpronounceable junk
        vowel_count = sum(1 for c in sld if c in VOWELS)
        vowel_ratio = vowel_count / len(sld) if len(sld) > 0 else 0

        # Unpronounceable junk filter (no vowels or < 15% vowels without being an acronym)
        if vowel_count == 0 or (vowel_ratio < 0.15 and len(sld) >= 5):
            return 5.0

        # 1-word exact dictionary word
        if word_count == 1:
            return 100.0
        # 2-word clean compound (e.g., 'cloudpulse', 'payflow')
        elif word_count == 2:
            if 2 <= syllables <= 3:
                return 92.0
            else:
                return 82.0
        # CVCV pronounceable non-dictionary name (e.g. 'zulu', 'luma')
        elif is_cvcv:
            return 88.0
        # 3-word compound
        elif word_count >= 3:
            return 50.0
        else:
            # Non-dictionary string
            if syllables >= 2 and vowel_ratio >= 0.3:
                return 40.0
            return 15.0

    def calculate_commercial_score(self, sld: str, analysis: Dict) -> float:
        """
        Calculates S_comm (0 - 100) based on niche high-CPC buyer intent.
        """
        vowel_count = sum(1 for c in sld if c in VOWELS)
        if vowel_count == 0 and len(sld) >= 4:
            return 5.0

        category = analysis["primary_category"]
        word_count = analysis["word_count"]

        # If not a recognized word or CVCV, do not grant full General score
        if word_count == 0 and not analysis["is_cvcv"]:
            return 15.0

        base_score = CATEGORY_COMMERCIAL_SCORES.get(category, 35.0)
        multiplier = analysis["commercial_multiplier"]
        return min(100.0, base_score * multiplier)

    def calculate_tld_score(self, tld: str) -> float:
        """
        Calculates S_tld (0 - 100).
        """
        return TLD_PRESTIGE.get(tld.lower(), 40.0)

    def score(self, domain_name: str) -> Dict:
        """
        Computes the complete Tcha Alpha Score for a domain.
        """
        domain_name = domain_name.strip().lower()
        parts = domain_name.split(".")
        sld = parts[0]
        tld = parts[1] if len(parts) > 1 else "com"

        analysis = self.tokenizer.analyze(sld)
        is_clean_compound = analysis["word_count"] == 2
        vowel_count = sum(1 for c in sld if c in VOWELS)
        has_no_vowels = vowel_count == 0

        s_len = self.calculate_length_score(len(sld), is_clean_compound=is_clean_compound, has_no_vowels=has_no_vowels)
        s_ling = self.calculate_linguistic_score(sld, analysis)
        s_comm = self.calculate_commercial_score(sld, analysis)
        s_tld = self.calculate_tld_score(tld)

        # Weighted composite formula:
        # Length: 30%, Linguistic: 25%, Commercial: 35%, TLD: 10%
        composite = (
            0.30 * s_len +
            0.25 * s_ling +
            0.35 * s_comm +
            0.10 * s_tld
        )

        final_score = round(min(100.0, max(0.0, composite)), 1)

        return {
            "domain_name": domain_name,
            "sld": sld,
            "tld": tld,
            "char_length": len(sld),
            "syllables": analysis["syllables"],
            "detected_words": analysis["detected_words"],
            "primary_category": analysis["primary_category"],
            "commercial_multiplier": analysis["commercial_multiplier"],
            "sub_scores": {
                "length": s_len,
                "linguistic": s_ling,
                "commercial": s_comm,
                "tld": s_tld
            },
            "alpha_score": final_score
        }
