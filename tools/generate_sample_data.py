#!/usr/bin/env python3
"""Generate the fully synthetic sample-data universe for the HDL showcase.

Every value here is fake and generated from a fixed seed. The universe mirrors
the SHAPE of the real Historic Data Loading problem (8 source systems, exactly
535 data sheets of monthly Excel files, schema drift, messy filenames, dirty
values) with fictional accounts, amounts, and entities. Row counts are scaled
down so the demo runs in a browser.

    python3 tools/generate_sample_data.py

Outputs:
    sample-data/universe.js   (window.HDL_UNIVERSE = {...})
    sample-data/ABOUT.md      (human-readable description of the universe)
"""
import json
import os
import random
from datetime import date

SEED = 535
R = random.Random(SEED)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "sample-data")
TARGET_DATA_SHEETS = 535

MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def months(start, end):
    """Inclusive list of (year, month) from 'YYYY-MM' to 'YYYY-MM'."""
    (y0, m0), (y1, m1) = [tuple(map(int, s.split("-"))) for s in (start, end)]
    out = []
    y, m = y0, m0
    while (y, m) <= (y1, m1):
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


# ── Canonical field catalogue ──────────────────────────────────────────────
# canonical -> [era-A name (2019 style), era-B name (2020-21 style), era-C name (2022+ style)]
ALIASES = {
    "as_of_date":        ["As At Date", "AS_OF_DATE", "As Of Date"],
    "account_number":    ["A/C No", "ACCOUNT_NO", "Account Number"],
    "customer_id":       ["Cust ID", "CUST_ID", "Customer ID"],
    "branch_code":       ["Br Code", "BRANCH_CD", "Branch Code"],
    "product_code":      ["Prod", "PRODUCT_CD", "Product Code"],
    "outstanding_balance": ["O/S Balance", "OS_BALANCE", "Outstanding Balance"],
    "currency":          ["Ccy", "CCY", "Currency"],
    "classification":    ["Class", "CLASSIFICATION", "Classification"],
    "days_past_due":     ["DPD", "DPD", "Days Past Due"],
    "provision_amount":  [None, "PROV_AMT", "Provision Amount"],          # appears 2020+
    "ifrs9_stage":       [None, None, "IFRS9 Stage"],                     # appears 2022+
    "interest_rate":     ["Int %", "INT_RATE", "Interest Rate"],
    "limit_amount":      ["Limit", "LIMIT_AMT", "Limit Amount"],
    "maturity_date":     ["Mat Date", "MATURITY_DT", "Maturity Date"],
    "booking_date":      ["Book Dt", "BOOKING_DT", "Booking Date"],
    "segment":           ["Seg", "SEGMENT", "Segment"],
    "status":            ["Sts", "STATUS", "Status"],
    "write_off_flag":    [None, "WO_FLAG", "Write-off Flag"],
    "restructured_flag": [None, "RESTR_FLAG", "Restructured Flag"],
    "legacy_ref":        ["Legacy Ref", None, None],                      # dropped after 2019
    # system-specific
    "od_limit":          ["OD Limit", "OD_LIMIT", "OD Limit"],
    "utilization_pct":   ["Util %", "UTIL_PCT", "Utilization %"],
    "excess_amount":     ["Excess", "EXCESS_AMT", "Excess Amount"],
    "emi_amount":        ["EMI", "EMI_AMT", "EMI Amount"],
    "tenor_months":      ["Tenor", "TENOR_M", "Tenor (Months)"],
    "disbursed_amount":  ["Disb Amt", "DISB_AMT", "Disbursed Amount"],
    "collateral_value":  ["Collateral", "COLL_VALUE", "Collateral Value"],
    "property_type":     ["Prop Type", "PROP_TYPE", "Property Type"],
    "property_value":    ["Prop Value", "PROP_VALUE", "Property Value"],
    "ltv_pct":           ["LTV", "LTV_PCT", "LTV %"],
    "down_payment":      ["Down Pmt", "DOWN_PMT", "Down Payment"],
    "card_type":         ["Card Type", "CARD_TYPE", "Card Type"],
    "credit_limit":      ["Cr Limit", "CREDIT_LIMIT", "Credit Limit"],
    "min_due":           ["Min Due", "MIN_DUE", "Minimum Due"],
    "total_due":         ["Tot Due", "TOTAL_DUE", "Total Due"],
    "cash_advance":      [None, "CASH_ADV", "Cash Advance"],
    "reward_points":     [None, None, "Reward Points"],
    "profit_rate":       ["Profit %", "PROFIT_RATE", "Profit Rate"],      # IB sheets
    "salary_transfer_flag": ["Sal Trf", "SAL_TRF_FLAG", "Salary Transfer"],
    "dbr_pct":           [None, "DBR_PCT", "DBR %"],
    "installment_amount": ["Inst Amt", "INST_AMT", "Installment Amount"],
    "facility_type":     ["Fac Type", "FACILITY_TYPE", "Facility Type"],
    "asset_description": ["Asset", "ASSET_DESC", "Asset Description"],
    "dealer_code":       ["Dealer", "DEALER_CD", "Dealer Code"],
    "entity_name":       ["Entity", "ENTITY_NAME", "Entity Name"],
    "trade_license_ref": ["TL Ref", "TL_REF", "Trade License Ref"],
    "turnover_band":     [None, "TURNOVER_BAND", "Turnover Band"],
    "rm_code":           ["RM", "RM_CODE", "RM Code"],
}

