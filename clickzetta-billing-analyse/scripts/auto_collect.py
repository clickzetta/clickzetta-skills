#!/usr/bin/env python3
"""
auto_collect.py — Collect instance_usage billing data for each Region via cz-cli (v3)

Data source: sys.information_schema.instance_usage (instance-local view, requires instance_admin role)
Collection method: cz-cli sql -p <profile> "<SQL>" --limit 0
No LLM analysis (that is the Agent's own job). Produces data.json + summary.txt in the output directory.

Usage:
    python3 auto_collect.py --from 2026-02 --to 2026-06 --profiles <your_profile>
    python3 auto_collect.py --profiles p1,p2               # defaults to the last 6 months
    python3 auto_collect.py --profiles p1 --check-only      # permission gate only, no collection

Design notes:
    - profile-driven, with no hardcoded account_id / region / username
    - instance_usage is instance-local; one profile = one Region's data, carrying region_name / account_name
    - profiles without permission are skipped and recorded in skipped_regions, for the dashboard to mark as "no permission / not collected"
"""
import json
import re
import sys
import time
import argparse
import subprocess
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def parse_args():
    parser = argparse.ArgumentParser(description="Collect instance_usage billing data via cz-cli (v3)")
    today = date.today()
    default_to = today.strftime("%Y-%m")
    default_from = (today - relativedelta(months=5)).replace(day=1).strftime("%Y-%m")

    parser.add_argument("--from", dest="from_month", default=default_from,
                        help="start month YYYY-MM (default: current month -5)")
    parser.add_argument("--to", dest="to_month", default=default_to,
                        help="end month YYYY-MM (default: current month)")
    parser.add_argument("--profiles", required=True,
                        help="cz-cli profile names, comma-separated (required, no default)")
    parser.add_argument("--check-only", action="store_true",
                        help="run the permission gate check only, without collecting")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR),
                        help="output directory (default: scripts/../output)")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# cz-cli invocation (argv as a list, to prevent command injection)
# ---------------------------------------------------------------------------
def run_cz(profile: str, sql: str, limit: int = 0, timeout: int = 300):
    """Execute cz-cli sql and return (columns, rows). Raises an exception on failure."""
    proc = subprocess.run(
        ["cz-cli", "sql", "-p", profile, sql, "--limit", str(limit)],
        capture_output=True, text=True, timeout=timeout,
    )
    out = proc.stdout.strip()
    if not out:
        raise RuntimeError(proc.stderr.strip() or f"cz-cli produced no output (exit={proc.returncode})")
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        raise RuntimeError(out[:300])
    if isinstance(payload, dict) and payload.get("error"):
        err = payload["error"]
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        raise RuntimeError(msg)
    cols = payload.get("columns", [])
    rows = [dict(zip(cols, r)) for r in payload.get("rows", [])]
    return cols, rows


# ---------------------------------------------------------------------------
# Permission gate
# ---------------------------------------------------------------------------
def check_permissions(profile: str) -> dict:
    """
    Check whether the profile has permission to collect instance_usage.
    Requires: (a) the instance_admin role; (b) at least one usable vcluster that can run queries.
    Returns {ok, has_instance_admin, can_query, reason}.
    """
    result = {"ok": False, "has_instance_admin": False, "can_query": False, "reason": ""}

    # (a) The role scan is only an auxiliary hint (instance_admin may be granted at the instance level,
    #     which is not necessarily visible in a workspace-level SHOW GRANTS, so it is not used as a hard
    #     gate, only to provide a more specific hint on failure)
    try:
        _, grant_rows = run_cz(profile, "SHOW GRANTS", limit=0)
        blob = json.dumps(grant_rows, ensure_ascii=False).lower()
        result["has_instance_admin"] = "instance_admin" in blob
    except Exception:
        pass

    # (b) The probe query is the authoritative gate: it directly verifies whether instance_usage can be
    #     SELECTed using a compute cluster. A successful run (even with count=0) proves both
    #     instance_admin and a usable vcluster are available
    probe = ("SELECT count(*) AS c FROM sys.information_schema.instance_usage "
             "WHERE measurement_start >= CURRENT_DATE() - INTERVAL 1 DAYS")
    try:
        _, rows = run_cz(profile, probe, limit=0)
        result["can_query"] = bool(rows)
    except Exception as e:
        msg = str(e)
        low = msg.lower()
        if "vcluster" in low or "virtual cluster" in low:
            result["reason"] = "No usable compute cluster (vcluster); cannot run queries. At least one workspace must have the use vcluster permission"
        elif "nopermission" in low or "no select" in low or "not found" in low or "permission" in low:
            result["reason"] = "Missing the instance_admin role; cannot query sys.information_schema.instance_usage"
        else:
            result["reason"] = f"Probe query failed: {msg[:150]}"
        return result

    if not result["can_query"]:
        result["reason"] = "Probe query returned no results; permission could not be confirmed"
        return result

    result["ok"] = True
    return result


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------
def to_float(v):
    if v is None:
        return 0.0
    try:
        return float(v)
    except Exception:
        return 0.0


