"""Unit tests for the deterministic logic that must not regress."""

from app.api.quant import _exact_match, _to_number
from app.services.grader import _bucket


def test_to_number_handles_fractions_and_symbols():
    assert _to_number("1/6") == 1 / 6
    assert _to_number("7.5%") == 7.5
    assert _to_number("$1,200") == 1200.0
    assert _to_number("not a number") is None


def test_exact_match_integers_require_exact():
    assert _exact_match("391", "391") is True
    assert _exact_match("391", "390") is False


def test_exact_match_fractions_allow_tolerance():
    assert _exact_match("1/6", "0.1667") is True
    assert _exact_match("1/6", "0.2") is False


def test_exact_match_non_numeric_returns_none():
    assert _exact_match("triangle", "circle") is None


def test_bucket_thresholds():
    assert _bucket(4.5) == "yes"
    assert _bucket(3.6) == "lean_yes"
    assert _bucket(3.0) == "lean_no"
    assert _bucket(2.2) == "no"
    assert _bucket(1.0) == "strong_no"
