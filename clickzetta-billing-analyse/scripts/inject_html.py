#!/usr/bin/env python3
"""
inject_html.py — Merge data.json + insights.json and generate an HTML report (v3)

Steps:
  1. Read output/data.json (produced by auto_collect.py)
  2. Read output/insights.json (produced by Agent Step 3)
  3. Merge the conclusion and region_analysis from insights.json into data.json
  4. Copy the template from template/ to output/, inject the data, and generate the final report

Usage:
    python3 inject_html.py
    python3 inject_html.py --data ./output/data.json --insights ./output/insights.json
"""
import json
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATE_DIR = BASE_DIR / "template"
TEMPLATE_FILE = TEMPLATE_DIR / "billing_analysis_template.html"
OUTPUT_FILE = OUTPUT_DIR / "billing_analysis_report.html"


def parse_args():
    parser = argparse.ArgumentParser(description="Merge analysis results and inject into HTML")
    parser.add_argument("--data", default=str(OUTPUT_DIR / "data.json"),
                        help="path to data.json")
    parser.add_argument("--insights", default=str(OUTPUT_DIR / "insights.json"),
                        help="path to insights.json")
    parser.add_argument("--no-backup", action="store_true",
                        help="do not back up the old HTML")
    return parser.parse_args()


def validate_insights(insights: dict, data: dict) -> list:
    """
    Validate the insights.json format and return a list of warnings.
    Invalid fields fall back to default values and do not block the flow.
    """
    warnings = []
    regions = [r["region_id"] for r in data.get("region_mapping", [])]

    for rid in regions:
        if rid not in insights:
            warnings.append(f"[{rid}] missing insights data, will use empty values")
            insights[rid] = {}
            continue

        region_ins = insights[rid]

        # Validate each category's conclusion
        for cat_key in list(region_ins.keys()):
            if cat_key in ("region_analysis", "workspace_analysis"):
                continue
            cat_data = region_ins[cat_key]
            if not isinstance(cat_data, dict):
                warnings.append(f"[{rid}].{cat_key} is not a dict, skipping")
                continue
            if "conclusion" not in cat_data or not cat_data["conclusion"]:
                warnings.append(f"[{rid}].{cat_key}.conclusion is empty")

        # Validate region_analysis
        ra = region_ins.get("region_analysis")
        if ra is None:
            warnings.append(f"[{rid}] missing region_analysis")
        else:
            required_fields = ["verdict", "verdict_level", "main_reason", "details"]
            for field in required_fields:
                if field not in ra:
                    warnings.append(f"[{rid}].region_analysis.{field} is missing")

            # verdict_level validation
            valid_levels = ["none", "low", "medium", "high"]
            if ra.get("verdict_level") not in valid_levels:
                warnings.append(f"[{rid}].region_analysis.verdict_level is invalid: {ra.get('verdict_level')}")
                ra["verdict_level"] = "none"

            # details format validation
            details = ra.get("details", [])
            if not isinstance(details, list):
                warnings.append(f"[{rid}].region_analysis.details is not an array")
                ra["details"] = []

            # follow_ups format validation (optional field)
            follow_ups = ra.get("follow_ups", [])
            if not isinstance(follow_ups, list):
                ra["follow_ups"] = []

        # Validate workspace_analysis
        wa = region_ins.get("workspace_analysis")
        if wa is None:
            warnings.append(f"[{rid}] missing workspace_analysis")
        else:
            if "summary" not in wa or not wa.get("summary"):
                warnings.append(f"[{rid}].workspace_analysis.summary is missing or empty")
            top_ws = wa.get("top_workspaces", [])
            if not isinstance(top_ws, list):
                warnings.append(f"[{rid}].workspace_analysis.top_workspaces is not an array")
                wa["top_workspaces"] = []
            else:
                for i, ws_item in enumerate(top_ws):
                    if not isinstance(ws_item, dict):
                        warnings.append(f"[{rid}].workspace_analysis.top_workspaces[{i}] is not a dict")
                    elif "name" not in ws_item or "conclusion" not in ws_item:
                        warnings.append(f"[{rid}].workspace_analysis.top_workspaces[{i}] missing name or conclusion")

    return warnings


