# Weighted Passport Index — Proposal

*Status: draft for discussion. Nothing is built yet.*

## 1. The idea in one line

Count passport access by **what a destination is worth**, not by **how many destinations** there are — and make every assumption a visible, tunable knob.

## 2. Why

- Mainstream indexes add +1 for every visa-free country. Visa-free entry to a microstate scores the same as entry to the United States.
- The motivating example: Malaysia ranks near the top on raw counts but needs a full, interview-based visa for the US. Singapore and Switzerland don't.
- A weighted index should show that difference, and show **how much** it depends on the weighting chosen.

## 3. The model

```
Score(passport i) = Σ over destinations j ≠ home(i):  Weight(j) × Access(i, j)
```

Reported as **"% of the reachable world"**: the score divided by the total weight of all destinations, so 100% means frictionless entry everywhere.

### 3a. Access (how hard is it to get in?)

A configurable lookup table, not hard-coded constants.

| Entry type | Starting value |
|---|---|
| Visa-free | 1.00 |
| Electronic travel authorisation (ESTA, eTA, ETA, K-ETA) | 0.90 |
| Visa on arrival | 0.70 |
| eVisa | 0.50 |
| Visa required (embassy / consulate) | 0.10 |
| No admission / travel ban | 0.00 |

### 3b. Weight (how much is a destination worth?)

```
Weight(j) = ( GDP_j^α · Population_j^β · Area_j^γ ) ^ p
```

- **α, β, γ** set the mix of economy, people and land. Default 0.5 / 0.3 / 0.2.
- **p** sets how much big countries dominate:
  - `p → 0`: every country counts the same (the classic raw count)
  - `p ≈ 0.3–0.5`: big countries matter a lot, small ones still count (proposed default)
  - `p = 1`: weight is proportional to size
- The two mainstream views are both special cases of this one formula.

## 4. Changes from the original brief

| Original brief | Proposal | Why |
|---|---|---|
| Weight = α·log GDP + β·log Pop + γ·log Area | Weight = (GDP^α · Pop^β · Area^γ)^p | With log scaling the US is worth only ~1.4× Malaysia, so the gap the brief wants to show mostly disappears |
| Min-max scale weights to 0–100 | Report weights as shares of the world total | Min-max gives the smallest country a weight of exactly 0 |
| 4 friction levels (ETA lumped with visa-free) | 6 levels, all configurable | ETAs and eVisas are different from both visa-free entry and embassy visas |
| Test asserts "Malaysia must drop" | Malaysia / Singapore / Switzerland is a **showcase**; tests check how the maths behaves | A test that requires a particular answer is tuning the model to fit the conclusion |
| Single ranking | Ranking **plus a sensitivity band** across the parameter space | A rank that flips under small parameter changes shouldn't be presented as fact |

## 5. Data

| What | Source | Notes |
|---|---|---|
| Visa matrix (≈199 × 199) | Open passport-index CSV dataset (GitHub, open licence) | Snapshot is versioned in the repo; record the date |
| GDP (nominal, PPP as option) | World Bank WDI API; IMF WEO to fill gaps | Gaps include Taiwan and some territories |
| Population, land area | World Bank WDI | — |
| *(Phase 2)* Travel demand | UN Tourism arrivals / bilateral flows | Optional "where people actually go" weight |

Everything is keyed on ISO-3166 alpha-3 codes, with an explicit mapping file for disputed or partially recognised entities.

## 6. Deliverables

1. **Data pipeline** that fetches, cleans and caches the inputs, then writes one tidy parquet/CSV per snapshot.
2. **Scoring engine** (Python, pandas/numpy): pure functions, every parameter in one config file.
3. **Reports**
   - Top N passports by weighted score, with raw rank and **rank shift**
   - `bottlenecks(passport)`: the highest-weight destinations that block this passport
   - Malaysia / Singapore / Switzerland comparison table
   - Sensitivity view: rank range for each passport across parameter sweeps
4. **Tests** for the maths (monotonicity, the `p → 0` limit equalling raw counts, home country excluded) and for data integrity (no missing weights, matrix is square).
5. *(Later)* A static web page with sliders for α, β, γ and p.

## 7. Phases

| Phase | Outcome |
|---|---|
| 0 | Repo skeleton, licence, data-source and licence check |
| 1 | Ingest + clean data, frozen snapshot committed |
| 2 | Scoring engine + CLI + tests |
| 3 | Reports: rank shift, bottlenecks, showcase table |
| 4 | Sensitivity analysis + write-up of findings |
| 5 | *(Optional)* Interactive web page, travel-demand weighting, cost/wait-time penalties |

## 8. Open questions

- Should the default be nominal GDP or PPP?
- Should area be included at all, or left at γ = 0 by default?
- How do we treat conditional entry, e.g. "visa-free if you already hold a US visa"?
- How often do we refresh snapshots, and do we keep history so trends can be shown?
- Licence for the code (MIT?) and for the derived data (CC BY?).
