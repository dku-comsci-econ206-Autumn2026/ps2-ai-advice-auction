"""Reproduce every number and figure reported in the PS2 paper.

Usage:  python run_all.py
Writes: outputs/*.csv, outputs/*.md, figures/trust_sweep.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.auction import (MAIN, SECOND_PRICE, payoff_matrix_str, payoff_table, game_summary,
                         trust_sweep, trust_threshold, expected_outcomes, simulate,
                         ai_advice, CONDITIONS)

BASELINE_HIGH = 0.25  # ASSUMPTION: share of High bids without AI; replace with peer-play data
SEED = 42
OUT, FIG = Path("outputs"), Path("figures")
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)

# 1. Payoff matrices and equilibrium facts for both rules
with open(OUT / "matrices.md", "w") as f:
    for name, g in [("First price (main)", MAIN), ("Second price (comparison)", SECOND_PRICE)]:
        f.write(f"## {name}\n\n{payoff_matrix_str(g).to_markdown()}\n\n")
        s = game_summary(g)
        f.write("```\n" + json.dumps(s, indent=2, default=str) + "\n```\n\n")
        payoff_table(g).to_csv(OUT / f"payoffs_{g.rule}.csv", index=False)

# 2. Trust sweep, first price
sweep = trust_sweep(MAIN, BASELINE_HIGH)
sweep.to_csv(OUT / "trust_sweep_first_price.csv", index=False)
t_star = trust_threshold(MAIN, BASELINE_HIGH)

# 3. Headline table at trust = 0, 0.5, 1 for both rules
rows = []
for g in (MAIN, SECOND_PRICE):
    for cname, sponsor in CONDITIONS.items():
        adv = ai_advice(g, sponsor)
        for t in (0.0, 0.5, 1.0):
            r = expected_outcomes(g, adv, t, BASELINE_HIGH)
            rows.append({"rule": g.rule, "condition": cname, "advice": adv or "none",
                         "trust": t, **{k: round(v, 3) for k, v in r.items()}})
import pandas as pd
head = pd.DataFrame(rows)
head.to_csv(OUT / "headline.csv", index=False)

# 4. Monte Carlo check of the exact formulas
mc = []
for cname, sponsor in CONDITIONS.items():
    adv = ai_advice(MAIN, sponsor)
    ex = expected_outcomes(MAIN, adv, 0.5, BASELINE_HIGH)
    sim = simulate(MAIN, adv, 0.5, BASELINE_HIGH, n_pairs=10_000, seed=SEED)
    mc.append({"condition": cname, "exact_revenue": round(ex["revenue"], 3),
               "sim_revenue": round(sim["revenue"], 3),
               "exact_buyer": round(ex["buyer_payoff"], 3),
               "sim_buyer": round(sim["buyer_payoff"], 3)})
pd.DataFrame(mc).to_csv(OUT / "monte_carlo_check.csv", index=False)

# 5. Figure
colors = {"No AI": "#6B7280", "Buyer-aligned AI": "#2E7D46", "Seller-aligned AI": "#C7621A"}
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
for metric, ax, title in [("share_high", axes[0], "Share of High bids"),
                          ("buyer_payoff", axes[1], "Expected buyer payoff"),
                          ("revenue", axes[2], "Expected seller revenue")]:
    for c, d in sweep.groupby("condition"):
        ax.plot(d["trust"], d[metric], label=c, color=colors[c], lw=2)
    if t_star is not None:
        ax.axvline(t_star, color="#6B4FA8", ls="--", lw=1)
    ax.set_title(title); ax.set_xlabel("Trust (probability of following advice)")
    ax.grid(alpha=.3)
axes[0].axhline(2/3, color="#6B4FA8", ls=":", lw=1)
axes[0].legend(fontsize=8, loc="upper left")
fig.suptitle(f"First-price auction, baseline High share = {BASELINE_HIGH}; dashed line: t* = {t_star:.3f}",
             fontsize=10)
fig.tight_layout()
fig.savefig(FIG / "trust_sweep.png", dpi=200)

print(open(OUT / "matrices.md").read())
print(f"Trust threshold t* (first price, baseline {BASELINE_HIGH}): {t_star:.4f}\n")
print(head.to_string(index=False))
print("\nMonte Carlo check (trust 0.5, seed 42, 10,000 pairs):")
print(pd.DataFrame(mc).to_string(index=False))
