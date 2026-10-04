# Methodology — Global Cities

*Status: draft for discussion. Part of the [proposal](README.md).*

## 1. The idea in one line

A country is worth visiting for **its cities**: where business happens, where money flows, where people travel and where life is expensive. Value comes from those cities, not from GDP, population or land.

## 2. What it should get right

- **The US, the Schengen Area and the UK are the top destinations.**
- **Russia and the UAE are about equal.** Dubai is in high demand, even among Russians, which makes up for the UAE's small size.
- **Japan is worth more than Russia,** and **China and Japan are not equal.**
- **China's GDP doesn't make it worth ten Singapores.**
- **Small destinations still count, just a little.**
- **Every number can be traced back to a published source or a stated override.**

## 3. Approach

```
Value(j) = DataValue(j)   (unless an override applies)
```

- **No hand-assigned tiers.** Tiers proved too coarse: every bucket mixed countries that aren't really equal.
- **Value comes from global-city benchmarks** (§4).
- **A short override list** fixes only the cases the data clearly gets wrong (§5).

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
- **Schengen is scored as one destination.** One visa covers the whole area, so its cities (Paris, Frankfurt, Amsterdam, Milan, …) are pooled into one bloc, not 29 separate countries.
- **Hong Kong, Macau and Taiwan are their own destinations,** because the visa matrix treats them separately. Their cities do not count towards China.

### 4c. Data notes

- **We store only published ranks and benchmark tiers, with citations.** We don't redistribute full proprietary datasets. Licences are confirmed per source before committing.
- **Some benchmarks have quirks:**
  - Mecca ranks highly on tourism but is closed to non-Muslims.
  - Moscow is currently excluded from GFCI.
  - Airport hub rankings (e.g. OAG Megahubs) measure transfers, not destination value, so they are not used.
- **Russia may come out below the UAE.** Sanctions have pushed Moscow down on finance and tourism. If the gap is large, Russia is the likely first override.

## 5. Overrides

A small YAML file that adjusts a country's value only where the data is clearly wrong.

| Field | Example |
|---|---|
| Country | `RUS` |
| Adjusted value | Set equal to the UAE's value |
| Reason | One line, shown in the report |

- **We look at the data first.** Overrides are added after reviewing the destination value table in the report, never in advance.
- **Every override is listed openly** in the report.
- **A growing list is a warning sign.** If it grows past a handful of countries, we fix the benchmarks or weights instead.

## 6. How we'll judge it

These are not tests that force an answer. They are a checklist for reading the report:

- [ ] The US, Schengen and the UK have the three largest destination values.
- [ ] Russia ≈ the UAE; Japan > Russia; China ≠ Japan.
- [ ] Malaysia falls behind Singapore and Switzerland, and the report shows why (bottlenecks).
- [ ] No destination has value 0 (the floor works).
- [ ] Rankings don't flip wildly when `d` or the pillar weights move a little.
- [ ] The override list stays short.

## 7. Open questions

- Should the cost pillar be in at all? Expensive often tracks rich and desirable, but it also rewards places that are simply costly.
- Should we use the GaWC tiers or the Kearney GCI for connectivity, or average both?
- Should tourism use city arrivals (Euromonitor) or country arrivals (UN Tourism, which is open data)?
- Who approves overrides, and how are changes reviewed?
