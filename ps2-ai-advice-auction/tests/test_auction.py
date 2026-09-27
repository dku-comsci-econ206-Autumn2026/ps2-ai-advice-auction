import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from src.auction import (Game, MAIN, SECOND_PRICE, outcome, pure_nash, strictly_dominant,
                         mixed_threshold, risk_dominant, ai_advice, trust_threshold,
                         expected_outcomes, simulate)


def pair(g, a1, a2):
    o = outcome(g, a1, a2)
    return o["u1"], o["u2"]


def test_main_matrix():
    assert pair(MAIN, "Low", "Low") == (7, 7)
    assert pair(MAIN, "Low", "High") == (5, 6)
    assert pair(MAIN, "High", "Low") == (6, 5)
    assert pair(MAIN, "High", "High") == (5.5, 5.5)


def test_main_is_coordination_game():
    assert pure_nash(MAIN) == [("Low", "Low"), ("High", "High")]
    assert strictly_dominant(MAIN) is None
    assert mixed_threshold(MAIN) == pytest.approx(2 / 3)
    assert risk_dominant(MAIN) == "Low"


def test_welfare_constant():
    for g in (MAIN, SECOND_PRICE):
        for a1 in ("Low", "High"):
            for a2 in ("Low", "High"):
                assert outcome(g, a1, a2)["welfare"] == 2 * g.budget + g.value


def test_advice_follows_sponsor():
    assert ai_advice(MAIN, "buyer") == "Low"
    assert ai_advice(MAIN, "seller") == "High"


def test_trust_threshold():
    # p* = 2/3, baseline 0.25 -> t* = (2/3 - 1/4) / (3/4) = 5/9
    assert trust_threshold(MAIN, 0.25) == pytest.approx(5 / 9)


def test_second_price_high_dominant():
    assert strictly_dominant(SECOND_PRICE) == "High"
    assert pure_nash(SECOND_PRICE) == [("High", "High")]


def test_budget_guard():
    with pytest.raises(ValueError):
        Game(high=8.0, budget=5.0)


def test_simulation_matches_exact():
    ex = expected_outcomes(MAIN, "High", 0.6, 0.25)
    mc = simulate(MAIN, "High", 0.6, 0.25, n_pairs=20_000)
    assert ex["revenue"] == pytest.approx(mc["revenue"], abs=0.05)
    assert ex["buyer_payoff"] == pytest.approx(mc["buyer_payoff"], abs=0.03)
