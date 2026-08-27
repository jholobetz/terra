#!/usr/bin/env python3
"""
📊 Terra Physics Lab - Real-Time Enrichment Progress Dashboard
Inspects the live checkpoint ledger, LHI distribution, throughput, and ETC.

Usage:
    scripts/checkprogress
    scripts/checkprogress --watch 5
"""

import os
import sys
import json
import time
import glob
import argparse

SCRIPT_REAL_DIR = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_REAL_DIR)) if 'maintenance' in SCRIPT_REAL_DIR else os.path.dirname(SCRIPT_REAL_DIR)
CHECKPOINT_FILE = os.path.join(PROJECT_ROOT, 'app', 'config', 'vertex_enricher_checkpoint.json')
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')

def render_dashboard():
    if not os.path.exists(CHECKPOINT_FILE):
        print("⚠️ No checkpoint file found at app/config/vertex_enricher_checkpoint.json.")
        return

    try:
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading checkpoint: {e}")
        return

    processed = data.get('processed_ids', {})
    total_processed = len(processed)

    # Count total formulas in shards
    shard_files = glob.glob(os.path.join(FORMULAS_DIR, '*', 'shard_*.json'))
    total_formulas = 13802  # standard corpus

    if not processed:
        print("Checkpoint is empty. Runner has not started yet.")
        return

    # Classify processed by starting LHI
    p1_done = sum(1 for m in processed.values() if m.get('old_lhi') == 0)
    p2_done = sum(1 for m in processed.values() if 0 < m.get('old_lhi', 0) < 40)
    p3_done = sum(1 for m in processed.values() if 40 <= m.get('old_lhi', 0) < 75)

    p1_target = 2030
    p2_target = 537
    p3_target = 7039

    # Calculate statistics
    timestamps = sorted([m.get('timestamp', 0) for m in processed.values() if m.get('timestamp')])
    gains = [m.get('new_lhi', 0) - m.get('old_lhi', 0) for m in processed.values() if 'new_lhi' in m]
    new_scores = [m.get('new_lhi', 0) for m in processed.values() if 'new_lhi' in m]

    avg_gain = sum(gains) / len(gains) if gains else 0
    avg_score = sum(new_scores) / len(new_scores) if new_scores else 0

    # Recent speed (filter out multi-hour pauses by taking active session window)
    active_ts = []
    for i in range(len(timestamps) - 1, 0, -1):
        active_ts.insert(0, timestamps[i])
        if len(active_ts) >= 30 or (timestamps[i] - timestamps[i-1] > 180):
            break

    recent_ts = active_ts if len(active_ts) >= 2 else timestamps[-10:]
    speed_str = "Calculating..."
    p2_etc_str = "Calculating..."
    p3_etc_str = "Calculating..."
    full_etc_str = "Calculating..."
    if len(recent_ts) >= 2:
        span_secs = recent_ts[-1] - recent_ts[0]
        if span_secs > 0:
            f_per_sec = len(recent_ts) / span_secs
            f_per_min = f_per_sec * 60
            speed_str = f"{f_per_min:.1f} formulas/min ({f_per_sec:.2f} f/s)"
            
            p2_rem = max(0, p2_target - p2_done)
            p2_etc_mins = (p2_rem / f_per_sec / 60) if f_per_sec > 0 else 0
            p2_etc_str = f"{p2_etc_mins:.1f} mins ({p2_etc_mins/60:.2f} hrs)" if p2_rem > 0 else "✅ Complete"

            p3_rem = max(0, p3_target - p3_done)
            p3_etc_mins = (p3_rem / f_per_sec / 60) if f_per_sec > 0 else 0
            p3_etc_str = f"{p3_etc_mins:.1f} mins ({p3_etc_mins/60:.2f} hrs)" if p3_rem > 0 else "✅ Complete"

            full_rem = max(0, 12608 - total_processed)
            full_etc_mins = (full_rem / f_per_sec / 60) if f_per_sec > 0 else 0
            full_etc_str = f"{full_etc_mins:.1f} mins ({full_etc_mins/60:.2f} hrs)" if full_rem > 0 else "✅ Complete"

    # Financial & Token Accounting
    is_paid = data.get('is_paid_session', False)
    session_spend = data.get('session_spend_usd', 0.0)
    max_cost = data.get('max_cost_dollars', 0.0)
    active_model = data.get('active_model', 'gemini-3.5-flash-lite')
    
    # Unit cost estimate (Gemini 3.7 Flash with Hybrid Reasoning = ~$0.00256 / formula)
    if '3.7-flash' in active_model:
        unit_cost_est = 0.00256
    elif 'pro' in active_model:
        unit_cost_est = 0.00488
    else:
        unit_cost_est = 0.00035

    p3_rem_count = max(0, p3_target - p3_done)
    full_rem_count = max(0, 12608 - total_processed)
    p3_cost_est = p3_rem_count * unit_cost_est
    full_cost_est = full_rem_count * unit_cost_est

    p1_pct = min(100.0, (p1_done / p1_target) * 100) if p1_target > 0 else 100.0
    p2_pct = min(100.0, (p2_done / p2_target) * 100) if p2_target > 0 else 100.0
    p3_pct = min(100.0, (p3_done / p3_target) * 100) if p3_target > 0 else 100.0
    total_pct = (total_processed / 12608) * 100

    def make_bar(pct, length=20):
        filled = int((pct / 100.0) * length)
        return "█" * filled + "░" * (length - filled)

    print("=" * 70)
    print("🚀 TERRA PHYSICS LAB - REAL-TIME VERTEX AI ENRICHMENT DASHBOARD")
    print("=" * 70)
    print(f"  • Total Enriched So Far:   {total_processed:,} formulas | Avg LHI: {avg_score:.1f}/100")
    print(f"  • Current Live Speed:      {speed_str}")
    print("-" * 70)
    print("💵 LIVE DOLLAR METER & BUDGET:")
    if is_paid:
        cap_str = f" / ${max_cost:.2f} Limit" if max_cost > 0 else " (No Cap)"
        pct_used_str = f" ({(session_spend / max_cost)*100:.1f}% used)" if max_cost > 0 else ""
        rem_budget_str = f"${max_cost - session_spend:.4f}" if max_cost > 0 else "N/A"
        print(f"  • Total Spent (This Run):  ${session_spend:.4f}{cap_str}{pct_used_str}")
        print(f"  • Remaining Budget Left:   {rem_budget_str}")
        print(f"  • Estimated Cost to Finish: Phase 3: ~${p3_cost_est:.2f} | Full Corpus: ~${full_cost_est:.2f}")
    else:
        print("  • Current Billing Mode:    🆓 Google AI Studio Free Tier ($0.00 Cost)")
        print(f"  • Estimated Paid Cost:     Phase 3: ~${p3_cost_est:.2f} | Full Corpus: ~${full_cost_est:.2f}")
    print("-" * 70)
    p3_cost_tag = f" (${p3_cost_est:.2f})" if is_paid else ""
    full_cost_tag = f" (${full_cost_est:.2f})" if is_paid else ""
    print(f"  📌 Phase 1 (Isolated):     [{make_bar(100.0)}] 2,030/2,030 (100.0%) ✅")
    print(f"  📌 Phase 2 (Thin LHI 1-39): [{make_bar(p2_pct)}] {p2_done:,}/{p2_target:,} ({p2_pct:.1f}%) | ETC: {p2_etc_str}")
    print(f"  📌 Phase 3 (Moderate):     [{make_bar(p3_pct)}] {p3_done:,}/{p3_target:,} ({p3_pct:.1f}%) | ETC: {p3_etc_str}{p3_cost_tag}")
    print(f"  🌍 Full Corpus Queue:      [{make_bar(total_pct)}] {total_processed:,}/12,608 ({total_pct:.1f}%) | ETC: {full_etc_str}{full_cost_tag}")
    print("-" * 70)
    print("📜 Latest 5 Enriched Formulas:")
    
    items = list(processed.items())[-5:]
    for fid, meta in reversed(items):
        t_str = time.strftime('%H:%M:%S', time.localtime(meta.get('timestamp', time.time())))
        parent = meta.get('parent_id') or 'Axiom / First Principle'
        cost_info = f" (${meta.get('cost_usd', 0.0):.5f})" if meta.get('cost_usd') else ""
        print(f"  [{t_str}] {fid}{cost_info}")
        print(f"          └─ LHI: {meta.get('old_lhi', 0)} ➔ {meta.get('new_lhi', 0)}/100 | Parent: {parent}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Check Real-Time Vertex AI Enrichment Progress")
    parser.add_argument('interval', nargs='?', type=int, default=0, help="Optional refresh interval in seconds (e.g. scripts/checkprogress 3)")
    parser.add_argument('--watch', '-w', type=int, default=0, help="Live refresh interval in seconds (0 = single snapshot)")
    args = parser.parse_args()

    watch_interval = args.interval if args.interval > 0 else args.watch

    if watch_interval > 0:
        try:
            while True:
                os.system('clear')
                render_dashboard()
                print(f"\n[Watching live... Refreshing every {watch_interval}s | Press Ctrl+C to exit]")
                time.sleep(watch_interval)
        except KeyboardInterrupt:
            print("\nExited dashboard.")
    else:
        render_dashboard()

if __name__ == '__main__':
    main()
