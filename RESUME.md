# Resume prompt — Weighted Passport Index

> **To resume, paste this into a new Claude Code session on this repo:**
>
> `Read RESUME.md at the repo root and follow it exactly. Start with the preflight in section 1 and stop if it fails.`

Everything below is written to that session.

---

## 0. Rules. Read these first. They are not optional.

The previous session went wrong because Claude kept working after its own environment had blocked it. These rules exist so that does not happen again.

### 0.1 The stop rule

If **Claude's own environment** limits a step, **stop that work immediately**. Examples:
- the network policy blocks a host (HTTP 403 / `EGRESS_BLOCKED` / CONNECT rejected)
- the web-search allowance is used up
- a tool is missing or disabled
- a permission is denied
- a rate limit or quota is hit

Then:
1. Commit and push whatever already exists.
2. Tell the user in a few lines: what is blocked (name the host or tool), and what they need to change. For network access, that's the cloud environment menu in the session title bar, then **Edit** → **Network access**. Docs: https://code.claude.com/docs/en/cloud-environments#network-access
3. Wait for the user. Do not continue on other parts of the same task "in the meantime" unless the user says so.

**Never work around a block.** Specifically, never:
- probe dozens of alternative hosts, mirrors, archives, proxies or readers
- mine GitHub or other code hosts for third-party copies of a dataset
- substitute an older edition, a different source, or a partial list for the one that was asked for
- fill gaps from memory, interpolate, or estimate values
- let subagents continue after any one of them hits a block

Any of these needs explicit approval from the user first.

### 0.2 Preflight before any data work

Run section 1 before starting any research or launching any agent. If anything in it fails, apply the stop rule.

### 0.3 Web-search budget

- WebSearch is capped at **about 200 calls per session**, and **all subagents share that budget**. Last session, the first wave of parallel agents spent all of it before the rest started.
- Prefer **direct fetches of the known primary URLs** in section 7 over searching.
- Before launching agents, give each one a written search cap, e.g. "at most 10 WebSearch calls". Keep the total well under the budget.
- If searches run out, apply the stop rule.

### 0.4 Agents and workflows

- Use multi-agent workflows only if the user opts in.
- Even then:
  - Run the preflight first.
  - Keep fan-out small, roughly 5 agents or fewer doing web research at once.
  - Copy the stop rule (0.1) and a search cap into **every** agent prompt.
  - Read agent results as they arrive, and stop the run as soon as one reports a block.

### 0.5 Data integrity

- Every value must come from a source you actually read in this session, with the URL and edition recorded.
- Never invent, interpolate or recall values from memory. A missing value stays missing and is reported.
- Watch for data that looks synthetic. Example: the current `gfci.csv` ratings drop by exactly 1 point at 95 of 116 steps.

### 0.6 Working style the user expects

- **Commit and push every change**, to branch `claude/sharp-volta-4m3cxs`. Small commits are fine. Never leave untracked or uncommitted files; a stop hook checks.
- Do **not** open a pull request unless asked. The repo is **public**: no secrets or private details in commits.
- Keep things simple. Don't over-engineer. Don't add scope the user didn't ask for.
- Do **not** build the website. The goal is to get the ranking right first.
- Ask the user when a decision is theirs: formula changes, overrides, category conventions, source substitutions. Don't decide those silently.
- Keep chat replies short and plain.

---

## 1. Preflight (do this first)

```bash
# 1. Proxy state
curl -sS "$HTTPS_PROXY/__agentproxy/status" | head -40

# 2. Every host this task needs must answer (any HTTP code other than 000/403 from the proxy)
for h in gawc.lboro.ac.uk www.lboro.ac.uk www.longfinance.net www.zyen.com www.euromonitor.com \
         www.mercer.com www.kearney.com en.wikipedia.org \
         travel.state.gov www.gov.uk www.mofa.go.jp www.nia.gov.cn u.ae www.canada.ca \
         immi.homeaffairs.gov.au www.ica.gov.sg www.immd.gov.hk www.k-eta.go.kr \
         indianvisaonline.gov.in visa.visitsaudi.com www.evisa.gov.tr www.thaievisa.go.th \
         www.immigration.govt.nz visitqatar.com www.boca.gov.tw www.imi.gov.my \
         www.irishimmigration.ie www.gov.il eur-lex.europa.eu travel-europe.europa.eu; do
  printf "%-32s " "$h"; curl -sS -o /dev/null -w "%{http_code}\n" --max-time 15 "https://$h/" 2>&1 | tail -1
done

# 3. Python deps
pip install -q pandas numpy
```

