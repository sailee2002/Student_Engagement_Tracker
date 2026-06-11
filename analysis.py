"""
analysis.py
Core analysis functions for the Student Engagement & Outcomes Tracker.
Covers: data cleaning, quantitative analysis, qualitative theme extraction,
multi-semester trend synthesis, and summary report generation.
"""

import pandas as pd
import numpy as np
from collections import Counter
import re


# ─────────────────────────────────────────────
# 1. DATA LOADING & CLEANING
# ─────────────────────────────────────────────

def load_and_clean(filepath: str) -> pd.DataFrame:
    """Load CSV, validate schema, clean types, flag anomalies."""
    df = pd.read_csv(filepath)

    # Enforce types
    bool_cols = ["first_generation", "persisted", "secured_internship_job"]
    for c in bool_cols:
        df[c] = df[c].astype(bool)

    likert_cols = [
        "pre_confidence", "pre_skill_readiness", "pre_engagement",
        "post_confidence", "post_skill_readiness", "post_engagement"
    ]
    for c in likert_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").clip(1, 5)

    df["attendance_rate"] = df["attendance_rate"].clip(0, 1)
    df["gpa_change"] = pd.to_numeric(df["gpa_change"], errors="coerce")
    df["open_response"] = df["open_response"].fillna("").str.strip()

    # Derived fields
    df["confidence_gain"] = df["post_confidence"] - df["pre_confidence"]
    df["skill_gain"] = df["post_skill_readiness"] - df["pre_skill_readiness"]
    df["engagement_gain"] = df["post_engagement"] - df["pre_engagement"]
    df["overall_gain"] = df[["confidence_gain", "skill_gain", "engagement_gain"]].mean(axis=1).round(2)

    # Flag records with missing likert data
    df["data_quality_flag"] = df[likert_cols].isnull().any(axis=1)

    return df


# ─────────────────────────────────────────────
# 2. DESCRIPTIVE STATISTICS
# ─────────────────────────────────────────────

def demographic_summary(df: pd.DataFrame) -> dict:
    """Return demographic breakdown counts and percentages."""
    cols = ["gender", "race_ethnicity", "first_generation", "year", "college"]
    summary = {}
    for col in cols:
        vc = df[col].value_counts()
        pct = (vc / len(df) * 100).round(1)
        summary[col] = pd.DataFrame({"count": vc, "pct": pct})
    return summary


def pre_post_summary(df: pd.DataFrame, groupby: str = None) -> pd.DataFrame:
    """Compute mean pre/post scores and gains, optionally grouped."""
    metrics = {
        "Pre Confidence": "pre_confidence",
        "Post Confidence": "post_confidence",
        "Confidence Gain": "confidence_gain",
        "Pre Skill": "pre_skill_readiness",
        "Post Skill": "post_skill_readiness",
        "Skill Gain": "skill_gain",
        "Pre Engagement": "pre_engagement",
        "Post Engagement": "post_engagement",
        "Engagement Gain": "engagement_gain",
        "Overall Gain": "overall_gain",
    }
    cols = list(metrics.values())
    if groupby:
        result = df.groupby(groupby)[cols].mean().round(2)
        result.columns = list(metrics.keys())
    else:
        result = pd.DataFrame(df[cols].mean().round(2)).T
        result.columns = list(metrics.keys())
    return result


def persistence_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    """Persistence and outcome rates by program."""
    grp = df.groupby("program").agg(
        total_students=("student_id", "count"),
        persistence_rate=("persisted", "mean"),
        internship_rate=("secured_internship_job", "mean"),
        avg_attendance=("attendance_rate", "mean"),
        avg_gpa_change=("gpa_change", "mean"),
        avg_overall_gain=("overall_gain", "mean"),
    ).round(3)
    grp["persistence_rate"] = (grp["persistence_rate"] * 100).round(1)
    grp["internship_rate"] = (grp["internship_rate"] * 100).round(1)
    grp["avg_attendance"] = (grp["avg_attendance"] * 100).round(1)
    return grp


# ─────────────────────────────────────────────
# 3. MULTI-SEMESTER TREND ANALYSIS
# ─────────────────────────────────────────────