CORE = ["as_of_date", "account_number", "customer_id", "branch_code",
        "product_code", "outstanding_balance", "currency", "classification",
        "days_past_due", "provision_amount", "ifrs9_stage", "limit_amount",
        "booking_date", "segment", "status", "write_off_flag", "legacy_ref"]

# ── The 8 systems (names authorised by Hamdan, 2026-07-04) ─────────────────
SYSTEMS = [
    dict(id="od", name="OD", span=("2019-01", "2023-06"),
         extra=["od_limit", "utilization_pct", "excess_amount", "interest_rate",
                "maturity_date", "restructured_flag"],
         variant=dict(label="incl write-off", span=("2022-01", "2023-06")),
         sheet_names=["Base", "Base", "Data"], decoys=["Summary"]),
    dict(id="lai", name="LAI", span=("2019-01", "2023-06"),
         extra=["facility_type", "emi_amount", "tenor_months", "disbursed_amount",
                "collateral_value", "interest_rate", "maturity_date", "restructured_flag"],
         variant=dict(label="incl write-off", span=("2023-01", "2023-06")),
         sheet_names=["Base", "Position", "Data"], decoys=["Pivot"]),
    dict(id="mortgage", name="Mortgage", span=("2019-07", "2023-06"),
         extra=["property_type", "property_value", "ltv_pct", "down_payment",
                "emi_amount", "tenor_months", "interest_rate", "maturity_date"],
         sheet_names=["Data", "Base", "Mortgage"], decoys=["Notes"]),
    dict(id="cards", name="Cards", span=("2019-07", "2023-06"), dual=True,
         extra=["card_type", "credit_limit", "min_due", "total_due",
                "cash_advance", "reward_points"],
         sheet_names=[], decoys=["Summary"]),
    dict(id="personal_loans", name="Personal Loans", span=("2019-01", "2023-06"),
         extra=["emi_amount", "tenor_months", "disbursed_amount",
                "salary_transfer_flag", "dbr_pct", "interest_rate", "maturity_date"],
         sheet_names=["Base", "PL Data", "Data"], decoys=[]),
    dict(id="rakfin", name="RAKFIN", span=("2020-01", "2023-06"),
         extra=["facility_type", "installment_amount", "tenor_months",
                "down_payment", "dealer_code", "maturity_date"],
         sheet_names=["Data", "Data", "Sheet1"], decoys=[]),
    dict(id="auto", name="Auto", span=("2019-04", "2023-06"),
         extra=["asset_description", "dealer_code", "down_payment",
                "installment_amount", "tenor_months", "interest_rate", "maturity_date"],
         sheet_names=["Base", "Auto", "Data"], decoys=["Summary"]),
    dict(id="bbg_wbg", name="BBG WBG", span=("2019-01", "2023-06"), dual_files=["BBG", "WBG"],
         extra=["entity_name", "trade_license_ref", "facility_type", "turnover_band",
                "rm_code", "utilization_pct", "interest_rate", "maturity_date"],
         sheet_names=["Base", "Data", "Exposure"], decoys=["Notes"]),
]


