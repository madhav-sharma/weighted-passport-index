# Weighted Passport Index — Proposal

*Status: draft for discussion. Nothing is built yet.*

## 1. The idea in one line

Count passport access by **what a destination is worth**, not by **how many destinations** there are. A country is worth visiting for **its cities**: where business happens, where money flows, where people travel and where life is expensive.

## 2. Why

- Mainstream indexes add +1 for every visa-free country. Visa-free entry to a microstate scores the same as entry to the United States.
- The motivating example: Malaysia ranks near the top on raw counts but needs a full, interview-based visa for the US. Singapore and Switzerland don't.

## 3. What it should get right

- **The United States is a big deal.** It has several world cities, not one.
- **Russia, China, the UAE and Singapore are in the same league.** China's GDP shouldn't make it worth ten Singapores.
- **Small destinations still count, just a little.**
- **Every number can be traced back to a published source or a stated opinion.**
- **No GDP and no land area.** Both reward sheer size rather than how valuable a destination is.

## 4. The model

```
Score(passport i) = Σ over destinations j ≠ home(i):  Value(j) × Access(i, j)
```

The score is shown as **"% of the world's value you can reach"**: the score divided by the total value of all destinations, so 100% means frictionless entry everywhere.

### 4a. Access (how hard is it to get in?)

| Entry type | Default value |
|---|---|
| Visa-free | 1.00 |
| Electronic travel authorisation (ESTA, eTA, ETA, K-ETA) | 0.90 |
| Visa on arrival | 0.70 |
| eVisa | 0.50 |
| Visa required (embassy / consulate) | 0.10 |
| No admission / travel ban | 0.00 |

**Conditional exemptions are ignored.** "Visa-free if you hold a US / Schengen / UK visa" only reflects the other document's power. These cases are scored at the passport's own base requirement.

### 4b. Value (what is a destination worth?)

Value combines two layers:

```
Value(j) = λ · DataValue(j)  +  (1 − λ) · OpinionValue(j)
```

| Layer | What it is | Why |
|---|---|---|
| **Data** | Computed from global-city benchmarks | Reproducible and cites its sources |
| **Opinion** | A hand-curated tier list with a one-line reason per country | Captures judgements that no benchmark encodes |

`λ` slides between the two:
- `1` = pure data
- `0` = pure opinion
- `0.5` = proposed default

The report always shows all three rankings side by side: data, opinion and blended.

## 5. Data layer

### 5a. City signals (four pillars)

| Pillar | Benchmark | Latest edition found | What it captures |
|---|---|---|---|
| **Connectivity** | GaWC *World According to GaWC* (Alpha++ … Sufficiency tiers) | 2024 | How tied a city is into the global business network |
| | *Alternate:* Kearney Global Cities Index | 2025 | |
| **Finance** | Z/Yen Global Financial Centres Index (120 centres) | GFCI 39, Mar 2026 | How financially important a city is |
| **Tourism** | Euromonitor Top 100 City Destinations (international arrivals) | 2025 | Where people actually go |
| **Cost / affluence** | Mercer Cost of Living, or EIU Worldwide Cost of Living | 2024–25 | High-value, high-spend places |

Each city gets a score of 0–100 on each pillar, based on its rank or tier. A city that isn't listed scores 0 on that pillar.

```
CityScore = w_conn · Connectivity + w_fin · Finance + w_tour · Tourism + w_cost · Cost
```

Default weights are equal (0.25 each), all configurable.

### 5b. From cities to a country — the sliding scale

Sort a country's cities by `CityScore`, then add them with diminishing returns:

```
DataValue(j) = c₁ + d·c₂ + d²·c₃ + d³·c₄ + …   (+ a small floor so every country counts)
```

- **`d` is the depth dial:**
  - `d = 0`: only the best city counts. Singapore ≈ the US.
  - `d = 0.5` (proposed default): extra world cities add real value. New York + LA + SF + Chicago + Miami lift the US clear of the field.
  - `d = 1`: plain sum, so countries with many cities dominate.
