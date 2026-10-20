"""
Unit Tests for TchaDomains Filter, Tokenizer, and Scorer
"""

import pytest
from src.core.filter_engine import FilterEngine
from src.core.tokenizer import Tokenizer
from src.core.scorer import AlphaScorer

@pytest.fixture
def filter_engine():
    return FilterEngine()

@pytest.fixture
def tokenizer():
    return Tokenizer()

@pytest.fixture
def scorer():
    return AlphaScorer()

def test_filter_engine_rejections(filter_engine):
    assert filter_engine.is_candidate("my-domain.com")[0] is False
    assert filter_engine.is_candidate("domain123.com")[0] is False
    assert filter_engine.is_candidate("superlongdomainnameexceedinglength.com")[0] is False
    assert filter_engine.is_candidate("aaabbbccc.com")[0] is False
    assert filter_engine.is_candidate("ab.com")[0] is False  # too short (<3)
    # Pillar 4: Trademark rejections
    assert filter_engine.is_candidate("chatgptbot.com")[0] is False
    assert filter_engine.is_candidate("stripepay.com")[0] is False
    assert filter_engine.is_candidate("openainode.com")[0] is False
    assert filter_engine.is_candidate("googlecloud.com")[0] is False

def test_filter_engine_acceptance(filter_engine):
    assert filter_engine.is_candidate("payflow.com")[0] is True
    assert filter_engine.is_candidate("cloudpulse.com")[0] is True
    assert filter_engine.is_candidate("luma.ai")[0] is True

def test_tokenizer_compound_splitting(tokenizer):
    assert tokenizer.split_compound("payflow") == ["pay", "flow"]
    assert tokenizer.split_compound("cloudpulse") == ["cloud", "pulse"]
    assert tokenizer.split_compound("agentshield") == ["agent", "shield"]
    assert tokenizer.split_compound("fastcode") == ["fast", "code"]

def test_cvcv_detection(tokenizer):
    assert tokenizer.is_cvcv_brandable("zulu") is True
    assert tokenizer.is_cvcv_brandable("luma") is True
    assert tokenizer.is_cvcv_brandable("viva") is True
    assert tokenizer.is_cvcv_brandable("payflow") is False

def test_alpha_scorer_valuation_hierarchy(scorer):
    # Short ultra-high intent names
    aihub = scorer.score("aihub.com")
    paybot = scorer.score("paybot.com")
    payflow = scorer.score("payflow.com")
    cloudpulse = scorer.score("cloudpulse.com")
    zulu = scorer.score("zulu.com")
    xzqpk = scorer.score("xzqpk.com")

    assert aihub["alpha_score"] >= 90.0
    assert paybot["alpha_score"] >= 88.0
    assert payflow["alpha_score"] >= 85.0
    assert cloudpulse["alpha_score"] >= 80.0
    assert zulu["alpha_score"] >= 85.0

    # Random consonant junk should score <= 40.0
    assert xzqpk["alpha_score"] <= 40.0

    # Ensure quality separation between premium assets and junk
    assert payflow["alpha_score"] > xzqpk["alpha_score"] + 45.0
