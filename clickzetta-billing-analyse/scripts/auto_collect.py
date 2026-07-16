#!/usr/bin/env python3
"""
auto_collect.py — 通过 cz-cli 采集各 Region 的 instance_usage 计费数据 (v3)

数据源: sys.information_schema.instance_usage（实例本地视图，需 instance_admin 角色）
采集方式: cz-cli sql -p <profile> "<SQL>" --limit 0
不做 LLM 分析（那是 Agent 自己的活）。产出 data.json + summary.txt 到 output 目录。

用法:
    python3 auto_collect.py --from 2026-02 --to 2026-06 --profiles <your_profile>
    python3 auto_collect.py --profiles p1,p2               # 默认最近 6 个月
    python3 auto_collect.py --profiles p1 --check-only      # 只做权限门禁，不采集

设计要点:
    - profile 驱动，无任何硬编码 account_id / region / 用户名
    - instance_usage 是实例本地的，一个 profile = 一个 Region 的数据，自带 region_name / account_name
    - 权限不足的 profile 跳过并记录 skipped_regions，供看板标注「无权限/未采集」
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
    parser = argparse.ArgumentParser(description="通过 cz-cli 采集 instance_usage 计费数据 (v3)")
    today = date.today()
    default_to = today.strftime("%Y-%m")
    default_from = (today - relativedelta(months=5)).replace(day=1).strftime("%Y-%m")

    parser.add_argument("--from", dest="from_month", default=default_from,
                        help="起始月份 YYYY-MM (默认: 当前月 -5)")
    parser.add_argument("--to", dest="to_month", default=default_to,
                        help="结束月份 YYYY-MM (默认: 当前月)")
    parser.add_argument("--profiles", required=True,
                        help="cz-cli profile 名，逗号分隔（必填，无默认）")
    parser.add_argument("--check-only", action="store_true",
                        help="只做权限门禁检查，不执行采集")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR),
                        help="输出目录 (默认: scripts/../output)")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# cz-cli 调用（list 形式 argv，防命令注入）
# ---------------------------------------------------------------------------
def run_cz(profile: str, sql: str, limit: int = 0, timeout: int = 300):
    """执行 cz-cli sql，返回 (columns, rows)。失败抛异常。"""
    proc = subprocess.run(
        ["cz-cli", "sql", "-p", profile, sql, "--limit", str(limit)],
        capture_output=True, text=True, timeout=timeout,
    )
    out = proc.stdout.strip()
    if not out:
        raise RuntimeError(proc.stderr.strip() or f"cz-cli 无输出 (exit={proc.returncode})")
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
# 权限门禁
# ---------------------------------------------------------------------------
def check_permissions(profile: str) -> dict:
    """
    检查 profile 是否具备采集 instance_usage 的权限。
    需要: (a) instance_admin 角色; (b) 至少一个可用 vcluster 能执行查询。
    返回 {ok, has_instance_admin, can_query, reason}。
    """
    result = {"ok": False, "has_instance_admin": False, "can_query": False, "reason": ""}

    # (a) 角色扫描仅作辅助线索（instance_admin 可能是实例级授予，工作空间级 SHOW GRANTS 未必可见，
    #     因此不作为硬门禁，只用于失败时给出更具体的提示）
    try:
        _, grant_rows = run_cz(profile, "SHOW GRANTS", limit=0)
        blob = json.dumps(grant_rows, ensure_ascii=False).lower()
        result["has_instance_admin"] = "instance_admin" in blob
    except Exception:
        pass

    # (b) 探针查询是权威门禁：直接验证能否用计算集群 SELECT instance_usage
    #     成功执行（即使 count=0）即证明具备 instance_admin + 可用 vcluster
    probe = ("SELECT count(*) AS c FROM sys.information_schema.instance_usage "
             "WHERE measurement_start >= CURRENT_DATE() - INTERVAL 1 DAYS")
    try:
        _, rows = run_cz(profile, probe, limit=0)
        result["can_query"] = bool(rows)
    except Exception as e:
        msg = str(e)
        low = msg.lower()
        if "vcluster" in low or "virtual cluster" in low:
            result["reason"] = "无可用计算集群 (vcluster)，无法执行查询。需至少一个工作空间有 use vcluster 权限"
        elif "nopermission" in low or "no select" in low or "not found" in low or "permission" in low:
            result["reason"] = "缺少 instance_admin 角色，无法查询 sys.information_schema.instance_usage"
        else:
            result["reason"] = f"探针查询失败: {msg[:150]}"
        return result

    if not result["can_query"]:
        result["reason"] = "探针查询未返回结果，无法确认权限"
        return result

    result["ok"] = True
    return result


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def to_float(v):
    if v is None:
        return 0.0
    try:
        return float(v)
    except Exception:
        return 0.0


def profile_to_region_id(profile: str) -> str:
    """由 profile 名派生稳定的 region_id slug（下划线转连字符）。"""
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
    """自描述：从首行 region_name 取标签（instance_usage 自带该列）。"""
    for r in rows:
        rn = r.get("region_name")
        if rn:
            return rn
    return fallback


# ---------------------------------------------------------------------------
# 采集单个 profile
# ---------------------------------------------------------------------------
def collect_one_profile(profile, from_month, to_month):
    """采集单个 profile 的数据，返回 (region_id, rows, label, error)。"""
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
            "resource_name": sku,  # instance_usage 无集群名维度，用 sku_name 占位
            "month": r.get("month"),
            "total_amount": to_float(r.get("total_amount")),
            "total_cru": to_float(r.get("total_cru")),
        })
    label = region_label_from_rows(raw, region_id)
    print(f"  ✓ [{label}] {len(rows)} 行, {time.time()-t0:.1f}s")
    return (region_id, rows, label, None)


def compact_region_data(rows, amount_threshold=1.0, max_rows_per_group=50):
    """将大量小额记录合并为 '(其他 X 项)'，控制 HTML 体积。"""
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
            template["resource_name"] = f"(其他 {len(merge)} 项小额资源)"
            template["total_amount"] = round(sum(r["total_amount"] for r in merge), 2)
            template["total_cru"] = round(sum(r["total_cru"] for r in merge), 2)
            result.append(template)
    return result


def compute_insights_deterministic(rows, all_months):
    """确定性计算 insights（amounts / top_items / overall_change_pct），conclusion 留空由 Agent 填充。"""
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
# summary.txt 生成
# ---------------------------------------------------------------------------
def build_summary(all_data, region_labels, region_insights, months_list, skipped, from_month, to_month):
    lines = []
    lines.append("# Billing 计量成本采集摘要 (instance_usage)")
    lines.append(f"时间范围: {from_month} ~ {to_month} ({len(months_list)} 个月)")
    lines.append(f"采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"月份列表: {', '.join(months_list)}")
    lines.append("")

    for skip in skipped:
        lines.append(f"## {skip['label']} (❌ 跳过: {skip['reason']})")
        lines.append("")

    for rid, rows in all_data.items():
        label = region_labels.get(rid, rid)
        region_total = sum(r["total_amount"] for r in rows)
        lines.append(f"## {label} ({rid})")
        lines.append(f"总记录: {len(rows)} 行, 总费用: ¥{region_total:,.0f}")
        lines.append("")

        ins = region_insights.get(rid, {})
        for cat, cat_data in ins.items():
            amounts = cat_data["amounts"]
            pct = cat_data.get("overall_change_pct")
            pct_str = f"{pct:+.1f}%" if pct is not None else "N/A"
            lines.append(f"### {cat} (月度: {' → '.join([f'¥{a:,.0f}' for a in amounts])}, 变化: {pct_str})")
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

        # Workspace 维度汇总
        ws_monthly = {}
        for row in rows:
            ws = row.get("workspace_name") or "(未分配)"
            ws_monthly.setdefault(ws, {})
            ws_monthly[ws][row["month"]] = ws_monthly[ws].get(row["month"], 0) + row["total_amount"]
        ws_sorted = sorted(ws_monthly.items(), key=lambda x: sum(x[1].values()), reverse=True)[:8]
        if ws_sorted:
            lines.append("### [Workspace 维度汇总]")
            for ws_name, monthly in ws_sorted:
                ws_amounts = [monthly.get(m, 0) for m in months_list]
                ws_total = sum(ws_amounts)
                ws_pct = (ws_total / region_total * 100) if region_total > 0 else 0
                ws_last = ws_amounts[-1] if ws_amounts else 0
                ws_prev = ws_amounts[-2] if len(ws_amounts) >= 2 else 0
                ws_mom = ((ws_last - ws_prev) / ws_prev * 100) if ws_prev > 0 else (100 if ws_last > 0 else 0)
                lines.append(
                    f"  - {ws_name}: 合计 ¥{ws_total:,.0f} (占{ws_pct:.0f}%), "
                    f"末月 ¥{ws_last:,.0f}, 环比 {ws_mom:+.0f}%, "
                    f"月度: {' → '.join([f'¥{a:,.0f}' for a in ws_amounts])}"
                )
            if len(months_list) >= 2:
                first_ws = set(ws for ws, m in ws_monthly.items() if m.get(months_list[0], 0) > 0)
                last_ws = set(ws for ws, m in ws_monthly.items() if m.get(months_list[-1], 0) > 0)
                new_ws = last_ws - first_ws
                gone_ws = first_ws - last_ws
                if new_ws:
                    lines.append(f"  🆕 新增 Workspace: {', '.join(sorted(new_ws))}")
                if gone_ws:
                    lines.append(f"  💤 已停用 Workspace: {', '.join(sorted(gone_ws))}")
            lines.append("")
    return "\n".join(lines)


def main():
    args = parse_args()
    profiles = [p.strip() for p in args.profiles.split(",") if p.strip()]
    if not profiles:
        sys.exit("❌ --profiles 不能为空")

    # 权限门禁（所有 profile 先过一遍）
    print("🔐 权限门禁检查...")
    gate = {}
    for p in profiles:
        chk = check_permissions(p)
        gate[p] = chk
        status = "✅ 通过" if chk["ok"] else f"❌ {chk['reason']}"
        print(f"   [{p}] {status}")

    if args.check_only:
        ok_n = sum(1 for c in gate.values() if c["ok"])
        print(f"\n门禁完成: {ok_n}/{len(profiles)} 个 profile 可采集")
        return

    passed = [p for p in profiles if gate[p]["ok"]]
    skipped = [
        {"region_id": profile_to_region_id(p), "label": profile_to_region_id(p), "reason": gate[p]["reason"]}
        for p in profiles if not gate[p]["ok"]
    ]
    if not passed:
        sys.exit("❌ 所有 profile 均未通过权限门禁，无法采集。请检查 instance_admin 角色和 vcluster 权限。")

    months_list = compute_month_list(args.from_month, args.to_month)
    if len(months_list) > 12:
        sys.exit(f"❌ 时间范围过大（{len(months_list)} 个月），最多支持 12 个月")
    if len(months_list) == 0:
        sys.exit("❌ 起始月份必须 ≤ 结束月份")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📊 采集 (v3, instance_usage via cz-cli)")
    print(f"   时间范围: {args.from_month} ~ {args.to_month} ({len(months_list)} 个月)")
    print(f"   采集 profile: {len(passed)} 个 | 跳过: {len(skipped)} 个")
    print()

    all_data = {}
    region_labels = {}
    errors = {}
    region_mapping = []
    for p in passed:
        region_id, rows, label, error = collect_one_profile(p, args.from_month, args.to_month)
        if error:
            errors[region_id] = error
            skipped.append({"region_id": region_id, "label": label, "reason": f"采集失败: {error}"})
            print(f"  ⚠️ [{region_id}] {error}")
            continue
        all_data[region_id] = rows
        region_labels[region_id] = label
        region_mapping.append({"region_id": region_id, "label": label})

    # 数据精简
    print("\n🗜️  精简数据...")
    for rid in list(all_data.keys()):
        before = len(all_data[rid])
        all_data[rid] = compact_region_data(all_data[rid])
        after = len(all_data[rid])
        if before != after:
            print(f"  [{region_labels[rid]}] {before} → {after} 行 (合并了 {before - after} 条小额明细)")

    # 确定性 insights
    print("\n计算 insights（确定性部分）...")
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
        "data_source_note": "sys.information_schema.instance_usage（折后金额 total_after_discount）；无集群名维度，resource_name 以 sku_name 占位；下钻分析用 sys.information_schema.job_history",
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
    print(f"✅ 采集完成")
    print(f"   成功: {len(all_data)} 个地域, {total_rows} 条记录")
    if skipped:
        print(f"   跳过: {len(skipped)} 个地域 ({', '.join(s['region_id'] for s in skipped)})")
    print(f"   输出: {data_path} ({size_kb:.1f} KB)")
    print(f"   摘要: {summary_path} ({len(summary_text)} 字符)")
    print(f"{'='*50}")
    print()
    print("📝 下一步: Agent 读取 summary.txt 生成 insights.json（含 conclusion + region_analysis + workspace_analysis）")
    print("   然后执行: python3 inject_html.py --no-backup")


if __name__ == "__main__":
    main()