- **Hong Kong, Macau and Taiwan are their own destinations,** because the visa matrix treats them separately. Their cities do not count towards China.

### 5c. Data notes

- **We store only ranks and tiers, with citations.** We don't redistribute full proprietary datasets. Licences are confirmed per source before committing.
- **Some benchmarks have quirks:**
  - Mecca ranks highly on tourism but is closed to non-Muslims.
  - Moscow is currently excluded from GFCI.
  - Airport hub rankings (e.g. OAG Megahubs) measure transfers, not destination value, so they are not used.
- **The data alone probably won't put Russia level with the UAE.** Sanctions have pushed Moscow down on finance and tourism. This is one reason the opinion layer exists.

## 6. Opinion layer

A YAML file assigns every country to a tier, with a one-line reason.

| Tier | Value | Illustrative members (draft, to be edited) |
|---|---|---|
| **S** | 100 | United States |
| **A** | 50 | UK, China, Russia, UAE, Singapore, Japan, Canada, Australia, Hong Kong, the large Schengen economies |
| **B** | 20 | South Korea, India, Saudi Arabia, Türkiye, Brazil, Mexico, Thailand, … |
| **C** | 8 | Most mid-sized economies and major tourist countries |
| **D** | 3 | Smaller countries |
| **E** | 1 | Microstates and hard-to-reach territories |

- Tier values are knobs too. The gap between S and A decides how much US access matters.
- The file is explicitly opinionated and versioned. Disagreements become pull requests, not hidden constants.

## 7. Other data

| What | Source |
|---|---|
| Visa matrix (≈199 × 199) | Open passport-index CSV dataset (GitHub, open licence), at a pinned date |
| Country codes, territories | ISO-3166 alpha-3, plus a small mapping file for Hong Kong, Macau, Taiwan, Kosovo, Palestine, etc. |
| City → country mapping | Built alongside the city benchmarks |

## 8. Plan

```
Python script: fetch → clean → score → scores.json   (committed)
                                     → REPORT.md      (algorithm + complete ranking)
```

1. **Scoring script** (Python, pandas). All knobs (access values, pillar weights, `d`, `λ`, tier values) live in one config file.
2. **`scores.json`:**
   - Per passport: the raw count, plus data, opinion and blended scores and ranks
   - Per destination: the value from each layer and its top contributing cities
3. **`REPORT.md`:**
   - The algorithm in plain language
   - The complete passport ranking: raw vs data vs opinion vs blended, with rank shifts
   - A destination value table: what each country is worth, and why
   - The Malaysia / Singapore / Switzerland showcase
   - Bottlenecks for notable passports
4. **Review the ranking.** Then decide:
   - **Stable and convincing** → build a static website that reads `scores.json`.
   - **Depends heavily on knobs** → go dynamic, with sliders.

## 9. How we'll judge it

These are not tests that force an answer. They are a checklist for reading the report:

- [ ] US access is the single largest destination value.
- [ ] China, Russia, the UAE and Singapore land within roughly the same range.
- [ ] Malaysia falls behind Singapore and Switzerland, and the report shows why (bottlenecks).
- [ ] No destination has value 0 (the floor works).
- [ ] Rankings don't flip wildly when `d` or `λ` move a little.

## 10. Decided

- No GDP and no land area in destination value.
- Conditional exemptions are ignored.
- One recent snapshot, no history.
- Script → static JSON → Markdown report first. The website comes after reviewing the ranking.

## 11. Still open

- Should the cost pillar be in at all? Expensive often tracks rich and desirable, but it also rewards places that are simply costly.
- Schengen: count it as 29 separate destinations, or as one bloc (a single visa decision)?
- Should we use the GaWC tiers or the Kearney GCI for connectivity, or average both?
- Should tourism use city arrivals (Euromonitor) or country arrivals (UN Tourism, which is open data)?
- Who owns the tier list, and how are changes reviewed?
- Licences: MIT for code, CC BY for derived data?
