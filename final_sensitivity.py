"""Exact baseline sensitivity checks for the final release (v1.0-final).

These are model calculations. They contain no participant observations.
Run from this directory: python final_sensitivity.py
"""
from fractions import Fraction
from pathlib import Path
import json
import pandas as pd
from src.auction import MAIN, mixed_threshold, trust_threshold, outcome


def sensitivity_rows():
    rows = []
    for b in (Fraction(0), Fraction(1, 4), Fraction(1, 2)):
        p_star = Fraction(2, 3)
        threshold = (p_star - b) / (1 - b)
        t_star = trust_threshold(MAIN, float(b))
        p = float(b) + (1 - float(b)) * t_star
        u_low, u_high = 7 - 2 * p, 6 - 0.5 * p
        assert abs(t_star - float(threshold)) < 1e-12
        assert abs(u_low - u_high) < 1e-12
        rows.append(dict(baseline_high=float(b), p_star=float(p_star),
                         threshold_fraction=str(threshold), t_star=t_star,
                         p_at_threshold=p, low_payoff=u_low, high_payoff=u_high,
                         evidence_status="exact model calculation"))
    return rows


def main():
    out = Path('outputs'); out.mkdir(exist_ok=True)
    rows = sensitivity_rows()
    pd.DataFrame(rows).to_csv(out / 'final_baseline_sensitivity.csv', index=False)
    (out / 'final_baseline_sensitivity.json').write_text(json.dumps(rows, indent=2))
    (out / 'final_baseline_sensitivity.md').write_text(
        '# Baseline sensitivity\n\nExact model calculations, not observed trust or behavior.\n\n' +
        pd.DataFrame(rows)[['baseline_high', 'threshold_fraction', 't_star',
                            'p_at_threshold', 'low_payoff', 'high_payoff']].to_markdown(index=False) +
        '\n\nAt equality both bids are best replies. High is strictly better above the threshold.\n')
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == '__main__':
    main()
