# Methodology — Global Cities

*Status: draft for discussion. Part of the [proposal](README.md).*

## 1. The idea in one line

A country is worth visiting for **its cities**: where business happens, where money flows, where people travel and where life is expensive. Value comes from those cities, not from GDP, population or land.

## 2. What it should get right

- **The US, the Schengen Area and the UK are the top destinations,** at maximum value. **Japan joins them if its entry is as strict as theirs,** otherwise it sits just below at 75.
- **Russia and the UAE are about equal.** Dubai is in high demand, even among Russians, which makes up for the UAE's small size.
- **China's GDP doesn't make it worth ten Singapores.**
- **Small destinations still count, just a little.**
- **Every number can be traced back to a published source or a stated override.**

## 3. Approach

```
Value(j) = 100                         if j is pinned (US, Schengen, UK, Japan)
         = min(100, DataValue(j) / R)  otherwise
```

- **Four destinations are pinned at the maximum of 100** by hand (§5).
- **Every other destination is valued from global-city benchmarks** (§4) on the same 0–100 scale.
- **`R` is the lowest raw `DataValue` among the pinned four.** Scaling by it means a country that matches the weakest pinned destination also scores 100, and none can exceed it.
- **No hand-assigned tiers.** Tiers proved too coarse: every bucket mixed countries that aren't really equal.

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

A small YAML file of hand-set values, each with a one-line reason shown in the report.

| Destination | Value | Reason |
|---|---|---|
| United States | 100 | The world's most important destination for business, finance and travel |
| Schengen Area (one bloc) | 100 | One visa opens Paris, Frankfurt, Amsterdam, Milan and 25+ other countries |
| United Kingdom | 100 | London is the world's most connected city |
| Japan | 100 *(conditional)* | Very strict entry: most passports need a visa, so access is a real mark of passport strength |

- **The benchmark values for the pinned four are still computed and shown** in the report, for transparency.
- **Japan's 100 must be confirmed by the visa data.** The script measures strictness as the share of the world's passports that need an embassy visa for Japan.
  - If Japan is about as strict as the least strict of the US, Schengen and the UK, it stays at 100.
  - If not, it drops to **75**.
  - The report shows the strictness of all four.
- **Further overrides are added only after reviewing the data,** never in advance. Russia is the likely candidate if it lands far below the UAE.
- **A growing list is a warning sign.** If it grows past a handful of countries, we fix the benchmarks or weights instead.

## 6. How we'll judge it

These are not tests that force an answer. They are a checklist for reading the report:

- [ ] No unpinned destination comes close to 100 without a clear reason.
- [ ] Russia ≈ the UAE.
- [ ] Malaysia falls behind Singapore and Switzerland, and the report shows why (bottlenecks).
- [ ] No destination has value 0 (the floor works).
- [ ] Rankings don't flip wildly when `d` or the pillar weights move a little.
- [ ] The override list stays short.

## 7. Open questions

- Should the cost pillar be in at all? Expensive often tracks rich and desirable, but it also rewards places that are simply costly.
- Should we use the GaWC tiers or the Kearney GCI for connectivity, or average both?
- Should tourism use city arrivals (Euromonitor) or country arrivals (UN Tourism, which is open data)?
- Who approves overrides, and how are changes reviewed?
