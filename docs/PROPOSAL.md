# Weighted Passport Index — Proposal

*Status: draft for discussion. Nothing is built yet.*

## 1. The idea in one line

Count passport access by **what a destination is worth**, not by **how many destinations** there are. Present it on a polished, interactive website for one recent snapshot.

## 2. Why

- Mainstream indexes add +1 for every visa-free country. Visa-free entry to a microstate scores the same as entry to the United States.
- The motivating example: Malaysia ranks near the top on raw counts but needs a full, interview-based visa for the US. Singapore and Switzerland don't.
- A weighted index should show that difference, and let people see **how much** it depends on the weighting chosen.

## 3. Scope

**In scope (v1):**
- One recent snapshot of visa rules and country data
- A website as the main product

**Not now:**
- Historical trends
- Travel-demand weighting
- Visa cost and wait-time penalties
- PPP GDP

## 4. The model

```
Score(passport i) = Σ over destinations j ≠ home(i):  Weight(j) × Access(i, j)
```

Shown as **"% of the world you can reach"**: the score divided by the total weight of all destinations, so 100% means frictionless entry everywhere.

### 4a. Access (how hard is it to get in?)

| Entry type | Default value |
|---|---|
| Visa-free | 1.00 |
| Electronic travel authorisation (ESTA, eTA, ETA, K-ETA) | 0.90 |
| Visa on arrival | 0.70 |
| eVisa | 0.50 |
| Visa required (embassy / consulate) | 0.10 |
| No admission / travel ban | 0.00 |

**Conditional exemptions are ignored.** "Visa-free if you hold a US / Schengen / UK visa" only reflects the other document's power, not this passport's. These cases are scored at the passport's own base requirement.

### 4b. Weight (how much is a destination worth?)

```
Weight(j) = ( GDP_j^α · Population_j^β · Area_j^γ ) ^ p
```

- **GDP is nominal, in US dollars.**
- **α, β, γ** set the mix of economy, people and land. Defaults: 0.5 / 0.3 / 0.2.
- **p** sets how much big countries dominate:
  - `p → 0`: every country counts the same (the classic raw count)
  - `p ≈ 0.3–0.5`: big countries matter a lot, small ones still count (proposed default)
  - `p = 1`: weight is proportional to size
- Both the raw-count index and a fully size-proportional index are settings of the same formula.

## 5. Changes from the original brief

| Original brief | Proposal | Why |
|---|---|---|
| Weight = α·log GDP + β·log Pop + γ·log Area | Weight = (GDP^α · Pop^β · Area^γ)^p | With log scaling the US is worth only ~1.4× Malaysia, so the paradox mostly disappears |
| Min-max scale weights to 0–100 | Weights as shares of the world total | Min-max gives the smallest country a weight of exactly 0 |
| 4 friction levels | 6 levels | ETAs and eVisas are different from both visa-free entry and embassy visas |
| Test asserts "Malaysia must drop" | Malaysia / Singapore / Switzerland is a **showcase**; tests check the maths | Requiring a particular answer in a test is tuning the model to fit the conclusion |
| Python script with printed tables | Website with live sliders | Readers can see for themselves how sensitive the ranking is |

## 6. Data

| What | Source |
|---|---|
| Visa matrix (≈199 × 199) | Open passport-index CSV dataset (GitHub, open licence), at a pinned date |
| Nominal GDP (USD) | World Bank WDI; IMF WEO to fill gaps (e.g. Taiwan) |
| Population, land area | World Bank WDI |

- Everything is keyed on ISO-3166 alpha-3 codes.
- One small mapping file covers disputed or partially recognised entities.
- The cleaned snapshot is committed to the repo, so the site builds without network access.

## 7. Architecture

```
 Python (offline, run occasionally)        Static website (GitHub Pages)
 ┌──────────────────────────────┐          ┌──────────────────────────────────┐
 │ fetch → clean → validate     │  JSON    │ scoring engine (TypeScript)      │
 │ → snapshot.json              │ ───────► │ runs in the browser, live sliders│
 └──────────────────────────────┘          │ map · leaderboard · passport page│
                                           └──────────────────────────────────┘
```

- **Single scoring implementation.** It lives in the frontend and recomputes about 40k cells per slider move, which is instant.
- **Python only prepares data.**
- **No backend and no running costs.**

## 8. The website

| View | What it shows |
|---|---|
| **Home / hero** | The Malaysia vs Singapore vs Switzerland story: "same count, very different reach" |
| **Leaderboard** | All passports ranked by weighted score, with raw-count rank beside it and a **rank-shift** arrow |
| **World map** | Choropleth of passport power. Select a passport and the map recolours by its access to each country |
| **Passport page** | Score, rank, access breakdown, and its **biggest bottlenecks** (highest-weight countries that need an embassy visa) |
| **Compare** | Two or three passports side by side |
| **Tune it** | Sliders for α, β, γ, p and the access values; every view updates live, and settings are shareable via the URL |
| **Methodology** | Formula, data sources, snapshot date, caveats |

Design goals:
- Fast, mobile-friendly, and works in light and dark modes
- Animated transitions when rankings change
- Accessible colour scales

## 9. Phases

| Phase | Outcome |
|---|---|
| 0 | Repo skeleton, licences, data-source check |
| 1 | Data pipeline → committed `snapshot.json` |
| 2 | Scoring engine in TypeScript, plus unit tests |
| 3 | Website: leaderboard, map, passport page, sliders |
| 4 | Polish: hero story, compare view, methodology, deploy to GitHub Pages |

## 10. Decided

- Nominal GDP only.
- Conditional exemptions ("if you hold a US visa") are ignored.
- One recent snapshot, no history.
- Website is the main deliverable.

## 11. Still open

- Should area be included by default, or should γ start at 0?
- Licences: MIT for code, CC BY for derived data?
- Frontend stack (proposed: Vite + Svelte + D3).