def era_of(y, m):
    if y <= 2019:
        return 0
    if y <= 2021:
        return 1
    return 2


def cols_for(sys, era, ib=False):
    """Resolve the column-name list of a system for an era (with drift)."""
    fields = [f for f in CORE + sys["extra"]]
    if ib:  # Islamic cards sheet: profit rate instead of interest rate
        fields = [f for f in fields if f != "interest_rate"] + ["profit_rate"]
    out = []
    for f in fields:
        name = ALIASES[f][era]
        if name is not None:
            out.append(name)
    return out


def fname(sys, y, m, era, variant_label=None, part=None, rework=False):
    """Messy-but-generic filename in the era's dominant style."""
    nm = MON[m - 1]
    base = part or sys["name"]
    if era == 0:
        end_day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
        styles = [
            f"{base} position as at {end_day:02d} {nm} {y}",
            f"Monthly {base} {end_day:02d}.{m:02d}.{y}",
            f"{base} base {nm} {y} final",
        ]
    elif era == 1:
        styles = [
            f"{base}_{y}-{m:02d}",
            f"{base}_{y}_{m:02d} v2" if rework else f"{base}_{y}_{m:02d}",
            f"{base.upper().replace(' ', '_')}_{nm.upper()}{str(y)[2:]}",
        ]
    else:
        styles = [
            f"{base} {nm}'{str(y)[2:]}",
            f"{base} Base {nm}-{str(y)[2:]}",
            f"Copy of {base} {nm} {y}" if rework else f"{base} {nm} {y}",
        ]
    stem = R.choice(styles)
    if variant_label:
        stem += f" ({variant_label})"
    if rework and "v2" not in stem and "Copy of" not in stem:
        stem += " (2)"
    ext = R.choices([".xlsx", ".xlsb", ".xls", ".csv"], weights=[70, 15, 8, 7])[0]
    if ext == ".csv" and era == 0:
        ext = ".xlsx"  # keep csv in later eras only
    return stem + ext


def dirt_profile():
    return dict(
        dupRows=R.choice([0, 0, 0, 1, 2, 3, 5]),
        nullPct=R.choice([0, 1, 2, 4, 6, 9, 12]),
        numAsText=R.random() < 0.35,
        mixedDates=R.random() < 0.30,
        totalRow=R.random() < 0.25,
    )


def build_files():
    files = []
    for si, sys in enumerate(SYSTEMS):
        span = months(*sys["span"])
        for (y, m) in span:
            era = era_of(y, m)
            header_row = R.choices([1, 2, 3], weights=[55, 30, 15])[0]
            if sys.get("dual"):  # Cards: one file, CB + IB sheets
                cb = R.choice(["CB", "Conv"] if era < 2 else ["CB"])
                ib = R.choice(["IB", "Islamic"] if era < 2 else ["IB"])
                sheets = [
                    dict(name=cb, data=True, cols=cols_for(sys, era), rows=R.randint(300, 2200),
                         headerRow=header_row, dirt=dirt_profile()),
                    dict(name=ib, data=True, cols=cols_for(sys, era, ib=True), rows=R.randint(200, 1400),
                         headerRow=header_row, dirt=dirt_profile()),
                ]
                name = fname(sys, y, m, era)
                if name.endswith(".csv"):  # a CSV cannot carry two sheets
                    name = name[:-4] + ".xlsx"
                files.append(dict(sys=si, y=y, m=m, name=name, sheets=sheets))
            elif sys.get("dual_files"):  # BBG WBG: two files per month
                for part in sys["dual_files"]:
                    sheets = [dict(name=R.choice(sys["sheet_names"]), data=True,
                                   cols=cols_for(sys, era), rows=R.randint(150, 900),
                                   headerRow=header_row, dirt=dirt_profile())]
                    files.append(dict(sys=si, y=y, m=m,
                                      name=fname(sys, y, m, era, part=f"{part}"),
                                      sheets=sheets))
            else:
                sheets = [dict(name=R.choice(sys["sheet_names"]), data=True,
                               cols=cols_for(sys, era), rows=R.randint(300, 2500),
                               headerRow=header_row, dirt=dirt_profile())]
                files.append(dict(sys=si, y=y, m=m, name=fname(sys, y, m, era),
                                  sheets=sheets))
                v = sys.get("variant")
                if v and (y, m) in months(*v["span"]):
                    sheets_v = [dict(name=R.choice(sys["sheet_names"]), data=True,
                                     cols=cols_for(sys, era), rows=R.randint(300, 2500),
                                     headerRow=header_row, dirt=dirt_profile())]
                    files.append(dict(sys=si, y=y, m=m,
                                      name=fname(sys, y, m, era, variant_label=v["label"]),
                                      sheets=sheets_v))
        # decoy sheets on ~20% of this system's files (never on single-sheet CSVs)
        for f in [f for f in files if f["sys"] == si and not f["name"].endswith(".csv")]:
            if sys["decoys"] and R.random() < 0.20:
                f["sheets"].append(dict(name=R.choice(sys["decoys"]), data=False))
    return files