def profile_to_region_id(profile: str) -> str:
    """Derive a stable region_id slug from the profile name (underscores to hyphens)."""
    return re.sub(r"_billing$", "", profile).replace("_", "-")


def compute_month_list(from_month: str, to_month: str) -> list:
    start = datetime.strptime(from_month, "%Y-%m")
    end = datetime.strptime(to_month, "%Y-%m")
    months = []
    cur = start
    while cur <= end:
        months.append(cur.strftime("%Y-%m"))
        cur += relativedelta(months=1)
    return months


def next_month_first(month_str: str) -> str:
    dt = datetime.strptime(month_str, "%Y-%m") + relativedelta(months=1)
    return dt.strftime("%Y-%m-%d")


def region_label_from_rows(rows: list, fallback: str) -> str:
    """Self-describing: take the label from the first row's region_name (instance_usage carries this column)."""
    for r in rows:
        rn = r.get("region_name")
        if rn:
            return rn
    return fallback


# ---------------------------------------------------------------------------
# Collect a single profile
# ---------------------------------------------------------------------------
def collect_one_profile(profile, from_month, to_month):
    """Collect data for a single profile and return (region_id, rows, label, error)."""
    region_id = profile_to_region_id(profile)
    from_date = f"{from_month}-01"
    to_next = next_month_first(to_month)

    sql = f"""
        SELECT SUBSTRING(CAST(measurement_start AS STRING),1,7) AS month,
               LOWER(sku_category) AS sku_category, sku_name,
               COALESCE(workspace_name,'(未分配)') AS workspace_name,
               region_name, account_name,
               ROUND(SUM(total_after_discount),2)     AS total_amount,
               ROUND(SUM(measurements_consumption),2) AS total_cru
        FROM sys.information_schema.instance_usage
        WHERE measurement_start >= '{from_date}' AND measurement_start < '{to_next}'
        GROUP BY 1,2,3,4,5,6
        ORDER BY sku_category, month, total_amount DESC
    """

    t0 = time.time()
    try:
        _, raw = run_cz(profile, sql, limit=0)
    except Exception as e:
        return (region_id, [], region_id, str(e)[:200])

    rows = []
    for r in raw:
        sku = r.get("sku_name") or ""
        rows.append({
            "sku_name": sku,
            "sku_code": sku,
            "sku_category": (r.get("sku_category") or "other").lower(),
            "workspace_name": r.get("workspace_name") or "(未分配)",
            "resource_name": sku,  # instance_usage has no cluster-name dimension; use sku_name as a placeholder
            "month": r.get("month"),
            "total_amount": to_float(r.get("total_amount")),
            "total_cru": to_float(r.get("total_cru")),
        })
    label = region_label_from_rows(raw, region_id)
    print(f"  ✓ [{label}] {len(rows)} rows, {time.time()-t0:.1f}s")
    return (region_id, rows, label, None)


def compact_region_data(rows, amount_threshold=1.0, max_rows_per_group=50):
    """Merge many small-amount records into '(Other X items)' to control HTML size."""
    from collections import defaultdict
    groups = defaultdict(list)
    for row in rows:
        key = (row.get("sku_code", ""), row.get("workspace_name", ""), row.get("month", ""))
        groups[key].append(row)

    result = []
    for _, group_rows in groups.items():
        group_rows.sort(key=lambda r: -r["total_amount"])
        keep, merge = [], []
        for i, r in enumerate(group_rows):
            if i < max_rows_per_group or r["total_amount"] >= amount_threshold:
                keep.append(r)
            else:
                merge.append(r)
        result.extend(keep)
        if merge:
            template = merge[0].copy()
            template["resource_name"] = f"(Other {len(merge)} small-amount resources)"
            template["total_amount"] = round(sum(r["total_amount"] for r in merge), 2)
            template["total_cru"] = round(sum(r["total_cru"] for r in merge), 2)
            result.append(template)
    return result


