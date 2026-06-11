"""
generate_data.py
Generates mock multi-semester student engagement and outcomes data
for the Student Engagement & Outcomes Tracker project.
"""

import pandas as pd
import numpy as np
import random
import os

np.random.seed(42)
random.seed(42)

SEMESTERS = ["Fall 2022", "Spring 2023", "Fall 2023", "Spring 2024", "Fall 2024"]
PROGRAMS = ["Experiential Learning", "Career Readiness", "Leadership Development", "Community Engagement"]
DEMOGRAPHICS = {
    "gender": ["Female", "Male", "Non-binary", "Prefer not to say"],
    "race_ethnicity": ["Asian", "Black/African American", "Hispanic/Latino", "White", "Multiracial", "Other"],
    "first_gen": [True, False],
    "year": ["Freshman", "Sophomore", "Junior", "Senior"],
    "college": ["Engineering", "Business", "Liberal Arts", "Sciences", "Education"]
}

QUAL_POSITIVE = [
    "The workshops helped me build real-world skills I can use immediately.",
    "I felt more confident after completing the program milestones.",
    "The mentorship component was incredibly valuable for my career path.",
    "I learned how to network effectively and landed an internship.",
    "The program connected me with peers who share my interests.",
    "I developed stronger communication and leadership skills.",
    "The hands-on projects gave me practical experience beyond coursework.",
    "I appreciated the structured feedback from program advisors.",
]
QUAL_NEUTRAL = [
    "The program was okay but I wish there were more flexible scheduling options.",
    "Some sessions were more useful than others.",
    "I would have liked more one-on-one advising time.",
    "The resources were helpful but hard to find sometimes.",
]
QUAL_NEGATIVE = [
    "The program felt disconnected from my major.",
    "Scheduling conflicts made it hard to participate fully.",
    "I needed more support navigating the application process.",
]


def generate_students(n=300):
    rows = []
    student_id = 1000
    for _ in range(n):
        student_id += random.randint(1, 5)
        semester = random.choice(SEMESTERS)
        program = random.choice(PROGRAMS)
        gender = random.choice(DEMOGRAPHICS["gender"])
        race = random.choice(DEMOGRAPHICS["race_ethnicity"])
        first_gen = random.choice(DEMOGRAPHICS["first_gen"])
        year = random.choice(DEMOGRAPHICS["year"])
        college = random.choice(DEMOGRAPHICS["college"])

        # Pre-survey scores (1–5 scale)
        pre_confidence = random.randint(1, 4)
        pre_skill = random.randint(1, 4)
        pre_engagement = random.randint(1, 4)

        # Post scores — generally higher, with some variation
        boost = random.uniform(0.3, 1.5)
        post_confidence = min(5, pre_confidence + round(boost + random.uniform(-0.3, 0.5)))
        post_skill = min(5, pre_skill + round(boost + random.uniform(-0.2, 0.6)))
        post_engagement = min(5, pre_engagement + round(boost + random.uniform(-0.4, 0.7)))

        sessions_attended = random.randint(1, 12)
        total_sessions = 12
        attendance_rate = round(sessions_attended / total_sessions, 2)

        # Persistence: attended more than half
        persisted = attendance_rate >= 0.5

        # Outcomes
        got_internship = random.random() < (0.3 + 0.2 * persisted + 0.1 * (college == "Business"))
        gpa_change = round(random.uniform(-0.1, 0.4) if persisted else random.uniform(-0.2, 0.2), 2)

        # Qualitative response — weighted by engagement
        if post_engagement >= 4:
            qual = random.choice(QUAL_POSITIVE)
        elif post_engagement == 3:
            qual = random.choice(QUAL_POSITIVE + QUAL_NEUTRAL)
        else:
            qual = random.choice(QUAL_NEUTRAL + QUAL_NEGATIVE)

        rows.append({
            "student_id": student_id,
            "semester": semester,
            "program": program,
            "gender": gender,
            "race_ethnicity": race,
            "first_generation": first_gen,
            "year": year,
            "college": college,
            "pre_confidence": pre_confidence,
            "pre_skill_readiness": pre_skill,
            "pre_engagement": pre_engagement,
            "post_confidence": post_confidence,
            "post_skill_readiness": post_skill,
            "post_engagement": post_engagement,
            "sessions_attended": sessions_attended,
            "total_sessions": total_sessions,
            "attendance_rate": attendance_rate,
            "persisted": persisted,
            "secured_internship_job": got_internship,
            "gpa_change": gpa_change,
            "open_response": qual
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_students(300)
    out = os.path.join(os.path.dirname(__file__), "student_engagement_data.csv")
    df.to_csv(out, index=False)
    print(f"Generated {len(df)} student records → {out}")
    print(df.head(3).to_string())