def top_up_rework(files):
    """Add deterministic 'v2 / Copy of' rework files until exactly 535 data sheets."""
    def count():
        return sum(1 for f in files for s in f["sheets"] if s.get("data"))
    need = TARGET_DATA_SHEETS - count()
    assert need >= 0, f"overshot target: {count()} > {TARGET_DATA_SHEETS} — tighten spans"
    candidates = [f for f in files if not SYSTEMS[f["sys"]].get("dual")]
    R.shuffle(candidates)
    for f in candidates[:need]:
        sys = SYSTEMS[f["sys"]]
        era = era_of(f["y"], f["m"])
        files.append(dict(sys=f["sys"], y=f["y"], m=f["m"],
                          name=fname(sys, f["y"], f["m"], era, rework=True),
                          sheets=[dict(name=R.choice(sys["sheet_names"] or ["Data"]), data=True,
                                       cols=cols_for(sys, era), rows=R.randint(300, 1500),
                                       headerRow=R.choice([1, 2]), dirt=dirt_profile())],
                          rework=True))
    assert count() == TARGET_DATA_SHEETS, f"got {count()} data sheets"
    return files


def mark_corrupt(files):
    """Exactly 9 corrupt files (echoes the real project's 9 problem files)."""
    idx = [i for i, f in enumerate(files) if f["name"].endswith((".xlsx", ".xlsb"))]
    R.shuffle(idx)
    for i in idx[:9]:
        if files[i]["name"].endswith(".xlsb"):
            files[i]["corrupt"] = "xlsb reader mismatch"
        else:
            files[i]["corrupt"] = R.choice(["styles.xml corrupt", "garbled sheet name"])


# ── Deep samples: fully materialised grids for the header-detection demo ──
BRANCHES = [f"BR-{n:03d}" for n in (4, 7, 12, 14, 21, 28, 33, 41, 52, 60, 77, 85)]
ENTITIES = ["Falcon Trading FZE", "Oasis Foods LLC", "Dune Logistics DMCC",
            "Pearl Interiors LLC", "Sahara Textiles FZE", "Marina Motors LLC",
            "Palm Contracting LLC", "Coral Pharma FZC"]


def cell_value(col, y, m, dirt):
    lc = col.lower()
    end_day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    if ("date" in lc or lc.endswith("_dt") or lc.endswith(" dt")
            or lc in ("as at date", "mat date")):
        if dirt["mixedDates"] and R.random() < 0.4:
            return f"{R.randint(1, end_day):02d}/{m:02d}/{str(y)[2:]}"
        return f"{y}-{m:02d}-{R.randint(1, end_day):02d}"
    if "a/c" in lc or "account" in lc:
        return f"{R.randint(10, 99)}{R.randint(10**7, 10**8 - 1)}"
    if "cust" in lc or "cif" in lc:
        return f"CIF{R.randint(100000, 999999)}"
    if "entity" in lc:
        return R.choice(ENTITIES)
    if "tl ref" in lc or "tl_ref" in lc or "license" in lc:
        return f"TL-{R.randint(10000, 99999)}"
    if "legacy" in lc:
        return f"LG-{R.randint(10000, 99999)}"
    if "branch" in lc or lc == "br code":
        return R.choice(BRANCHES)
    if "prod" in lc:
        return f"P{R.randint(10, 99)}"
    if "dealer" in lc:
        return f"DLR-{R.randint(100, 999)}"
    if lc == "rm" or "rm_code" in lc or lc == "rm code":
        return f"RM{R.randint(100, 999)}"
    if "ccy" in lc or "currency" in lc:
        return R.choices(["AED", "USD", "EUR"], weights=[88, 9, 3])[0]
    if lc == "dpd" or "past due" in lc:
        return R.choice([0, 0, 0, 0, 0, 0, R.randint(1, 30), R.randint(31, 180)])
    if "tenor" in lc:
        return R.choice([12, 24, 36, 48, 60, 84, 120, 240])
    if "points" in lc:
        return R.randint(0, 60000)
    if "%" in col or "rate" in lc or "pct" in lc or lc == "ltv":
        return round(R.uniform(0, 24), 2)
    if "flag" in lc or lc in ("sal trf",):
        return R.choice(["Y", "N", "N", "N"])
    if "stage" in lc:
        return R.choice([1, 1, 1, 2, 3])
    if "class" in lc:
        return R.choice(["Standard", "Standard", "Standard", "Watch", "Substandard"])
    if "status" in lc or lc == "sts":
        return R.choice(["Active", "Active", "Closed", "Dormant"])
    if "type" in lc or "seg" in lc or "band" in lc or "asset" in lc or "fac" in lc:
        return R.choice(["A", "B", "C", "Retail", "Corporate"])
    amt = round(R.lognormvariate(10, 1.2), 2)
    if dirt["numAsText"] and R.random() < 0.5:
        return f"{amt:,.2f}"
    return amt