def merge_insights(data: dict, insights: dict) -> dict:
    """
    Merge the contents of insights.json into data.json.
    - conclusion: overrides data.insights[region][cat].conclusion
    - region_analysis: written to data.insights[region].region_analysis
    - workspace_analysis: written to data.insights[region].workspace_analysis
    """
    for rid, region_ins in insights.items():
        if rid not in data.get("insights", {}):
            data.setdefault("insights", {})[rid] = {}

        # Merge each category's conclusion
        for cat_key, cat_value in region_ins.items():
            if cat_key in ("region_analysis", "workspace_analysis"):
                continue
            if not isinstance(cat_value, dict):
                continue
            conclusion = cat_value.get("conclusion", "")
            if conclusion and rid in data["insights"] and cat_key in data["insights"][rid]:
                data["insights"][rid][cat_key]["conclusion"] = conclusion

        # Merge region_analysis
        if "region_analysis" in region_ins:
            data["insights"][rid]["region_analysis"] = region_ins["region_analysis"]

        # Merge workspace_analysis
        if "workspace_analysis" in region_ins:
            data["insights"][rid]["workspace_analysis"] = region_ins["workspace_analysis"]

    return data


def inject_html(html_path: Path, payload: dict):
    """Inject the merged data into the HTML file"""
    html = html_path.read_text(encoding="utf-8")

    marker_start = "<!-- __INLINE_DATA_START__ -->"
    marker_end = "<!-- __INLINE_DATA_END__ -->"

    inline_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    inline_block = (
        f"{marker_start}\n"
        f"<script>window.__BILLING_INFRA_DATA__ = {inline_json};</script>\n"
        f"{marker_end}"
    )

    if marker_start in html:
        html = re.sub(
            f"{re.escape(marker_start)}.*?{re.escape(marker_end)}",
            inline_block,
            html,
            flags=re.DOTALL
        )
    else:
        html = html.replace("</head>", f"{inline_block}\n</head>")

    html_path.write_text(html, encoding="utf-8")


def main():
    args = parse_args()

    data_path = Path(args.data)
    insights_path = Path(args.insights)

    # Check that files exist
    if not data_path.exists():
        sys.exit(f"❌ data.json does not exist: {data_path}\n   please run auto_collect.py first")

    if not insights_path.exists():
        sys.exit(
            f"❌ insights.json does not exist: {insights_path}\n"
            f"   please have the Agent read data.json and generate insights.json first\n"
            f"   (containing conclusion + region_analysis)"
        )

    if not TEMPLATE_FILE.exists():
        sys.exit(f"❌ HTML template does not exist: {TEMPLATE_FILE}")

    # Ensure the output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Copy from template to output
    print(f"📋 Copying template → {OUTPUT_FILE.name}")
    shutil.copy2(TEMPLATE_FILE, OUTPUT_FILE)

    # resource_notes.js is deprecated (instance_usage has no cluster-name dimension; its purpose is now
    # inferred from the SKU type; getResourceNote falls back to '—' when there is no match), so it is no
    # longer copied.

    # Read the data
    print("📖 Reading data.json...")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    print(f"   Regions: {len(data.get('region_mapping', []))}")
    print(f"   Months: {data.get('months', [])}")

    print("📖 Reading insights.json...")
    insights = json.loads(insights_path.read_text(encoding="utf-8"))
    print(f"   Regions included: {list(insights.keys())}")

    # Validation
    print("\n🔍 Validating insights format...")
    warnings = validate_insights(insights, data)
    if warnings:
        print(f"   ⚠️ {len(warnings)} warnings:")
        for w in warnings:
            print(f"      - {w}")
    else:
        print("   ✅ Format validation passed")

    # Merge
    print("\n🔗 Merging data.json + insights.json...")
    merged = merge_insights(data, insights)

    # Check whether region_analysis and workspace_analysis have been injected
    for r in data.get("region_mapping", []):
        rid = r["region_id"]
        has_ra = "region_analysis" in merged.get("insights", {}).get(rid, {})
        has_wa = "workspace_analysis" in merged.get("insights", {}).get(rid, {})
        ra_status = "✅" if has_ra else "⚠️ missing"
        wa_status = "✅" if has_wa else "⚠️ missing"
        print(f"   [{r['label']}] region_analysis: {ra_status} | workspace_analysis: {wa_status}")

    # Backup
    if not args.no_backup and OUTPUT_FILE.exists():
        backup_path = OUTPUT_FILE.with_suffix(f".bak.{datetime.now().strftime('%Y%m%d%H%M%S')}.html")
        shutil.copy2(OUTPUT_FILE, backup_path)
        print(f"\n💾 Backing up old HTML → {backup_path.name}")

    # Inject
    print(f"\n💉 Injecting data into {OUTPUT_FILE.name}...")
    inject_html(OUTPUT_FILE, merged)

    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\n{'='*50}")
    print(f"✅ Done")
    print(f"   HTML: {OUTPUT_FILE} ({size_kb:.1f} KB)")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