def compute_insights_deterministic(rows, all_months):
    """Deterministically compute insights (amounts / top_items / overall_change_pct); leave conclusion empty for the Agent to fill in."""
    insights = {}
    cat_monthly, cat_details = {}, {}
    for row in rows:
        cat = (row.get("sku_category") or "other").lower()
        month = row["month"]
        cat_monthly.setdefault(cat, {})
        cat_details.setdefault(cat, {})
        cat_monthly[cat][month] = cat_monthly[cat].get(month, 0) + row["total_amount"]
        cat_details[cat].setdefault(month, []).append({
            "sku_name": row.get("sku_name", ""),
            "sku_code": row.get("sku_code", ""),
            "resource_name": row.get("resource_name", ""),
            "workspace_name": row.get("workspace_name", ""),
            "amount": row["total_amount"],
            "cru": row["total_cru"],
        })

    for cat, monthly in cat_monthly.items():
        amounts = [round(monthly.get(m, 0), 2) for m in all_months]
        if sum(amounts) < 5:
            continue
        if len(amounts) >= 2 and amounts[0] > 0:
            overall_change = round((amounts[-1] - amounts[0]) / amounts[0] * 100, 1)
        else:
            overall_change = None
        top_n = 5 if cat == "storage" else 3
        top_items = {}
        for m in all_months:
            items = cat_details[cat].get(m, [])
            top_items[m] = sorted(items, key=lambda x: -x["amount"])[:top_n]
        insights[cat] = {
            "amounts": amounts, "months": all_months, "conclusion": "",
            "overall_change_pct": overall_change, "top_items": top_items,
        }
    return insights


# ---------------------------------------------------------------------------
# summary.txt generation
# ---------------------------------------------------------------------------
def build_summary(all_data, region_labels, region_insights, months_list, skipped, from_month, to_month):
    lines = []
    lines.append("# Billing metering cost collection summary (instance_usage)")
    lines.append(f"Time range: {from_month} ~ {to_month} ({len(months_list)} months)")
    lines.append(f"Collected at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Month list: {', '.join(months_list)}")
    lines.append("")

    for skip in skipped:
        lines.append(f"## {skip['label']} (❌ skipped: {skip['reason']})")
        lines.append("")

    for rid, rows in all_data.items():
        label = region_labels.get(rid, rid)
        region_total = sum(r["total_amount"] for r in rows)
        lines.append(f"## {label} ({rid})")
        lines.append(f"Total records: {len(rows)} rows, total cost: ¥{region_total:,.0f}")
        lines.append("")

        ins = region_insights.get(rid, {})
        for cat, cat_data in ins.items():
            amounts = cat_data["amounts"]
            pct = cat_data.get("overall_change_pct")
            pct_str = f"{pct:+.1f}%" if pct is not None else "N/A"
            lines.append(f"### {cat} (monthly: {' → '.join([f'¥{a:,.0f}' for a in amounts])}, change: {pct_str})")
            for mi in [-2, -1]:
                if abs(mi) > len(months_list):
                    continue
                m = months_list[mi]
                top = cat_data.get("top_items", {}).get(m, [])[:5]
                if top:
                    lines.append(f"  {m} Top:")
                    for t in top:
                        ws = t.get("workspace_name") or "-"
                        sku = t.get("sku_name") or "-"
                        lines.append(f"    - {ws}/{sku}: ¥{t['amount']:,.0f} ({t['cru']:.1f} CRU)")
            lines.append("")

        # Workspace-dimension summary
        ws_monthly = {}
        for row in rows:
            ws = row.get("workspace_name") or "(未分配)"
            ws_monthly.setdefault(ws, {})
            ws_monthly[ws][row["month"]] = ws_monthly[ws].get(row["month"], 0) + row["total_amount"]
        ws_sorted = sorted(ws_monthly.items(), key=lambda x: sum(x[1].values()), reverse=True)[:8]
        if ws_sorted:
            lines.append("### [Workspace-dimension summary]")
            for ws_name, monthly in ws_sorted:
                ws_amounts = [monthly.get(m, 0) for m in months_list]
                ws_total = sum(ws_amounts)
                ws_pct = (ws_total / region_total * 100) if region_total > 0 else 0
                ws_last = ws_amounts[-1] if ws_amounts else 0
                ws_prev = ws_amounts[-2] if len(ws_amounts) >= 2 else 0
                ws_mom = ((ws_last - ws_prev) / ws_prev * 100) if ws_prev > 0 else (100 if ws_last > 0 else 0)
                lines.append(
                    f"  - {ws_name}: total ¥{ws_total:,.0f} ({ws_pct:.0f}%), "
                    f"last month ¥{ws_last:,.0f}, MoM {ws_mom:+.0f}%, "
                    f"monthly: {' → '.join([f'¥{a:,.0f}' for a in ws_amounts])}"
                )
            if len(months_list) >= 2:
                first_ws = set(ws for ws, m in ws_monthly.items() if m.get(months_list[0], 0) > 0)
                last_ws = set(ws for ws, m in ws_monthly.items() if m.get(months_list[-1], 0) > 0)
                new_ws = last_ws - first_ws
                gone_ws = first_ws - last_ws
                if new_ws:
                    lines.append(f"  🆕 New Workspaces: {', '.join(sorted(new_ws))}")
                if gone_ws:
                    lines.append(f"  💤 Deactivated Workspaces: {', '.join(sorted(gone_ws))}")
            lines.append("")
    return "\n".join(lines)


