## First price (main)

| Buyer 1 / Buyer 2   | Low 2   | High 5     |
|:--------------------|:--------|:-----------|
| Low 2               | (7, 7)  | (5, 6)     |
| High 5              | (6, 5)  | (5.5, 5.5) |

```
{
  "rule": "first",
  "high_bid": 5.0,
  "pure_nash": [
    [
      "Low",
      "Low"
    ],
    [
      "High",
      "High"
    ]
  ],
  "dominant": null,
  "mixed_p_star": 0.6666666666666666,
  "risk_dominant": "Low",
  "buyer_ai_advice": "Low",
  "seller_ai_advice": "High"
}
```

## Second price (comparison)

| Buyer 1 / Buyer 2   | Low 2   | High 5     |
|:--------------------|:--------|:-----------|
| Low 2               | (7, 7)  | (5, 9)     |
| High 5              | (9, 5)  | (5.5, 5.5) |

```
{
  "rule": "second",
  "high_bid": 5.0,
  "pure_nash": [
    [
      "High",
      "High"
    ]
  ],
  "dominant": "High",
  "mixed_p_star": null,
  "risk_dominant": null,
  "buyer_ai_advice": "Low",
  "seller_ai_advice": "High"
}
```