Then make **one** WebSearch call, e.g. "GFCI 40 report", to confirm search works.

**If any benchmark host (first 8 hosts) is blocked, or search fails → stop rule.**
- Recommend that the user set Network access to the broadest level for this work, or allow at least the hosts above.
- Visa hosts that are blocked → list them to the user and ask how to proceed. Don't work around them.

---

## 2. The project in brief

The Weighted Passport Index counts passport access by **what each destination is worth**, not by how many destinations there are.

```
Score(passport i) = Σ_{j ≠ home(i)} Value(j) × Access(i, j)  /  Σ_{j ≠ home(i)} Value(j)     (shown as %)
```

The full design is in [`proposals/README.md`](proposals/README.md) (home page) and [`proposals/methodology.md`](proposals/methodology.md).

---

## 3. Decisions already made by the user. Do not reopen them.

- **No GDP and no land area** in destination value.
- **Conditional exemptions are ignored.** "Visa-free if you hold a US/UK/Schengen visa" is scored at the passport's base requirement.
- **Access values:**

  | Entry type | Access |
  |---|---|
  | Visa-free | 1.0 |
  | ETA (ESTA, eTA, ETA, K-ETA, NZeTA, ETIAS) | 0.9 |
  | Visa on arrival | 0.7 |
  | eVisa | 0.5 |
  | Visa required | 0.1 |
  | No admission | 0.0 |

- **The Schengen Area is one destination** (one bloc). Andorra, Monaco, San Marino and the Vatican are folded into it.
- **Pinned at the maximum value of 100:**
  - The US, Schengen and the UK.
  - **Japan** too, *if* its entry is about as strict as the least strict of those three. Otherwise Japan gets **75**. The reason for pinning Japan: it's a bucket-list destination and a proxy for wealth and status.
- **Every other destination is valued from city benchmarks:**
  - Four pillars: connectivity (GaWC), finance (GFCI), tourism (Euromonitor arrivals) and cost (most expensive cities).
  - Equal weights.
  - Cities are summed with a depth dial `d = 0.5`: best city in full, 2nd × 0.5, 3rd × 0.25, …
  - A floor ensures every country is worth a little.
- **No hand-assigned tiers.** Overrides only after reviewing the data, each with a stated reason, and the list should stay short.
- **One recent snapshot, no history.** Script → JSON → Markdown report first; the website comes later, after the ranking is right.

### The user's sanity expectations (a checklist, not tests to force)

- The US, Schengen and the UK (and Japan) are at the top.
- **Russia ≈ the UAE.** Dubai is in high demand, even among Russians.
- Japan is worth more than Russia, and **China is not equal to Japan**.
- Malaysia ranks well below Singapore and Switzerland. The original motivation: Malaysia needs an embassy visa for the US.
- No destination has value 0.

---

## 4. Current state of the repo (as of 2026-10-04)

| Path | State |
|---|---|
| `proposals/README.md`, `proposals/methodology.md` | Design docs, up to date with the decisions above |
| `data/raw/passport-index-tidy-iso3.csv` | Visa matrix: 199 × 199, snapshot of **17 Feb 2026** from github.com/imorte/passport-index-data (MIT). Never edit it; corrections go in `data/visa_corrections.csv` |
| `data/countries.csv` | ISO3 → country name for the 199 entries |
| `data/benchmarks/*.csv` | **Draft, unverified.** Status per file in [`data/benchmarks/README.md`](data/benchmarks/README.md). In short: GaWC complete but checked only against copies; GFCI ranks unverified and ratings look interpolated; **tourism is the 2019 edition (stale)**; cost is partial (103 of 226, gaps in the top 50); Kearney unusable (top 5 only) |
| `score.py` | Draft scoring script. **Never run yet.** Needs two missing inputs: `data/visa_corrections.csv` and `data/sources.json` |
| `notes/paused-run-2026-10-04/` | Raw, **unverified** agent reports from the stopped run: `benchmark_reports.json` (builders and verifiers) and `visa_findings.json` (visa checks) |

### Unverified visa findings to re-check (from `notes/paused-run-2026-10-04/visa_findings.json`)

