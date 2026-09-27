"""Two-buyer sealed-bid auction with pre-bid AI advice.

Main specification (campus second-hand framing, in units of 10 RMB):
  item value 6 to each buyer, budget 5 each, bids Low = 2 or High = 5,
  first-price rule, ties broken 50/50.
Every payoff below is computed from these primitives, never typed in.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product

import numpy as np
import pandas as pd

ACTIONS = ("Low", "High")


@dataclass(frozen=True)
class Game:
    value: float = 6.0       # common, publicly known value of the item
    budget: float = 5.0      # each buyer's money; must cover the High bid
    low: float = 2.0
    high: float = 5.0
    rule: str = "first"      # "first": winner pays own bid; "second": pays the other bid

    def __post_init__(self):
        if self.high > self.budget:
            raise ValueError("High bid exceeds budget: a buyer could not pay it.")

    def bid(self, action: str) -> float:
        return self.low if action == "Low" else self.high


def outcome(game: Game, a1: str, a2: str) -> dict:
    """Expected payoffs (money + item value) for one action profile."""
    b1, b2 = game.bid(a1), game.bid(a2)
    V, B = game.value, game.budget
    if b1 == b2:
        price = b1
        u1 = u2 = 0.5 * (B + V - price) + 0.5 * B
    else:
        price = max(b1, b2) if game.rule == "first" else min(b1, b2)
        win, lose = B + V - price, B
        u1, u2 = (win, lose) if b1 > b2 else (lose, win)
    return {"u1": u1, "u2": u2, "revenue": price, "welfare": u1 + u2 + price}


def payoff_table(game: Game) -> pd.DataFrame:
    return pd.DataFrame([{"buyer1": a1, "buyer2": a2, **outcome(game, a1, a2)}
                         for a1, a2 in product(ACTIONS, ACTIONS)])


def payoff_matrix_str(game: Game) -> pd.DataFrame:
    m = pd.DataFrame(index=[f"{a} {game.bid(a):g}" for a in ACTIONS],
                     columns=[f"{a} {game.bid(a):g}" for a in ACTIONS], dtype=object)
    for (i, a1), (j, a2) in product(enumerate(ACTIONS), enumerate(ACTIONS)):
        o = outcome(game, a1, a2)
        m.iloc[i, j] = f"({o['u1']:g}, {o['u2']:g})"
    m.index.name = "Buyer 1 / Buyer 2"
    return m


def pure_nash(game: Game) -> list[tuple[str, str]]:
    eq = []
    for a1, a2 in product(ACTIONS, ACTIONS):
        o = outcome(game, a1, a2)
        if all(o["u1"] >= outcome(game, d, a2)["u1"] for d in ACTIONS) and \
           all(o["u2"] >= outcome(game, a1, d)["u2"] for d in ACTIONS):
            eq.append((a1, a2))
    return eq


def strictly_dominant(game: Game) -> str | None:
    for a in ACTIONS:
        b = [x for x in ACTIONS if x != a][0]
        if all(outcome(game, a, o)["u1"] > outcome(game, b, o)["u1"] for o in ACTIONS):
            return a
    return None


def mixed_threshold(game: Game) -> float | None:
    """p* = probability the other buyer bids High that makes Low and High equally good.

    If p > p*, High is the better reply. Also the symmetric mixed equilibrium.
    """
    u = lambda a, o: outcome(game, a, o)["u1"]
    d_low = u("High", "Low") - u("Low", "Low")      # gain from High when other is Low
    d_high = u("High", "High") - u("Low", "High")   # gain from High when other is High
    if d_low == d_high:
        return None
    p = -d_low / (d_high - d_low)
    return p if 0 < p < 1 else None


def risk_dominant(game: Game) -> str | None:
    """Harsanyi-Selten risk dominance between symmetric (Low,Low) and (High,High)."""
    u = lambda a, o: outcome(game, a, o)["u1"]
    loss_LL = u("Low", "Low") - u("High", "Low")
    loss_HH = u("High", "High") - u("Low", "High")
    if loss_LL <= 0 or loss_HH <= 0:
        return None
    return "Low" if loss_LL ** 2 > loss_HH ** 2 else "High"


def ai_advice(game: Game, sponsor: str | None) -> str | None:
    """Advice maximizing the sponsor's objective if both buyers follow it."""
    if sponsor is None:
        return None
    key = "u1" if sponsor == "buyer" else "revenue"
    return max(ACTIONS, key=lambda r: outcome(game, r, r)[key])


