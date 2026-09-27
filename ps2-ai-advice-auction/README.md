# AI Advice, Human Trust, and First-Price Bidding

COMSCI/ECON 206 · PS2 · Team FP07 · Course instructor: Professor Luyao Zhang

**Question.** When a bidding assistant serves either the buyer or the seller, does buyers'
trust carry the assistant's objective into their bids, and whose payoff moves as a result?

## The game

Two buyers bid for one second-hand item worth 6 to each (units of 10 RMB). Each has a budget
of 5 and bids Low 2 or High 5 at the same time. The higher bid wins and pays its own bid; ties
are broken by a coin flip. Before bidding, buyers may see advice from an AI whose sponsor is
disclosed: none, the buyer, or the seller.

| Buyer 1 / Buyer 2 | Low 2 | High 5 |
|---|---|---|
| **Low 2** | (7, 7) | (5, 6) |
| **High 5** | (6, 5) | (5.5, 5.5) |

Payoff = money left + item value if won; ties give the average of winning and losing.

## Main results (actual output of `python run_all.py`)

| Fact | Value |
|---|---|
| Pure Nash equilibria (first price) | (Low, Low) and (High, High) |
| Risk-dominant equilibrium | (Low, Low) |
| High is the better reply when P(other bids High) exceeds | p* = 2/3 |
| Buyer-aligned AI advises / seller-aligned AI advises | Low / High |
| Trust needed for following High advice to be rational, t* | 0.556 (with baseline High share 0.25, an assumption) |
| Seller revenue at trust 1: buyer-aligned / seller-aligned AI | 2.0 / 5.0 |
| Buyer payoff at trust 1: buyer-aligned / seller-aligned AI | 7.0 / 5.5 |
| Total welfare, every profile | 16 (advice only redistributes) |
| Second-price comparison | High strictly dominant; unique equilibrium (High, High) |

The baseline High share (0.25) is a placeholder until the No-AI peer-play data replace it.
Full tables: `outputs/headline.csv`, `outputs/trust_sweep_first_price.csv`; figure:
`figures/trust_sweep.png`.

## Reproduce

```bash
pip install -r requirements.txt
pytest -q            # 8 checks: payoffs, equilibria, welfare, advice, threshold, second price
python run_all.py    # writes outputs/ and figures/
```

Colab: open `notebooks/ps2_analysis.ipynb`, set `REPO_URL` in the first code cell, Run all.
Runtime is a few seconds; the Monte Carlo check uses seed 42 and 10,000 pairs.

## Repository map

| Path | Content |
|---|---|
| `src/auction.py` | Game primitives, payoffs, equilibria, advice rule, trust model |
| `tests/test_auction.py` | Automated checks of every reported fact |
| `run_all.py` | Regenerates all outputs and the figure |
| `notebooks/ps2_analysis.ipynb` | Narrative walk-through with outputs |
| `advice/prompts.md` | Planned protocol for checking a real language model's advice |
| `outputs/`, `figures/` | Generated results |

## Pseudocode

```
for rule in {first price, second price}:
    build payoffs for all four bid profiles from value, budget, bids, rule
    find pure Nash equilibria by checking every unilateral deviation
    compute p*, risk dominance, and each sponsor's advice
for condition in {No AI, buyer-aligned, seller-aligned}:
    for trust t in 0, 0.05, ..., 1:
        P(High) = t * [advice is High] + (1 - t) * baseline
        expected payoffs = sum over profiles of P(profile) * payoff
check expected values against a seeded Monte Carlo simulation
```

## Limits

Common, publicly known value rather than private values; two bid levels; one-shot play; trust
modelled as one probability; baseline behavior assumed; LLM advice check not yet run.
Classroom peer play is exploratory, not population evidence.

## Links

- Hugging Face Space: https://huggingface.co/spaces/yt1080/ps2-ai-advice-auction
- Paper and A0 poster: [TODO]

License: MIT.
