# Weighted Passport Index — Proposal

*Status: draft for discussion. Nothing is built yet.*

## 1. The idea in one line

Count passport access by **what a destination is worth**, not by **how many destinations** there are.

## 2. Why

- Mainstream indexes add +1 for every visa-free country. Visa-free entry to a microstate scores the same as entry to the United States.
- The motivating example: Malaysia ranks near the top on raw counts but needs a full, interview-based visa for the US. Singapore and Switzerland don't.

## 3. Docs

| Doc | What it covers |
|---|---|
| **This page** | The scoring model, access values, data, plan and decisions |
| [Methodology — Global Cities](methodology.md) | How much each destination is worth |

## 4. The model

```
Score(passport i) = Σ over destinations j ≠ home(i):  Value(j) × Access(i, j)
```

- **Value(j)** is what destination j is worth. See [the methodology](methodology.md).
- **Access(i, j)** is how hard it is for passport i to get into j.

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

## 5. Data

| What | Source |
|---|---|
| Visa matrix (≈199 × 199) | Open passport-index CSV dataset (GitHub, open licence), at a pinned date |
| Country codes, territories | ISO-3166 alpha-3, plus a small mapping file for Hong Kong, Macau, Taiwan, Kosovo, Palestine, etc. |
| Destination value inputs | City benchmarks and override list (see [the methodology](methodology.md)) |

## 6. Plan

```
Python script: fetch → clean → score → scores.json   (committed)
                                     → REPORT.md      (algorithm + complete ranking)
```

1. **Scoring script** (Python, pandas). All knobs live in one config file.
2. **`scores.json`:**
   - Per passport: the raw count, plus weighted scores and ranks
   - Per destination: its value and what drives it
3. **`REPORT.md`:**
   - The algorithm in plain language
   - The complete passport ranking: raw-count rank vs weighted rank, with rank shift
   - A destination value table
   - The Malaysia / Singapore / Switzerland showcase
   - Bottlenecks for notable passports
4. **Review the ranking.** Then decide:
   - **Stable and convincing** → build a static website that reads `scores.json`.
   - **Depends heavily on knobs** → go dynamic, with sliders.

## 7. Decided

- No GDP and no land area in destination value.
- Conditional exemptions are ignored.
- Schengen counts as one destination (one bloc).
- The US, Schengen, the UK and Japan are pinned at the maximum value. Every other destination is valued from city benchmarks. There are no hand-assigned tiers.
- One recent snapshot, no history.
- Script → static JSON → Markdown report first. The website comes after reviewing the ranking.

## 8. Still open

- Licences: MIT for code, CC BY for derived data?
- Methodology-specific questions are in [the methodology](methodology.md#7-open-questions).