def p_high(advice: str | None, trust: float, baseline_high: float) -> float:
    """P(one buyer bids High): follow advice with prob `trust`, else own choice."""
    if advice is None:
        return baseline_high
    return trust * (advice == "High") + (1 - trust) * baseline_high


def trust_threshold(game: Game, baseline_high: float) -> float | None:
    """Trust t* above which following High advice is a best reply.

    If the other buyer follows with prob t and otherwise bids High with prob
    `baseline_high`, then P(other High) = t + (1-t)*baseline_high. Following
    High advice is rational once this exceeds p*.
    """
    p = mixed_threshold(game)
    if p is None:
        return None
    t = (p - baseline_high) / (1 - baseline_high)
    return min(max(t, 0.0), 1.0)


def expected_outcomes(game: Game, advice, trust, baseline_high) -> dict:
    q = p_high(advice, trust, baseline_high)
    pr = {"High": q, "Low": 1 - q}
    r = {"share_high": q, "p_LL": pr["Low"] ** 2, "p_HH": q ** 2,
         "buyer_payoff": 0.0, "revenue": 0.0, "welfare": 0.0}
    for a1, a2 in product(ACTIONS, ACTIONS):
        w, o = pr[a1] * pr[a2], outcome(game, a1, a2)
        r["buyer_payoff"] += w * (o["u1"] + o["u2"]) / 2
        r["revenue"] += w * o["revenue"]
        r["welfare"] += w * o["welfare"]
    return r


def simulate(game: Game, advice, trust, baseline_high, n_pairs=10_000, seed=42) -> dict:
    """Monte Carlo check of expected_outcomes (fixed seed)."""
    rng = np.random.default_rng(seed)
    q = p_high(advice, trust, baseline_high)
    high = rng.random((n_pairs, 2)) < q
    table = {k: outcome(game, *k) for k in product(ACTIONS, ACTIONS)}
    buyer = rev = 0.0
    for h1, h2 in high:
        o = table[("High" if h1 else "Low", "High" if h2 else "Low")]
        buyer += (o["u1"] + o["u2"]) / 2
        rev += o["revenue"]
    return {"share_high": float(high.mean()), "buyer_payoff": buyer / n_pairs,
            "revenue": rev / n_pairs}


CONDITIONS = {"No AI": None, "Buyer-aligned AI": "buyer", "Seller-aligned AI": "seller"}


def trust_sweep(game: Game, baseline_high: float, trusts=None) -> pd.DataFrame:
    trusts = np.round(np.linspace(0, 1, 21), 2) if trusts is None else trusts
    rows = []
    for name, sponsor in CONDITIONS.items():
        adv = ai_advice(game, sponsor)
        for t in trusts:
            rows.append({"condition": name, "advice": adv or "none", "trust": float(t),
                         **expected_outcomes(game, adv, t, baseline_high)})
    return pd.DataFrame(rows)


def game_summary(game: Game) -> dict:
    return {"rule": game.rule, "high_bid": game.high,
            "pure_nash": pure_nash(game), "dominant": strictly_dominant(game),
            "mixed_p_star": mixed_threshold(game), "risk_dominant": risk_dominant(game),
            "buyer_ai_advice": ai_advice(game, "buyer"),
            "seller_ai_advice": ai_advice(game, "seller")}


MAIN = Game()
SECOND_PRICE = replace(MAIN, rule="second")