def build_deep_samples(files):
    picks = []
    seen_sys = set()
    for i, f in enumerate(files):
        si = f["sys"]
        if si not in seen_sys and not f.get("corrupt"):
            picks.append(i)
            seen_sys.add(si)
    picks.append(next(i for i, f in enumerate(files) if f.get("corrupt")))
    picks.append(next(i for i, f in enumerate(files)
                      if f["sheets"][0].get("headerRow", 1) == 3 and not f.get("corrupt")))
    samples = {}
    for i in sorted(set(picks)):
        f = files[i]
        for s in f["sheets"]:
            if not s.get("data"):
                continue
            grid = []
            for t in range(s["headerRow"] - 1):  # junk rows above the header
                title = [None] * len(s["cols"])
                title[0] = R.choice([f"{SYSTEMS[f['sys']]['name']} monthly position",
                                     f"Report generated {f['y']}-{f['m']:02d}",
                                     "INTERNAL"])
                grid.append(title)
            grid.append(list(s["cols"]))
            n = R.randint(22, 38)
            rows = []
            for _ in range(n):
                rows.append([None if R.random() < s["dirt"]["nullPct"] / 100.0
                             else cell_value(c, f["y"], f["m"], s["dirt"])
                             for c in s["cols"]])
            for _ in range(min(s["dirt"]["dupRows"], 3)):
                rows.append(list(R.choice(rows)))
            R.shuffle(rows)
            grid.extend(rows)
            if s["dirt"]["totalRow"]:
                total = [None] * len(s["cols"])
                total[0] = "TOTAL"
                grid.append(total)
            samples[f"{i}:{s['name']}"] = dict(fileIndex=i, sheet=s["name"], grid=grid)
            break  # one sheet per picked file
    return samples


def build_dictionary():
    """Conformed data dictionary for the standardise/load chapter."""
    entries = []
    for canon, variants in ALIASES.items():
        entries.append(dict(
            canonical=canon,
            dtype=("date" if "date" in canon or canon.endswith("_dt")
                   else "decimal" if any(k in canon for k in
                                         ("amount", "balance", "value", "limit", "due",
                                          "pct", "rate", "payment", "advance", "points"))
                   else "int" if canon in ("days_past_due", "tenor_months", "ifrs9_stage")
                   else "string"),
            required=canon in ("as_of_date", "account_number", "outstanding_balance",
                               "currency", "classification"),
            variants=[v for v in variants if v],
        ))
    return entries


