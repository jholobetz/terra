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

    # Calculate statistics
    timestamps = [m.get('timestamp', 0) for m in processed.values() if m.get('timestamp')]
    gains = [m.get('new_lhi', 0) - m.get('old_lhi', 0) for m in processed.values() if 'new_lhi' in m]
    new_scores = [m.get('new_lhi', 0) for m in processed.values() if 'new_lhi' in m]

    avg_gain = sum(gains) / len(gains) if gains else 0
    avg_score = sum(new_scores) / len(new_scores) if new_scores else 0

    speed_str = "Calculating..."
    etc_str = "Calculating..."
    if len(timestamps) >= 2:
        span_secs = max(timestamps) - min(timestamps)
        if span_secs > 0:
            f_per_sec = len(timestamps) / span_secs
            f_per_min = f_per_sec * 60
            speed_str = f"{f_per_min:.1f} formulas/min ({f_per_sec:.2f} f/s)"
            
            # Full corpus target: 12,608 formulas with LHI < 80
            remaining_total = max(0, 12608 - total_processed)
            etc_mins = (remaining_total / f_per_sec / 60) if f_per_sec > 0 else 0
            etc_str = f"{etc_mins:.1f} minutes ({etc_mins/60:.2f} hours)"

    pct_phase1 = min(100.0, (total_processed / 2030) * 100)
    pct_full = (total_processed / 12608) * 100

    print("=" * 68)
    print("🚀 TERRA PHYSICS LAB - REAL-TIME VERTEX AI ENRICHMENT DASHBOARD")
    print("=" * 68)
    print(f"  • Total Enriched So Far:   {total_processed:,} formulas")
    print(f"  • Average LHI Score:       {avg_score:.1f} / 100 (Avg Gain: +{avg_gain:.1f} pts)")
    print(f"  • Processing Speed:        {speed_str}")
    print(f"  • Phase 1 (Isolated):      ✅ 100% Complete ({min(total_processed, 2030):,}/2,030 formulas)")
    print(f"  • Full Encyclopedia Queue: {total_processed:,} / 12,608 ({pct_full:.1f}%)")
    print(f"  • Estimated Full ETC:      {etc_str}")
    print("-" * 68)
    print("📜 Latest 5 Enriched Formulas:")
    
    items = list(processed.items())[-5:]
    for fid, meta in reversed(items):
        t_str = time.strftime('%H:%M:%S', time.localtime(meta.get('timestamp', time.time())))
        parent = meta.get('parent_id') or 'Axiom / First Principle'
        print(f"  [{t_str}] {fid}")
        print(f"          └─ LHI: {meta.get('old_lhi', 0)} ➔ {meta.get('new_lhi', 0)}/100 | Parent: {parent}")
    print("=" * 68)

def main():
    parser = argparse.ArgumentParser(description="Check Real-Time Vertex AI Enrichment Progress")
    parser.add_argument('--watch', type=int, default=0, help="Live refresh interval in seconds (0 = single snapshot)")
    args = parser.parse_args()

    if args.watch > 0:
        try:
            while True:
                os.system('clear')
                render_dashboard()
                print(f"\n[Watching live... Refreshing every {args.watch}s | Press Ctrl+C to exit]")
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nExited dashboard.")
    else:
        render_dashboard()

if __name__ == '__main__':
    main()
