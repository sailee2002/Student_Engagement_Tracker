"""
main.py
Run the full Student Engagement & Outcomes Tracker pipeline:
  1. Load & clean data
  2. Run quantitative + qualitative analysis
  3. Generate all visualizations
  4. Write narrative summary report to /reports/
"""

import os
import sys

# Allow running from any working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from analysis import (
    load_and_clean, demographic_summary, pre_post_summary,
    persistence_outcomes, semester_trends, equity_analysis,
    extract_themes, sentiment_split, generate_narrative
)
from visualizations import generate_all_charts

DATA_PATH    = os.path.join(BASE_DIR, "data", "student_engagement_data.csv")
REPORTS_DIR  = os.path.join(BASE_DIR, "reports")
FIGURES_DIR  = os.path.join(REPORTS_DIR, "figures")
REPORT_PATH  = os.path.join(REPORTS_DIR, "summary_report.txt")


def run():
    print("=" * 60)
    print("STUDENT ENGAGEMENT & OUTCOMES TRACKER")
    print("=" * 60)

    # ── 1. Load & Clean ──────────────────────────────────────────
    print("\n[1/4] Loading and cleaning data...")
    df = load_and_clean(DATA_PATH)
    flagged = df["data_quality_flag"].sum()
    print(f"  ✓ {len(df)} records loaded | {flagged} flagged for data quality review")

    # ── 2. Analysis ──────────────────────────────────────────────
    print("\n[2/4] Running analysis...")

    demo = demographic_summary(df)
    print("  ✓ Demographic summary complete")
    print(f"    → {len(demo['gender'])} gender categories | "
          f"{len(demo['race_ethnicity'])} race/ethnicity categories")

    pre_post = pre_post_summary(df)
    avg_gain = df["overall_gain"].mean()
    print(f"  ✓ Pre/post analysis complete | avg overall gain: {avg_gain:.2f}")

    outcomes = persistence_outcomes(df)
    print("  ✓ Persistence & outcomes by program:")
    for prog, row in outcomes.iterrows():
        print(f"    → {prog}: {row['persistence_rate']}% persistence | "
              f"{row['internship_rate']}% internship rate")

    trends = semester_trends(df)
    print("  ✓ Multi-semester trend analysis complete")

    equity = equity_analysis(df)
    print("  ✓ Equity analysis complete")

    themes = extract_themes(df)
    sentiment = sentiment_split(df)
    print(f"  ✓ Qualitative theme extraction complete | "
          f"Sentiment: {sentiment['Positive']} pos / {sentiment['Neutral']} neu / {sentiment['Negative']} neg")

    # ── 3. Visualizations ────────────────────────────────────────
    print("\n[3/4] Generating visualizations...")
    generate_all_charts(df, themes, outdir=FIGURES_DIR)

    # ── 4. Report ────────────────────────────────────────────────
    print("\n[4/4] Writing summary report...")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    narrative = generate_narrative(df)
    with open(REPORT_PATH, "w") as f:
        f.write(narrative)
    print(f"  ✓ Report saved → {REPORT_PATH}")

    # ── Print report to console ──────────────────────────────────
    print("\n" + narrative)

    print("\n" + "=" * 60)
    print("Pipeline complete. Outputs in /reports/")
    print("=" * 60)


if __name__ == "__main__":
    run()
