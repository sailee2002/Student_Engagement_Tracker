"""
visualizations.py
All chart generation for the Student Engagement & Outcomes Tracker.
Produces publication-ready PNG figures saved to /reports/figures/.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# ── Style ──────────────────────────────────────────────────────────────
PALETTE = ["#1F3864", "#2E75B6", "#70AD47", "#ED7D31", "#FFC000", "#A9D18E"]
ACCENT  = "#1F3864"
sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 120,
})

SEMESTER_ORDER = ["Fall 2022", "Spring 2023", "Fall 2023", "Spring 2024", "Fall 2024"]


def _save(fig, outdir, filename):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, filename)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved → {path}")
    return path


# ── 1. Pre/Post Score Comparison ───────────────────────────────────────
def plot_pre_post(df, outdir):
    metrics = ["confidence", "skill_readiness", "engagement"]
    labels  = ["Confidence", "Skill Readiness", "Engagement"]
    pre_means  = [df[f"pre_{m}"].mean()  for m in metrics]
    post_means = [df[f"post_{m}"].mean() for m in metrics]

    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width/2, pre_means,  width, label="Pre-Survey",  color=PALETTE[1], alpha=0.85)
    bars2 = ax.bar(x + width/2, post_means, width, label="Post-Survey", color=PALETTE[2], alpha=0.85)

    for bar in bars1: ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.03,
                               f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=9)
    for bar in bars2: ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.03,
                               f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylim(0, 5.5); ax.set_ylabel("Mean Score (1–5 Scale)")
    ax.set_title("Pre vs. Post Survey Scores Across All Programs", fontweight="bold", pad=12)
    ax.legend(); ax.yaxis.grid(True, alpha=0.4); ax.set_axisbelow(True)
    return _save(fig, outdir, "01_pre_post_scores.png")


# ── 2. Semester Enrollment & Persistence Trend ─────────────────────────
def plot_semester_trends(df, outdir):
    df = df.copy()
    df["semester"] = pd.Categorical(df["semester"], categories=SEMESTER_ORDER, ordered=True)
    trends = df.groupby("semester", observed=True).agg(
        enrollment=("student_id","count"),
        persistence_rate=("persisted","mean"),
        avg_gain=("overall_gain","mean"),
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(9, 5))
    color_bar = PALETTE[0]
    ax1.bar(trends["semester"], trends["enrollment"], color=color_bar, alpha=0.7, label="Enrollment")
    ax1.set_ylabel("Enrollment", color=color_bar)
    ax1.tick_params(axis="y", labelcolor=color_bar)
    ax1.set_xticklabels(trends["semester"], rotation=20, ha="right")

    ax2 = ax1.twinx()
    ax2.plot(trends["semester"], trends["persistence_rate"]*100, color=PALETTE[3],
             marker="o", linewidth=2.2, label="Persistence %", zorder=5)
    ax2.plot(trends["semester"], trends["avg_gain"]*20, color=PALETTE[2],
             marker="s", linewidth=2.2, linestyle="--", label="Avg Gain (scaled)", zorder=5)
    ax2.set_ylabel("Rate / Scaled Gain")
    ax2.set_ylim(0, 110)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1+lines2, labels1+labels2, loc="upper left", fontsize=9)
    ax1.set_title("Enrollment, Persistence & Learning Gains by Semester", fontweight="bold", pad=12)
    fig.tight_layout()
    return _save(fig, outdir, "02_semester_trends.png")


# ── 3. Program Comparison Heatmap ──────────────────────────────────────
def plot_program_heatmap(df, outdir):
    grp = df.groupby("program").agg(
        Persistence=("persisted","mean"),
        Internship=("secured_internship_job","mean"),
        Attendance=("attendance_rate","mean"),
        Confidence_Gain=("confidence_gain","mean"),
        Skill_Gain=("skill_gain","mean"),
        Engagement_Gain=("engagement_gain","mean"),
    ).round(3)
    grp.columns = ["Persistence", "Internship Rate", "Attendance", "Confidence Gain", "Skill Gain", "Engagement Gain"]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    sns.heatmap(grp, annot=True, fmt=".2f", cmap="Blues", ax=ax,
                linewidths=0.5, cbar_kws={"shrink": 0.8})
    ax.set_title("Program Performance Heatmap", fontweight="bold", pad=12)
    ax.set_ylabel("")
    plt.xticks(rotation=25, ha="right")
    return _save(fig, outdir, "03_program_heatmap.png")


# ── 4. Qualitative Theme Bar Chart ─────────────────────────────────────
def plot_themes(themes_df, outdir):
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [PALETTE[4] if "Improvement" in t else PALETTE[0] for t in themes_df["theme"]]
    bars = ax.barh(themes_df["theme"], themes_df["pct_of_responses"], color=colors, alpha=0.88)
    for bar in bars:
        ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
                f"{bar.get_width():.1f}%", va="center", fontsize=9)
    ax.set_xlabel("% of Responses")
    ax.set_title("Qualitative Theme Frequency (Open-Response Analysis)", fontweight="bold", pad=12)
    ax.set_xlim(0, themes_df["pct_of_responses"].max() + 15)
    ax.invert_yaxis()

    pos_patch = mpatches.Patch(color=PALETTE[0], label="Positive/Neutral Theme")
    neg_patch = mpatches.Patch(color=PALETTE[4], label="Area for Improvement")
    ax.legend(handles=[pos_patch, neg_patch], fontsize=9)
    fig.tight_layout()
    return _save(fig, outdir, "04_qualitative_themes.png")


# ── 5. Equity Analysis: Gain by Demographic ────────────────────────────
def plot_equity(df, outdir):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # First-gen vs non
    fg = df.groupby("first_generation")["overall_gain"].mean().reset_index()
    fg["label"] = fg["first_generation"].map({True: "First-Gen", False: "Non-First-Gen"})
    axes[0].bar(fg["label"], fg["overall_gain"], color=[PALETTE[1], PALETTE[3]], alpha=0.85)
    for i, row in fg.iterrows():
        axes[0].text(i, row["overall_gain"]+0.02, f"{row['overall_gain']:.2f}", ha="center", fontsize=10)
    axes[0].set_title("Avg Learning Gain: First-Gen vs. Non-First-Gen", fontweight="bold")
    axes[0].set_ylabel("Mean Overall Gain"); axes[0].set_ylim(0, 1.5)

    # Race/ethnicity
    re_grp = df.groupby("race_ethnicity")["overall_gain"].mean().sort_values(ascending=True)
    axes[1].barh(re_grp.index, re_grp.values, color=PALETTE[0], alpha=0.82)
    for i, (idx, val) in enumerate(re_grp.items()):
        axes[1].text(val+0.01, i, f"{val:.2f}", va="center", fontsize=9)
    axes[1].set_title("Avg Learning Gain by Race/Ethnicity", fontweight="bold")
    axes[1].set_xlabel("Mean Overall Gain")

    fig.suptitle("Equity Analysis — Learning Outcomes by Demographic", fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    return _save(fig, outdir, "05_equity_analysis.png")


# ── 6. Attendance vs. Gain Scatter ─────────────────────────────────────
def plot_attendance_gain(df, outdir):
    fig, ax = plt.subplots(figsize=(8, 5))
    programs = df["program"].unique()
    cmap = {p: PALETTE[i] for i, p in enumerate(programs)}

    for prog in programs:
        sub = df[df["program"] == prog]
        ax.scatter(sub["attendance_rate"]*100, sub["overall_gain"],
                   color=cmap[prog], alpha=0.55, s=40, label=prog)

    # Trend line
    x = df["attendance_rate"]*100
    y = df["overall_gain"]
    m, b = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, m*xs+b, color="black", linewidth=1.5, linestyle="--", label=f"Trend (r={np.corrcoef(x,y)[0,1]:.2f})")

    ax.set_xlabel("Attendance Rate (%)")
    ax.set_ylabel("Overall Learning Gain")
    ax.set_title("Attendance Rate vs. Learning Gains (by Program)", fontweight="bold", pad=12)
    ax.legend(fontsize=8, loc="upper left")
    return _save(fig, outdir, "06_attendance_vs_gain.png")


# ── Run all ─────────────────────────────────────────────────────────────
def generate_all_charts(df, themes_df, outdir="reports/figures"):
    print("\nGenerating visualizations...")
    paths = []
    paths.append(plot_pre_post(df, outdir))
    paths.append(plot_semester_trends(df, outdir))
    paths.append(plot_program_heatmap(df, outdir))
    paths.append(plot_themes(themes_df, outdir))
    paths.append(plot_equity(df, outdir))
    paths.append(plot_attendance_gain(df, outdir))
    print(f"  ✓ {len(paths)} charts saved to {outdir}/")
    return paths