The snapshot is 17 Feb 2026. Most of these agents could not reach official sites and worked from GitHub copies or memory. **Re-verify each finding against a live official source before using it.**

| Destination | First pass | Second pass | Gist |
|---|---|---|---|
| USA | 27 | 8 confirmed, 19 rejected | Proclamation 10998 (from 2026-01-01). Full bans → `no admission`: BFA, LAO, MLI, NER, SLE, SSD, SYR, PSE. The 19 partial bans are a **convention question for the user** |
| South Korea | 41 | 38 confirmed | Most of 40 visa-free rows → `eta` (K-ETA). Only 22 countries are exempt from K-ETA. Check whether that exemption was extended |
| Thailand | 35 | not run | 60-day exemption revised by Cabinet on 19 May and 14 Jul 2026 |
| China | 3 | 3 confirmed | GBR and CAN visa-free from 2026-02-17; MNG → visa required |
| Russia | 3 | 3 confirmed | SAU and MMR visa-free (2026); LCA → e-visa |
| UK | 2 | 2 confirmed | LCA and NIC → visa required (Mar 2026) |
| Hong Kong | 2 | 2 confirmed | IND and TWN → eta (pre-arrival registration) |
| Singapore | 1 | 1 confirmed | SSD → e-visa |
| India | 6 | 2 confirmed | ARE → e-visa (the VoA is conditional); MRT → e-visa |
| Japan | 1 | 0 confirmed | — |
| UAE | 4 | 0 confirmed | — |
| Saudi Arabia | 102 | not run | 98 rows `e-visa` → `visa required`: a **convention question** |
| Israel | 96 | not run | 89 rows `e-visa` → `visa required`: a **convention question** |
| Qatar | 86 | not run | 84 rows `visa on arrival` → `visa free`: a **convention question** |
| Türkiye | 13 | not run | Mixed |
| Taiwan | 16 | not run | Mixed |
| Ireland | 3 | not run | A June 2026 change |
| Brazil 2, Mexico 1, Malaysia 2 | | not run | Small |
| Schengen, Canada, Australia, New Zealand | 0 | — | Checked offline only; recheck live |

**Convention questions go to the user.** Examples: partial US bans; how to classify an online visa that needs full approval; a free "visa on arrival" waiver.

---

## 5. What went wrong last time (do not repeat)

1. I launched about 30 parallel agents (benchmark builders and verifiers, plus 24 visa checkers and their verifiers) **without checking network access or the search budget first**.
2. The first agents used up the **whole 200-search budget**. Later agents had none.
3. The network policy blocked almost every primary source; only GitHub was reachable.
4. Instead of stopping, agents went on a goose chase:
   - probed about 60 hosts
   - mined GitHub for third-party copies of datasets
   - used the **2019** tourism edition in place of 2025
   - pieced the Mercer list together from news snippets
   - worked from memory
5. I didn't stop the run when the first block was reported. The user had to step in.

---

## 6. The task: what to do, in order

The user's request:
- Produce a correct ranking with all data gathered and rechecked.
- Apply the formula to every destination except the pinned ones (Schengen, US, UK, Japan).
- Review the output and any incomplete data sources.
- Output **(1) a table of what each destination is worth** and **(2) the passport index for every passport**.
- One Python file produces the JSON rankings. Another converts JSON into Markdown tables; committing that one is optional.
- The JSON outputs and the final Markdown must be committed.
- Polish the methodology doc. **Do not build the website.**

**Steps (commit and push after each):**