def main():
    args = parse_args()
    profiles = [p.strip() for p in args.profiles.split(",") if p.strip()]
    if not profiles:
        sys.exit("❌ --profiles cannot be empty")

    # Permission gate (run every profile through it first)
    print("🔐 Permission gate check...")
    gate = {}
    for p in profiles:
        chk = check_permissions(p)
        gate[p] = chk
        status = "✅ passed" if chk["ok"] else f"❌ {chk['reason']}"
        print(f"   [{p}] {status}")

    if args.check_only:
        ok_n = sum(1 for c in gate.values() if c["ok"])
        print(f"\nGate complete: {ok_n}/{len(profiles)} profiles can be collected")
        return

    passed = [p for p in profiles if gate[p]["ok"]]
    skipped = [
        {"region_id": profile_to_region_id(p), "label": profile_to_region_id(p), "reason": gate[p]["reason"]}
        for p in profiles if not gate[p]["ok"]
    ]
    if not passed:
        sys.exit("❌ No profile passed the permission gate; cannot collect. Please check the instance_admin role and vcluster permissions.")

    months_list = compute_month_list(args.from_month, args.to_month)
    if len(months_list) > 12:
        sys.exit(f"❌ Time range too large ({len(months_list)} months); at most 12 months are supported")
    if len(months_list) == 0:
        sys.exit("❌ The start month must be ≤ the end month")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📊 Collecting (v3, instance_usage via cz-cli)")
    print(f"   Time range: {args.from_month} ~ {args.to_month} ({len(months_list)} months)")
    print(f"   Profiles to collect: {len(passed)} | skipped: {len(skipped)}")
    print()

    all_data = {}
    region_labels = {}
    errors = {}
    region_mapping = []
    for p in passed:
        region_id, rows, label, error = collect_one_profile(p, args.from_month, args.to_month)
        if error:
            errors[region_id] = error
            skipped.append({"region_id": region_id, "label": label, "reason": f"collection failed: {error}"})
            print(f"  ⚠️ [{region_id}] {error}")
            continue
        all_data[region_id] = rows
        region_labels[region_id] = label
        region_mapping.append({"region_id": region_id, "label": label})

    # Data compaction
    print("\n🗜️  Compacting data...")
    for rid in list(all_data.keys()):
        before = len(all_data[rid])
        all_data[rid] = compact_region_data(all_data[rid])
        after = len(all_data[rid])
        if before != after:
            print(f"  [{region_labels[rid]}] {before} → {after} rows (merged {before - after} small-amount line items)")

    # Deterministic insights
    print("\nComputing insights (deterministic part)...")
    region_insights = {}
    for rid in all_data:
        region_insights[rid] = compute_insights_deterministic(all_data[rid], months_list)

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "query_params": {"from": args.from_month, "to": args.to_month, "profiles": ",".join(passed)},
        "months": months_list,
        "region_mapping": region_mapping,
        "regions_data": all_data,
        "insights": region_insights,
        "data_source_note": "sys.information_schema.instance_usage (discounted amount total_after_discount); no cluster-name dimension, resource_name uses sku_name as a placeholder; use sys.information_schema.job_history for drill-down analysis",
    }
    if skipped:
        payload["skipped_regions"] = skipped
    if errors:
        payload["collection_errors"] = errors

    data_path = output_dir / "data.json"
    data_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    size_kb = data_path.stat().st_size / 1024

    summary_text = build_summary(all_data, region_labels, region_insights, months_list, skipped,
                                 args.from_month, args.to_month)
    summary_path = output_dir / "summary.txt"
    summary_path.write_text(summary_text, encoding="utf-8")

    total_rows = sum(len(rows) for rows in all_data.values())
    print(f"\n{'='*50}")
    print(f"✅ Collection complete")
    print(f"   Success: {len(all_data)} regions, {total_rows} records")
    if skipped:
        print(f"   Skipped: {len(skipped)} regions ({', '.join(s['region_id'] for s in skipped)})")
    print(f"   Output: {data_path} ({size_kb:.1f} KB)")
    print(f"   Summary: {summary_path} ({len(summary_text)} characters)")
    print(f"{'='*50}")
    print()
    print("📝 Next step: the Agent reads summary.txt to generate insights.json (with conclusion + region_analysis + workspace_analysis)")
    print("   then run: python3 inject_html.py --no-backup")


if __name__ == "__main__":
    main()