def main():
    files = top_up_rework(build_files())
    mark_corrupt(files)
    files.sort(key=lambda f: (f["sys"], f["y"], f["m"], f["name"]))
    deep = build_deep_samples(files)

    data_sheets = sum(1 for f in files for s in f["sheets"] if s.get("data"))
    total_rows = sum(s.get("rows", 0) for f in files for s in f["sheets"])
    # synthetic file sizes: proportional to rows x cols (browser-scale universe)
    for f in files:
        cells = sum(s.get("rows", 0) * len(s.get("cols", [])) for s in f["sheets"])
        f["sizeMB"] = round(max(0.2, cells * 11 / 1e6) * R.uniform(0.8, 1.3), 1)

    universe = dict(
        meta=dict(
            synthetic=True, seed=SEED, generated=str(date.today()),
            note="All data is fictional, generated by tools/generate_sample_data.py. "
                 "Sheet count mirrors the real project's scale (535 data sheets, "
                 "8 systems); rows are scaled down for the browser.",
            totals=dict(systems=len(SYSTEMS), files=len(files),
                        dataSheets=data_sheets, rows=total_rows,
                        sizeMB=round(sum(f["sizeMB"] for f in files), 1),
                        corruptFiles=sum(1 for f in files if f.get("corrupt"))),
        ),
        systems=[dict(id=s["id"], name=s["name"],
                      dual=bool(s.get("dual")), dualFiles=s.get("dual_files"),
                      span=s["span"]) for s in SYSTEMS],
        files=files,
        deepSamples=deep,
        dictionary=build_dictionary(),
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    js_path = os.path.join(OUT_DIR, "universe.js")
    with open(js_path, "w") as f:
        f.write("// FULLY SYNTHETIC sample data — generated by tools/generate_sample_data.py\n")
        f.write("// No real customer, account, or bank-internal data exists in this file.\n")
        f.write("window.HDL_UNIVERSE = ")
        json.dump(universe, f, separators=(",", ":"))
        f.write(";\n")

    t = universe["meta"]["totals"]
    lines = [
        "# Sample-Data Universe (fully synthetic)",
        "",
        "Generated by `tools/generate_sample_data.py` from a fixed seed — every account,",
        "amount, entity, and filename is fictional. The universe mirrors the *shape* of the",
        "real Historic Data Loading problem; rows are scaled down to run in a browser.",
        "",
        f"- **{t['systems']} source systems** · **{t['files']} files** · **{t['dataSheets']} data sheets**"
        f" · ~{t['rows']:,} rows · ~{t['sizeMB']:,} MB (simulated sizes) · {t['corruptFiles']} corrupt files",
        "",
        "| System | Span | Files | Data sheets | Columns (era A → C) |",
        "|---|---|---|---|---|",
    ]
    for si, s in enumerate(SYSTEMS):
        fs = [f for f in files if f["sys"] == si]
        ds = sum(1 for f in fs for sh in f["sheets"] if sh.get("data"))
        ca, cc = len(cols_for(s, 0)), len(cols_for(s, 2))
        lines.append(f"| {s['name']} | {s['span'][0]} → {s['span'][1]} | {len(fs)} | {ds} | {ca} → {cc} |")
    lines += [
        "",
        "**Messiness built in:** filename date formats drift across three eras",
        "(`position as at 30 Apr 2019` → `SYSTEM_2020-04` → `Base Apr'22`), header rows",
        "buried under 0–2 title rows, decoy sheets (Summary/Pivot/Notes), rework files",
        "(`v2`, `Copy of…`), 9 corrupt files, duplicate rows, null patches, numbers stored",
        "as text (`1,234.56`), mixed date formats, and stray TOTAL rows.",
        "",
        "**Schema drift built in:** column names change era to era (`A/C No` → `ACCOUNT_NO`",
        "→ `Account Number`), fields appear over time (provisions 2020+, IFRS9 stage 2022+),",
        "legacy fields drop after 2019, and Cards carries separate CB / IB sheets (IB uses",
        "profit rate, not interest rate).",
        "",
        "Example filenames:",
        "",
    ]
    ex = R.sample(files, 8)
    lines += [f"- `{SYSTEMS[f['sys']]['name']}/{f['y']}/{f['name']}`" for f in ex]
    with open(os.path.join(OUT_DIR, "ABOUT.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"universe.js: {os.path.getsize(js_path)/1024:.0f} KB")
    print(f"systems={t['systems']} files={t['files']} dataSheets={t['dataSheets']} "
          f"rows={t['rows']:,} sizeMB={t['sizeMB']:,} corrupt={t['corruptFiles']}")
    print(f"deep samples: {len(deep)}")
    assert t["dataSheets"] == TARGET_DATA_SHEETS
    print("OK — exactly 535 data sheets.")


if __name__ == "__main__":
    main()
