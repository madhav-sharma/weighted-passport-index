# Methodology B — Global Cities

*Status: draft for discussion. Part of the [proposals](README.md).*

## 1. The idea in one line

A country is worth visiting for **its cities**: where business happens, where money flows, where people travel and where life is expensive. Value comes from those cities, not from GDP, population or land.

## 2. What it should get right

- **The United States is a big deal.** It has several world cities, not one.
- **Russia, China, the UAE and Singapore are in the same league.** China's GDP shouldn't make it worth ten Singapores.
- **Small destinations still count, just a little.**
- **Every number can be traced back to a published source or a stated opinion.**

## 3. Two layers

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

## 4. Data layer

### 4a. City signals (four pillars)

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

### 4b. From cities to a country — the sliding scale

Sort a country's cities by `CityScore`, then add them with diminishing returns:

```
DataValue(j) = c₁ + d·c₂ + d²·c₃ + d³·c₄ + …   (+ a small floor so every country counts)
```

- **`d` is the depth dial:**
  - `d = 0`: only the best city counts. Singapore ≈ the US.
  - `d = 0.5` (proposed default): extra world cities add real value. New York + LA + SF + Chicago + Miami lift the US clear of the field.
  - `d = 1`: plain sum, so countries with many cities dominate.
- **Hong Kong, Macau and Taiwan are their own destinations,** because the visa matrix treats them separately. Their cities do not count towards China.

### 4c. Data notes

- **We store only ranks and tiers, with citations.** We don't redistribute full proprietary datasets. Small factual extracts with attribution should be fine; we'll confirm licences per source before committing.
- **Some benchmarks have quirks:**
  - Mecca ranks highly on tourism but is closed to non-Muslims.
  - Moscow is currently excluded from GFCI.
  - Airport hub rankings (e.g. OAG Megahubs) measure transfers, not destination value, so they are not used.
- **The data alone probably won't put Russia level with the UAE.** Sanctions have pushed Moscow down on finance and tourism. This is one reason the opinion layer exists.

## 5. Opinion layer

A YAML file assigns every country to a tier, with a one-line reason.

| Tier | Value | Illustrative members (draft, to be edited) |
|---|---|---|
| **S** | 100 | United States |
| **A** | 50 | UK, China, Russia, UAE, Singapore, Japan, Canada, Australia, Hong Kong, the large Schengen economies |
| **B** | 20 | South Korea, India, Saudi Arabia, Türkiye, Brazil, Mexico, Thailand, Switzerland (if not counted with Schengen), … |
| **C** | 8 | Most mid-sized economies and major tourist countries |
| **D** | 3 | Smaller countries |
| **E** | 1 | Microstates and hard-to-reach territories |

- Tier values are knobs too. The gap between S and A decides how much US access matters.
- The file is explicitly opinionated and versioned. Disagreements become pull requests, not hidden constants.

## 6. Output

The same pipeline as the main proposal, with this methodology's columns added:

- **`scores.json`:** per passport, the raw count plus data, opinion and blended scores and ranks. Per destination, the value from each layer and its top contributing cities.
- **`REPORT.md`:**
  - The algorithm in plain language
  - The complete passport ranking: raw vs data vs opinion vs blended, with rank shifts
  - A destination value table: what each country is worth, and why
  - The Malaysia / Singapore / Switzerland showcase
  - Bottlenecks for notable passports

## 7. How we'll judge it

These are not tests that force an answer. They are a checklist for reading the report:

- [ ] US access is the single largest destination value.
- [ ] China, Russia, the UAE and Singapore land within roughly the same range.
- [ ] Malaysia falls behind Singapore and Switzerland, and the report shows why (bottlenecks).
- [ ] No destination has value 0 (the floor works).
- [ ] Rankings don't flip wildly when `d` or `λ` move a little. If they do, that argues for a dynamic site with sliders.

## 8. Open questions

- Should the cost pillar be in at all? Expensive often tracks rich and desirable, but it also rewards places that are simply costly.
- Should we use the GaWC tiers or the Kearney GCI for connectivity, or average both?
- Should the tourism pillar use city arrivals (Euromonitor) or country arrivals (UN Tourism, which is open data)?
- Who owns the tier list, and how are changes reviewed?
