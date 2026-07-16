#!/usr/bin/env python3
"""
inject_html.py — 合并 data.json + insights.json，生成 HTML 报告 (v3)

步骤:
  1. 读取 output/data.json（auto_collect.py 产出）
  2. 读取 output/insights.json（Agent Step 3 产出）
  3. 将 insights.json 中的 conclusion 和 region_analysis 合并到 data.json
  4. 从 template/ 复制模板到 output/，注入数据后生成最终报告

用法:
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
    parser = argparse.ArgumentParser(description="合并分析结果并注入 HTML")
    parser.add_argument("--data", default=str(OUTPUT_DIR / "data.json"),
                        help="data.json 路径")
    parser.add_argument("--insights", default=str(OUTPUT_DIR / "insights.json"),
                        help="insights.json 路径")
    parser.add_argument("--no-backup", action="store_true",
                        help="不备份旧 HTML")
    return parser.parse_args()


def validate_insights(insights: dict, data: dict) -> list:
    """
    校验 insights.json 格式，返回警告列表。
    不合格字段用默认值兜底，不阻塞流程。
    """
    warnings = []
    regions = [r["region_id"] for r in data.get("region_mapping", [])]

    for rid in regions:
        if rid not in insights:
            warnings.append(f"[{rid}] 缺少 insights 数据，将使用空值")
            insights[rid] = {}
            continue

        region_ins = insights[rid]

        # 校验每个品类的 conclusion
        for cat_key in list(region_ins.keys()):
            if cat_key in ("region_analysis", "workspace_analysis"):
                continue
            cat_data = region_ins[cat_key]
            if not isinstance(cat_data, dict):
                warnings.append(f"[{rid}].{cat_key} 不是 dict，跳过")
                continue
            if "conclusion" not in cat_data or not cat_data["conclusion"]:
                warnings.append(f"[{rid}].{cat_key}.conclusion 为空")

        # 校验 region_analysis
        ra = region_ins.get("region_analysis")
        if ra is None:
            warnings.append(f"[{rid}] 缺少 region_analysis")
        else:
            required_fields = ["verdict", "verdict_level", "main_reason", "details"]
            for field in required_fields:
                if field not in ra:
                    warnings.append(f"[{rid}].region_analysis.{field} 缺失")

            # verdict_level 校验
            valid_levels = ["none", "low", "medium", "high"]
            if ra.get("verdict_level") not in valid_levels:
                warnings.append(f"[{rid}].region_analysis.verdict_level 无效: {ra.get('verdict_level')}")
                ra["verdict_level"] = "none"

            # details 格式校验
            details = ra.get("details", [])
            if not isinstance(details, list):
                warnings.append(f"[{rid}].region_analysis.details 不是数组")
                ra["details"] = []

            # follow_ups 格式校验（可选字段）
            follow_ups = ra.get("follow_ups", [])
            if not isinstance(follow_ups, list):
                ra["follow_ups"] = []

        # 校验 workspace_analysis
        wa = region_ins.get("workspace_analysis")
        if wa is None:
            warnings.append(f"[{rid}] 缺少 workspace_analysis")
        else:
            if "summary" not in wa or not wa.get("summary"):
                warnings.append(f"[{rid}].workspace_analysis.summary 缺失或为空")
            top_ws = wa.get("top_workspaces", [])
            if not isinstance(top_ws, list):
                warnings.append(f"[{rid}].workspace_analysis.top_workspaces 不是数组")
                wa["top_workspaces"] = []
            else:
                for i, ws_item in enumerate(top_ws):
                    if not isinstance(ws_item, dict):
                        warnings.append(f"[{rid}].workspace_analysis.top_workspaces[{i}] 不是 dict")
                    elif "name" not in ws_item or "conclusion" not in ws_item:
                        warnings.append(f"[{rid}].workspace_analysis.top_workspaces[{i}] 缺少 name 或 conclusion")

    return warnings


def merge_insights(data: dict, insights: dict) -> dict:
    """
    将 insights.json 的内容合并到 data.json 中。
    - conclusion: 覆盖 data.insights[region][cat].conclusion
    - region_analysis: 写入 data.insights[region].region_analysis
    - workspace_analysis: 写入 data.insights[region].workspace_analysis
    """
    for rid, region_ins in insights.items():
        if rid not in data.get("insights", {}):
            data.setdefault("insights", {})[rid] = {}

        # 合并各品类 conclusion
        for cat_key, cat_value in region_ins.items():
            if cat_key in ("region_analysis", "workspace_analysis"):
                continue
            if not isinstance(cat_value, dict):
                continue
            conclusion = cat_value.get("conclusion", "")
            if conclusion and rid in data["insights"] and cat_key in data["insights"][rid]:
                data["insights"][rid][cat_key]["conclusion"] = conclusion

        # 合并 region_analysis
        if "region_analysis" in region_ins:
            data["insights"][rid]["region_analysis"] = region_ins["region_analysis"]

        # 合并 workspace_analysis
        if "workspace_analysis" in region_ins:
            data["insights"][rid]["workspace_analysis"] = region_ins["workspace_analysis"]

    return data


def inject_html(html_path: Path, payload: dict):
    """将合并后的数据注入 HTML 文件"""
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

    # 检查文件存在
    if not data_path.exists():
        sys.exit(f"❌ data.json 不存在: {data_path}\n   请先运行 auto_collect.py")

    if not insights_path.exists():
        sys.exit(
            f"❌ insights.json 不存在: {insights_path}\n"
            f"   请先让 Agent 读取 data.json 并生成 insights.json\n"
            f"   (包含 conclusion + region_analysis)"
        )

    if not TEMPLATE_FILE.exists():
        sys.exit(f"❌ HTML 模板不存在: {TEMPLATE_FILE}")

    # 确保 output 目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 从 template 复制到 output
    print(f"📋 复制模板 → {OUTPUT_FILE.name}")
    shutil.copy2(TEMPLATE_FILE, OUTPUT_FILE)

    # resource_notes.js 已弃用（instance_usage 无集群名维度，用途改由 SKU 类型推断；
    # getResourceNote 无匹配时自动降级为 '—'），不再复制。

    # 读取数据
    print("📖 读取 data.json...")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    print(f"   地域: {len(data.get('region_mapping', []))} 个")
    print(f"   月份: {data.get('months', [])}")

    print("📖 读取 insights.json...")
    insights = json.loads(insights_path.read_text(encoding="utf-8"))
    print(f"   包含地域: {list(insights.keys())}")

    # 校验
    print("\n🔍 校验 insights 格式...")
    warnings = validate_insights(insights, data)
    if warnings:
        print(f"   ⚠️ {len(warnings)} 个警告:")
        for w in warnings:
            print(f"      - {w}")
    else:
        print("   ✅ 格式校验通过")

    # 合并
    print("\n🔗 合并 data.json + insights.json...")
    merged = merge_insights(data, insights)

    # 检查 region_analysis 和 workspace_analysis 是否已注入
    for r in data.get("region_mapping", []):
        rid = r["region_id"]
        has_ra = "region_analysis" in merged.get("insights", {}).get(rid, {})
        has_wa = "workspace_analysis" in merged.get("insights", {}).get(rid, {})
        ra_status = "✅" if has_ra else "⚠️ 缺失"
        wa_status = "✅" if has_wa else "⚠️ 缺失"
        print(f"   [{r['label']}] region_analysis: {ra_status} | workspace_analysis: {wa_status}")

    # 备份
    if not args.no_backup and OUTPUT_FILE.exists():
        backup_path = OUTPUT_FILE.with_suffix(f".bak.{datetime.now().strftime('%Y%m%d%H%M%S')}.html")
        shutil.copy2(OUTPUT_FILE, backup_path)
        print(f"\n💾 备份旧 HTML → {backup_path.name}")

    # 注入
    print(f"\n💉 注入数据到 {OUTPUT_FILE.name}...")
    inject_html(OUTPUT_FILE, merged)

    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\n{'='*50}")
    print(f"✅ 完成！")
    print(f"   HTML: {OUTPUT_FILE} ({size_kb:.1f} KB)")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