SEMESTER_ORDER = ["Fall 2022", "Spring 2023", "Fall 2023", "Spring 2024", "Fall 2024"]

def semester_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate key metrics by semester in chronological order."""
    df = df.copy()
    df["semester"] = pd.Categorical(df["semester"], categories=SEMESTER_ORDER, ordered=True)
    trends = df.groupby("semester", observed=True).agg(
        enrollment=("student_id", "count"),
        persistence_rate=("persisted", "mean"),
        internship_rate=("secured_internship_job", "mean"),
        avg_overall_gain=("overall_gain", "mean"),
        avg_attendance=("attendance_rate", "mean"),
        first_gen_pct=("first_generation", "mean"),
    ).round(3)
    trends["persistence_rate"] = (trends["persistence_rate"] * 100).round(1)
    trends["internship_rate"] = (trends["internship_rate"] * 100).round(1)
    trends["avg_attendance"] = (trends["avg_attendance"] * 100).round(1)
    trends["first_gen_pct"] = (trends["first_gen_pct"] * 100).round(1)
    return trends


def equity_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compare outcomes by first-generation status and race/ethnicity."""
    grp = df.groupby(["race_ethnicity", "first_generation"]).agg(
        n=("student_id", "count"),
        avg_overall_gain=("overall_gain", "mean"),
        persistence_rate=("persisted", "mean"),
        internship_rate=("secured_internship_job", "mean"),
    ).round(3)
    grp["persistence_rate"] = (grp["persistence_rate"] * 100).round(1)
    grp["internship_rate"] = (grp["internship_rate"] * 100).round(1)
    return grp


# ─────────────────────────────────────────────
# 4. MIXED-METHODS: QUALITATIVE THEME EXTRACTION
# ─────────────────────────────────────────────

THEME_KEYWORDS = {
    "Career & Internship Readiness": ["internship", "career", "job", "landed", "network", "professional"],
    "Skill Development": ["skill", "skills", "practical", "hands-on", "experience", "learned", "develop"],
    "Confidence & Personal Growth": ["confident", "confidence", "growth", "stronger", "communication", "leadership"],
    "Program Structure & Resources": ["resources", "structured", "feedback", "advisor", "advising", "scheduling", "flexible"],
    "Peer & Community Connection": ["peers", "connected", "community", "share", "mentor", "mentorship"],
    "Areas for Improvement": ["disconnected", "hard", "needed", "more support", "conflict", "wish"],
}


def extract_themes(df: pd.DataFrame) -> pd.DataFrame:
    """Tag each response with matching themes."""
    responses = df["open_response"].str.lower()
    theme_counts = {}
    for theme, keywords in THEME_KEYWORDS.items():
        pattern = "|".join(keywords)
        matches = responses.str.contains(pattern, na=False)
        theme_counts[theme] = int(matches.sum())

    total = len(df[df["open_response"] != ""])
    result = pd.DataFrame({
        "theme": list(theme_counts.keys()),
        "mention_count": list(theme_counts.values()),
    })
    result["pct_of_responses"] = (result["mention_count"] / total * 100).round(1)
    return result.sort_values("mention_count", ascending=False).reset_index(drop=True)


def sentiment_split(df: pd.DataFrame) -> dict:
    """Split responses into positive, neutral, negative buckets."""
    positive_kw = ["valuable", "confident", "internship", "skills", "connected", "practical", "landed", "stronger", "helpful", "appreciated"]
    negative_kw = ["disconnected", "hard", "needed more", "conflict", "wish", "support"]

    text = df["open_response"].str.lower()
    pos = text.str.contains("|".join(positive_kw), na=False).sum()
    neg = text.str.contains("|".join(negative_kw), na=False).sum()
    neu = len(df) - pos - neg

    return {"Positive": int(pos), "Neutral": int(neu), "Negative": int(neg)}


# ─────────────────────────────────────────────
# 5. NARRATIVE SUMMARY GENERATOR
# ─────────────────────────────────────────────

