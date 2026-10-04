"""Weighted Passport Index: destination values and passport scores.

Reads the visa matrix and city benchmarks in data/ and writes:
  results/destination_values.json  what each destination is worth
  results/passport_index.json      how much of that value each passport reaches

Run: python score.py
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUT = ROOT / "results"

# --- Knobs -------------------------------------------------------------------

# How easy entry is, by visa category.
ACCESS = {
    "visa free": 1.0,
    "eta": 0.9,
    "visa on arrival": 0.7,
    "e-visa": 0.5,
    "visa required": 0.1,
    "no admission": 0.0,
}

# Categories a conventional index counts as "access" (for the raw-count comparison).
RAW_COUNT_CATEGORIES = {"visa free", "eta", "visa on arrival"}

# Categories that need a visa application. Used for the Japan strictness check.
STRICT_CATEGORIES = {"e-visa", "visa required", "no admission"}

# GaWC tier -> connectivity score.
GAWC_TIER_SCORE = {
    "Alpha++": 100, "Alpha+": 90, "Alpha": 80, "Alpha-": 70,
    "Beta+": 60, "Beta": 50, "Beta-": 40,
    "Gamma+": 30, "Gamma": 25, "Gamma-": 20,
    "High Sufficiency": 10, "Sufficiency": 5,
}

PILLAR_WEIGHTS = {"connectivity": 0.25, "finance": 0.25, "tourism": 0.25, "cost": 0.25}

# A country's best city counts in full, its 2nd city DEPTH times, its 3rd DEPTH^2 times, ...
DEPTH = 0.5

# Minimum value of any destination, so every country counts a little.
FLOOR = 1.0

# Destinations pinned at the maximum value, by hand.
PINNED = {
    "USA": "The world's most important destination for business, finance and travel",
    "SCHENGEN": "One visa opens Paris, Frankfurt, Amsterdam, Milan and 25+ other countries",
    "GBR": "London is the world's most connected city",
}

# Japan is pinned too, if its entry is about as strict as the least strict pinned destination.
JAPAN_PIN = {
    "value": 100,
    "fallback": 75,
    "tolerance": 0.05,
    "reason": "A bucket-list destination and a proxy for wealth and status; its strict entry "
              "means easy access marks a strong passport",
}

# Hand-set values after reviewing the data. {"iso3": {"match": "ARE" | "value": 50, "reason": "..."}}
OVERRIDES = {}

SCHENGEN_MEMBERS = [
    "AUT", "BEL", "BGR", "HRV", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "ISL",
    "ITA", "LVA", "LIE", "LTU", "LUX", "MLT", "NLD", "NOR", "POL", "PRT", "ROU", "SVK", "SVN",
    "ESP", "SWE", "CHE",
]
# Microstates reachable only through the Schengen Area; folded into the bloc.
SCHENGEN_ENCLAVES = ["AND", "MCO", "SMR", "VAT"]
SCHENGEN = "SCHENGEN"

# Benchmark cities in territories that follow another country's visa rules.
TERRITORY_MAP = {
    "PRI": "USA", "GUM": "USA", "VIR": "USA", "ASM": "USA", "MNP": "USA",
    "JEY": "GBR", "GGY": "GBR", "IMN": "GBR",
}

# --- Loading -----------------------------------------------------------------


def category(requirement):
    """Map a dataset value to a visa category ('-1' means own country)."""
    r = str(requirement).strip().lower()
    if r == "-1":
        return None
    if r.isdigit():
        return "visa free"
    if r not in ACCESS:
        raise ValueError(f"Unknown visa requirement: {requirement!r}")
    return r


def load_visa():
    df = pd.read_csv(DATA / "raw" / "passport-index-tidy-iso3.csv", dtype=str)
    df.columns = ["passport", "destination", "requirement"]
    df["category"] = df["requirement"].map(category)

    corrections = pd.read_csv(DATA / "visa_corrections.csv", dtype=str)
    for c in corrections.itertuples():
        dests = SCHENGEN_MEMBERS + SCHENGEN_ENCLAVES if c.destination == SCHENGEN else [c.destination]
        mask = (df["passport"] == c.passport) & df["destination"].isin(dests) & df["category"].notna()
        if not mask.any():
            raise ValueError(f"Correction matches nothing: {c.passport} -> {c.destination}")
        df.loc[mask, "category"] = category(c.requirement)

    return df.pivot(index="passport", columns="destination", values="category"), len(corrections)


def unit_of(iso3):
    """The destination unit a country belongs to (Schengen members fold into one bloc)."""
    return SCHENGEN if iso3 in SCHENGEN_MEMBERS or iso3 in SCHENGEN_ENCLAVES else iso3


def rank_score(ranks):
    """Linear rank score: rank 1 -> 100, last rank -> 100/N."""
    n = ranks.max()
    return 100 * (n + 1 - ranks) / n


def load_cities(countries):
    """One row per (city, country) with a 0-100 score per pillar and a combined city score."""
    b = DATA / "benchmarks"
    gawc = pd.read_csv(b / "gawc.csv")
    gawc["connectivity"] = gawc["tier"].map(GAWC_TIER_SCORE)
    if gawc["connectivity"].isna().any():
        raise ValueError(f"Unknown GaWC tiers: {gawc[gawc['connectivity'].isna()]['tier'].unique()}")

    pillars = [gawc[["city", "country_iso3", "connectivity"]]]
    for name, file in [("finance", "gfci.csv"), ("tourism", "tourism.csv"), ("cost", "cost.csv")]:
        t = pd.read_csv(b / file)
        t[name] = rank_score(t["rank"])
        pillars.append(t[["city", "country_iso3", name]])

    cities = pillars[0]
    for p in pillars[1:]:
        cities = cities.merge(p, on=["city", "country_iso3"], how="outer")
    cities[list(PILLAR_WEIGHTS)] = cities[list(PILLAR_WEIGHTS)].fillna(0.0)
    cities["score"] = sum(cities[k] * w for k, w in PILLAR_WEIGHTS.items())

    cities["country_iso3"] = cities["country_iso3"].replace(TERRITORY_MAP)
    dropped = cities[~cities["country_iso3"].isin(countries)]
    cities = cities[cities["country_iso3"].isin(countries)].copy()
    cities["unit"] = cities["country_iso3"].map(unit_of)
    return cities.sort_values("score", ascending=False), dropped


# --- Scoring -----------------------------------------------------------------


def depth_sum(scores):
    """Best city in full, then each next city DEPTH times the previous weight."""
    return sum(s * DEPTH**k for k, s in enumerate(sorted(scores, reverse=True)))


def strictness(column, own_passports):
    """Share of foreign passports that need a visa application."""
    col = column.drop(index=[p for p in own_passports if p in column.index]).dropna()
    return float(col.isin(STRICT_CATEGORIES).mean())


def schengen_column(visa):
    """One access category per passport for the bloc: the most common across member columns,
    ties broken towards the more restrictive category."""
    members = visa[SCHENGEN_MEMBERS + SCHENGEN_ENCLAVES]
    out, disagreements = {}, {}
    for passport, row in members.iterrows():
        counts = row.dropna().value_counts()
        if counts.empty:
            continue
        top = counts[counts == counts.max()].index
        out[passport] = min(top, key=lambda c: ACCESS[c])
        if len(counts) > 1:
            disagreements[passport] = counts.to_dict()
    return pd.Series(out), disagreements


def main():
    countries = pd.read_csv(DATA / "countries.csv").set_index("iso3")["name"]
    visa, n_corrections = load_visa()
    cities, dropped = load_cities(set(countries.index))

    # Access matrix over destination units.
    units = sorted({unit_of(c) for c in visa.columns})
    access = pd.DataFrame(index=visa.index, columns=units, dtype=object)
    for u in units:
        if u != SCHENGEN:
            access[u] = visa[u]
    access[SCHENGEN], schengen_disagreements = schengen_column(visa)
    bloc_passports = [p for p in visa.index if unit_of(p) == SCHENGEN]
    access.loc[bloc_passports, SCHENGEN] = "visa free"  # freedom of movement within the bloc

    names = {u: countries.get(u, u) for u in units}
    names[SCHENGEN] = "Schengen Area"

    # Data value per unit, scaled so the weakest pinned destination's data value = 100.
    raw = {u: depth_sum(cities.loc[cities["unit"] == u, "score"]) for u in units}
    reference_units = list(PINNED) + ["JPN"]
    R = min(raw[u] for u in reference_units)

    def scaled(r):
        return max(FLOOR, min(100.0, 100 * r / R))

    value = {u: scaled(raw[u]) for u in units}
    how = {u: "data" for u in units}

    for u in PINNED:
        value[u], how[u] = 100.0, "pinned"

    strict = {u: strictness(access[u], bloc_passports if u == SCHENGEN else [u])
              for u in reference_units}
    japan_ok = strict["JPN"] >= min(strict[u] for u in PINNED) - JAPAN_PIN["tolerance"]
    value["JPN"] = JAPAN_PIN["value"] if japan_ok else JAPAN_PIN["fallback"]
    how["JPN"] = "pinned" if japan_ok else "pinned (fallback)"

    for u, o in OVERRIDES.items():
        value[u] = value[o["match"]] if "match" in o else o["value"]
        how[u] = "override"

    reasons = {**PINNED, "JPN": JAPAN_PIN["reason"], **{u: o["reason"] for u, o in OVERRIDES.items()}}

    # For a Schengen member's own passport, the bloc is worth the rest of the bloc.
    def rest_of_bloc(passport):
        others = cities[(cities["unit"] == SCHENGEN) & (cities["country_iso3"] != passport)]
        return min(100.0, 100 * depth_sum(others["score"]) / R)

    # --- Destination table ---
    destinations = []
    for u in units:
        uc = cities[cities["unit"] == u]
        destinations.append({
            "code": u,
            "name": names[u],
            "value": round(value[u], 2),
            "method": how[u],
            "reason": reasons.get(u),
            "data_value": round(scaled(raw[u]), 2),
            "raw_data_value": round(raw[u], 2),
            "cities": [
                {"city": c.city, "score": round(c.score, 1),
                 **{k: round(getattr(c, k), 1) for k in PILLAR_WEIGHTS}}
                for c in uc.head(5).itertuples()
            ],
            "city_count": int(len(uc)),
            "members": SCHENGEN_MEMBERS + SCHENGEN_ENCLAVES if u == SCHENGEN else None,
        })
    destinations.sort(key=lambda d: (-d["value"], d["name"]))
    for i, d in enumerate(destinations):
        d["rank"] = 1 + sum(e["value"] > d["value"] for e in destinations)

    # --- Passport index ---
    passports = []
    for p in visa.index:
        home = unit_of(p)
        v = dict(value)
        if home == SCHENGEN:
            v[SCHENGEN] = rest_of_bloc(p)
        else:
            del v[home]
        a = {u: ACCESS[access.at[p, u]] for u in v}
        total = sum(v.values())
        points = sum(v[u] * a[u] for u in v)

        cats = visa.loc[p].dropna()
        lost = sorted(((v[u] * (1 - a[u]), u) for u in v), reverse=True)
        passports.append({
            "code": p,
            "name": countries[p],
            "score": round(100 * points / total, 2),
            "points": round(points, 2),
            "max_points": round(total, 2),
            "raw_count": int(cats.isin(RAW_COUNT_CATEGORIES).sum()),
            "categories": {c: int((cats == c).sum()) for c in ACCESS},
            "bottlenecks": [
                {"code": u, "name": names[u], "value": round(v[u], 2),
                 "category": access.at[p, u], "lost_points": round(loss, 2)}
                for loss, u in lost[:5] if loss > 0
            ],
        })

    df = pd.DataFrame(passports)
    df["rank"] = df["score"].rank(ascending=False, method="min").astype(int)
    df["raw_rank"] = df["raw_count"].rank(ascending=False, method="min").astype(int)
    for p, r, rr in zip(passports, df["rank"], df["raw_rank"]):
        p["rank"], p["raw_rank"], p["rank_shift"] = int(r), int(rr), int(rr - r)
    passports.sort(key=lambda p: (p["rank"], p["name"]))

    meta = {
        "sources": json.loads((DATA / "sources.json").read_text()),
        "knobs": {
            "access": ACCESS, "pillar_weights": PILLAR_WEIGHTS, "depth": DEPTH, "floor": FLOOR,
            "gawc_tier_score": GAWC_TIER_SCORE, "scale_reference_raw": round(R, 2),
        },
        "japan_check": {
            "strictness": {u: round(s, 3) for u, s in strict.items()},
            "passes": bool(japan_ok),
            "tolerance": JAPAN_PIN["tolerance"],
        },
        "visa_corrections_applied": n_corrections,
        "schengen_column_disagreements": schengen_disagreements,
        "benchmark_cities_dropped": sorted(f"{c.city} ({c.country_iso3})" for c in dropped.itertuples()),
    }

    OUT.mkdir(exist_ok=True)
    (OUT / "destination_values.json").write_text(
        json.dumps({"meta": meta, "destinations": destinations}, indent=1, ensure_ascii=False))
    (OUT / "passport_index.json").write_text(
        json.dumps({"meta": meta, "passports": passports}, indent=1, ensure_ascii=False))
    print(f"{len(destinations)} destinations, {len(passports)} passports -> {OUT}/")


if __name__ == "__main__":
    main()