1. **Preflight** (section 1). Stop if it fails.
2. **Benchmarks.** Fetch the primary sources directly (section 7) and fix each file in `data/benchmarks/`:
   - **GaWC 2024:** spot-check `gawc.csv` against the official page.
   - **GFCI:** check all 117 ranks and the real ratings against the GFCI 40 report PDF (Sept 2026).
   - **Tourism:** replace the 2019 edition with the latest Euromonitor *Top 100 City Destinations* (2025 edition, published Dec 2025, Bangkok #1 with 30.3m). **If the full 100-city arrivals list isn't publicly available, stop and ask the user which fallback to use.** Don't pick one yourself.
   - **Cost:** get the complete Mercer table (check for a 2025 or 2026 edition first). If it can't be obtained in full, stop and ask the user. Alternatives they could choose: EIU Worldwide Cost of Living, or Julius Baer.
   - **Kearney:** not used by `score.py`. Ask the user whether to complete it or delete it.
   - Write `data/sources.json`, which `score.py` reads: per benchmark, its edition, publication date, URLs and access date.
   - Update `data/benchmarks/README.md` with each file's status.
3. **Visa corrections.**
   - Re-verify the findings in section 4 against live official sources.
   - Raise the convention questions with the user.
   - Write confirmed corrections to `data/visa_corrections.csv`, with columns `passport,destination,requirement,effective_date,source,note`. `destination` may be `SCHENGEN`.
4. **Run `score.py`.** It has never been run, so fix bugs. City names must match exactly across the benchmark files, because they are joined on `(city, country_iso3)`. A known mismatch already: `St Petersburg` (gfci.csv) vs `Saint Petersburg` (tourism.csv). Check for others, e.g. by listing cities that appear in only one file.
5. **Review the output with the user** before adding overrides or changing the formula. Known concerns:
   - **Scaling cap.** Values are scaled so the weakest pinned destination's data value = 100, then capped at 100. China (Shanghai, Beijing, Shenzhen, Guangzhou …) may hit the cap and tie with the pinned four, which conflicts with "China ≠ Japan". India may also score high because it has many cities. Options: change the reference, lower `DEPTH`, or override.
   - **Russia vs the UAE.** In the draft files Moscow is only *Sufficiency* in GaWC 2024 and about 100th in GFCI, so Russia will likely land far below the UAE. The user expects them about equal, so Russia is the likely first override (match the UAE).
   - **Japan strictness check.** Report the strictness figures for all four pinned destinations.
   - **Rank stability.** Check the ranking at `DEPTH` 0.3 / 0.5 / 0.7 and with equal vs. adjusted pillar weights. This informs the later static-vs-dynamic site decision.
6. **Report.**
   - Write a small `render_report.py` (JSON → Markdown tables).
   - Write `REPORT.md`:
     - the method in plain language
     - **table 1: all destinations and their values**, with top cities
     - **table 2: all 199 passports**, with weighted rank, score, raw-count rank and rank shift
     - the Malaysia / Singapore / Switzerland showcase
     - top bottlenecks for notable passports
     - the data sources and their editions
     - the list of overrides
     - known limitations
7. **Polish `proposals/methodology.md`** so it matches what was actually implemented: formulas, scaling, Schengen handling, home exclusion and data sources.

---

## 7. Sources and URLs

| Data | Primary URL |
|---|---|
| GaWC 2024 | https://gawc.lboro.ac.uk/gawc-worlds/the-world-according-to-gawc/world-cities-2024/ |
| GFCI 40 (16 Sept 2026) | https://www.longfinance.net/media/documents/GFCI_40_Report_2026.09.16_v1.2.pdf (also zyen.com publications) |
| Euromonitor Top 100 City Destinations 2025 | https://www.euromonitor.com/newsroom/press-releases/december-2025/euromonitor-international-unveils-worlds-top-100-city-destinations-for-2025 |
| Mercer Cost of Living | https://www.mercer.com/insights/total-rewards/talent-mobility-insights/cost-of-living/ |
| Kearney GCI 2025 | https://www.kearney.com/service/global-business-policy-council/gcr/2025-full-report |
| Visa matrix | https://github.com/imorte/passport-index-data (check for a snapshot newer than 17 Feb 2026) |
| Visa policies | Official immigration / foreign-ministry sites of each destination, plus the Wikipedia "Visa policy of …" articles as a cross-check |

### How `score.py` works (draft)

1. Load the visa matrix and apply the corrections.
2. Fold the Schengen members and enclaves into one bloc. Each passport's access to the bloc is the most common category across member columns, with ties going to the stricter one.
3. Compute pillar scores per city, all 0–100:
   - GaWC tier → score (Alpha++ = 100 … Sufficiency = 5)
   - The other pillars use a linear rank score: `100 × (N + 1 − rank) / N`
4. Combine the pillars with equal weights into a city score.
5. Compute each country's raw data value with the depth sum.
6. Scale by `R` (the minimum raw value among US / Schengen / UK / Japan) and cap at 100, with a floor of 1.
7. Pin the US, Schengen and UK at 100, and run the Japan strictness check.
8. Score each passport over every destination except its home. For a Schengen member's own passport, the bloc's value is recomputed from the other members' cities.
9. Write `results/destination_values.json` and `results/passport_index.json`.
