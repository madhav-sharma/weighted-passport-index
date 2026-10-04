# Weighted Passport Index — Proposals

*Status: draft for discussion. Nothing is built yet.*

## 1. The idea in one line

Count passport access by **what a destination is worth**, not by **how many destinations** there are.

## 2. Why

- Mainstream indexes add +1 for every visa-free country. Visa-free entry to a microstate scores the same as entry to the United States.
- The motivating example: Malaysia ranks near the top on raw counts but needs a full, interview-based visa for the US. Singapore and Switzerland don't.
- A weighted index should show that difference and be honest about how it was weighted.

## 3. Proposals in this folder

| Doc | What it covers | Status |
|---|---|---|
| **This page** | Shared model, access values, plan of record | Current |
| [Methodology B — Global Cities](methodology-b-global-cities.md) | Destination value from global cities: connectivity, finance, tourism and cost, plus an opinionated tier list | **Current direction** |
| Methodology A — Size-weighted (§5 below) | Destination value from GDP, population and area | Set aside |

## 4. Shared model

Every methodology uses the same frame. Only **Value(j)** changes between them.

```
Score(passport i) = Σ over destinations j ≠ home(i):  Value(j) × Access(i, j)
```

The score is shown as **"% of the world's value you can reach"**: the score divided by the total value of all destinations, so 100% means frictionless entry everywhere.

### Access (how hard is it to get in?)

| Entry type | Default value |
|---|---|
| Visa-free | 1.00 |
| Electronic travel authorisation (ESTA, eTA, ETA, K-ETA) | 0.90 |
| Visa on arrival | 0.70 |
| eVisa | 0.50 |
| Visa required (embassy / consulate) | 0.10 |
| No admission / travel ban | 0.00 |

**Conditional exemptions are ignored.** "Visa-free if you hold a US / Schengen / UK visa" only reflects the other document's power. These cases are scored at the passport's own base requirement.

## 5. Methodology A — Size-weighted (set aside)

```
Value(j) = ( GDP_j^α · Population_j^β · Area_j^γ ) ^ p
```

Set aside after review:
- **Land area** says nothing about how valuable a destination is.
- **GDP** rewards sheer size. China outweighs Singapore and the UAE by an order of magnitude, even though access to each is roughly as valuable to a traveller.

Two lessons carry into Methodology B:
- **The sliding exponent `p`.** It controls how much the biggest destinations dominate.
- **No log-plus-min-max scaling.** With log weights the US was worth only ~1.4× Malaysia, and min-max gave the smallest country a weight of 0.

## 6. Plan of record

```
Python script: fetch → clean → score → scores.json   (committed)
                                     → REPORT.md      (algorithm + complete ranking)
```

1. **Scoring script** (Python, pandas). One run produces every methodology's scores from one config file.
2. **`scores.json`**: per-passport scores and ranks, plus per-destination values.
3. **`REPORT.md`**:
   - The algorithm in plain language
   - The complete ranking: raw-count rank vs weighted rank, with rank shift
   - The Malaysia / Singapore / Switzerland showcase
   - The top bottlenecks for notable passports
4. **Review the ranking.** Then decide:
   - **Good as-is** → build a static website that reads `scores.json`.
   - **Depends heavily on knobs** → go dynamic, with sliders for the weights.

## 7. Data shared by all methodologies

| What | Source |
|---|---|
| Visa matrix (≈199 × 199) | Open passport-index CSV dataset (GitHub, open licence), at a pinned date |
| Country codes, territories | ISO-3166 alpha-3, plus a small mapping file for Hong Kong, Macau, Taiwan, Kosovo, Palestine, etc. |

Methodology-specific data is listed in each methodology doc.

## 8. Decided

- Nominal GDP only, wherever GDP appears at all.
- Conditional exemptions are ignored.
- One recent snapshot, no history.
- Script → static JSON → Markdown report first. Website and static vs dynamic come after reviewing the ranking.
- Land area is not used.

## 9. Still open

- Licences: MIT for code, CC BY for derived data?
- Schengen: count it as 29 separate destinations, or as one bloc (a single visa decision)?
- Frontend stack, once we get to the website.
