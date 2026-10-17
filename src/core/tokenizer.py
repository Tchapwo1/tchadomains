"""
TchaDomains Linguistic Tokenizer & Lexical Analyzer
Deconstructs domain SLDs into constituent words, calculates syllables,
and identifies commercial category tags.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Basic vowel pattern for syllable counting
VOWELS = set("aeiouy")
CONSONANTS = set("abcdefghijklmnopqrstuvwxyz") - VOWELS

class Tokenizer:
    def __init__(self, dict_path: str = "data/dictionary/words.txt", comm_path: str = "data/dictionary/commercial.json"):
        self.dict_path = Path(dict_path)
        self.comm_path = Path(comm_path)
        self.words = set()
        self.categories = {}
        self.keyword_to_category = {}
        self.load_dictionaries()

    def load_dictionaries(self):
        """Loads English words and commercial category mappings."""
        if self.dict_path.exists():
            with open(self.dict_path, "r", encoding="utf-8") as f:
                for line in f:
                    w = line.strip().lower()
                    if len(w) >= 2:
                        self.words.add(w)

        if self.comm_path.exists():
            with open(self.comm_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.categories = data.get("categories", {})
                for cat_name, info in self.categories.items():
                    for kw in info.get("keywords", []):
                        self.keyword_to_category[kw.lower()] = {
                            "category": cat_name,
                            "weight": info.get("weight", 1.0)
                        }
                        self.words.add(kw.lower())

    def split_compound(self, sld: str) -> List[str]:
        """
        Decomposes an SLD into constituent dictionary words using DP / memoized search.
        Prefers splits that minimize unsegmented residues and maximize word lengths.
        """
        sld = sld.lower()
        n = len(sld)

        # 1. Direct single-word match
        if sld in self.words:
            return [sld]

        # 2. Dynamic programming for 2-word or 3-word split
        # We look for valid splits (w1, w2) where w1 in words and w2 in words
        best_split = None
        for i in range(2, n - 1):
            w1 = sld[:i]
            w2 = sld[i:]
            if w1 in self.words and w2 in self.words:
                best_split = [w1, w2]
                break

        if best_split:
            return best_split

        # 3. Check for 3-word splits
        for i in range(2, n - 3):
            w1 = sld[:i]
            if w1 in self.words:
                for j in range(i + 2, n - 1):
                    w2 = sld[i:j]
                    w3 = sld[j:]
                    if w2 in self.words and w3 in self.words:
                        return [w1, w2, w3]

        return [sld]

    def count_syllables(self, sld: str) -> int:
        """Estimates pronounceable syllables based on vowel clusters."""
        sld = sld.lower()
        count = 0
        prev_is_vowel = False
        for char in sld:
            is_vowel = char in VOWELS
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel
        # Silent 'e' at end
        if sld.endswith("e") and count > 1 and not sld.endswith("le"):
            count -= 1
        return max(1, count)

    def is_cvcv_brandable(self, sld: str) -> bool:
        """
        Detects pronounceable alternating CVCV or VCVC patterns (e.g., 'luma', 'zulu', 'viva').
        Highly prized in domain investing for 4-6 letter brandables.
        """
        sld = sld.lower()
        if len(sld) not in (4, 5, 6):
            return False

        pattern = [1 if c in VOWELS else 0 for c in sld]
        # Alternating: [0, 1, 0, 1] or [1, 0, 1, 0]
        is_alternating = all(pattern[i] != pattern[i+1] for i in range(len(pattern) - 1))
        return is_alternating

    def analyze(self, sld: str) -> Dict:
        """Full tokenization and category detection."""
        detected_words = self.split_compound(sld)
        syllables = self.count_syllables(sld)
        is_cvcv = self.is_cvcv_brandable(sld)

        # Detect category and commercial multiplier
        primary_category = "General"
        commercial_multiplier = 1.0

        for word in detected_words:
            if word in self.keyword_to_category:
                cat_info = self.keyword_to_category[word]
                primary_category = cat_info["category"]
                commercial_multiplier = max(commercial_multiplier, cat_info["weight"])

        if is_cvcv and primary_category == "General":
            primary_category = "Brandable CVCV"

        return {
            "sld": sld,
            "detected_words": detected_words,
            "word_count": len(detected_words) if detected_words[0] in self.words else 0,
            "syllables": syllables,
            "is_cvcv": is_cvcv,
            "primary_category": primary_category,
            "commercial_multiplier": commercial_multiplier
        }