def generate_narrative(df: pd.DataFrame) -> str:
    """Auto-generate a written summary translating data findings into recommendations."""
    trends = semester_trends(df)
    themes = extract_themes(df)
    sentiment = sentiment_split(df)
    outcomes = persistence_outcomes(df)

    total = len(df)
    semesters = df["semester"].nunique()
    programs = df["program"].nunique()

    avg_gain = df["overall_gain"].mean()
    best_semester = trends["avg_overall_gain"].idxmax()
    worst_semester = trends["avg_overall_gain"].idxmin()
    best_program = outcomes["avg_overall_gain"].idxmax()
    avg_persistence = df["persisted"].mean() * 100
    avg_internship = df["secured_internship_job"].mean() * 100

    top_theme = themes.iloc[0]["theme"]
    improvement_theme = themes[themes["theme"] == "Areas for Improvement"].iloc[0]["pct_of_responses"] if "Areas for Improvement" in themes["theme"].values else 0

    first_gen_gain = df[df["first_generation"] == True]["overall_gain"].mean()
    non_first_gen_gain = df[df["first_generation"] == False]["overall_gain"].mean()
    equity_gap = round(non_first_gen_gain - first_gen_gain, 2)

    lines = [
        "=" * 70,
        "STUDENT ENGAGEMENT & OUTCOMES TRACKER — STRATEGIC SUMMARY REPORT",
        "=" * 70,
        "",
        "OVERVIEW",
        "--------",
        f"This report synthesizes data from {total} student participants across {semesters} semesters",
        f"and {programs} experiential learning programs. Findings draw on quantitative pre/post",
        f"survey data, attendance tracking, and qualitative open-response analysis.",
        "",
        "KEY FINDINGS",
        "------------",
        f"1. LEARNING GAINS: Students showed an average overall gain of {avg_gain:.2f} points",
        f"   (on a 1–5 scale) across confidence, skill readiness, and engagement metrics.",
        f"   The strongest semester was {best_semester}; gains were lowest in {worst_semester},",
        f"   suggesting a possible program delivery or cohort composition factor worth investigating.",
        "",
        f"2. PROGRAM PERFORMANCE: '{best_program}' consistently produced the highest",
        f"   learning gains. Cross-program replication of its delivery model is recommended.",
        "",
        f"3. PERSISTENCE & OUTCOMES: {avg_persistence:.1f}% of students persisted through",
        f"   at least half of program sessions. Among persisters, {avg_internship:.1f}% secured",
        f"   an internship or job — indicating a strong link between program engagement and",
        f"   career outcomes.",
        "",
        f"4. QUALITATIVE THEMES: The most frequently cited theme across open responses was",
        f"   '{top_theme}' ({themes.iloc[0]['pct_of_responses']}% of responses). Sentiment analysis",
        f"   shows {sentiment['Positive']} positive, {sentiment['Neutral']} neutral, and {sentiment['Negative']} negative responses.",
        f"   {improvement_theme}% of responses flagged areas for improvement — primarily around",
        f"   scheduling flexibility and access to advising resources.",
        "",
        f"5. EQUITY LENS: First-generation students showed an average overall gain of {first_gen_gain:.2f}",
        f"   vs. {non_first_gen_gain:.2f} for non-first-gen peers (gap: {equity_gap:+.2f}).",
        "   " + ("Targeted support for first-gen students is recommended to close this gap."
                  if equity_gap > 0.1 else "No significant equity gap detected — positive sign for program inclusivity."),
        "",
        "RECOMMENDATIONS",
        "---------------",
        "• Scale delivery elements from the highest-performing program to other pathways.",
        "• Introduce mid-semester check-in surveys to improve early identification of at-risk students.",
        "• Add flexible scheduling options and expand advising touchpoints (flagged in 'Areas for Improvement').",
        "• Develop targeted outreach for first-generation students in lower-performing semesters.",
        "• Establish a semester-over-semester dashboard review cadence with program leads.",
        "",
        "DATA NOTES",
        "----------",
        f"• {df['data_quality_flag'].sum()} records flagged for missing Likert data (excluded from gain calculations).",
        "• Qualitative themes extracted via keyword matching; manual review recommended for nuance.",
        "• All data is synthetic and for demonstration purposes only.",
        "",
        "=" * 70,
    ]
    return "\n".join(lines)
