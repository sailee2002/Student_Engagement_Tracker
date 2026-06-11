# Data Dictionary & Collection SOP

## Required CSV Schema

| Column | Type | Values | Description |
|---|---|---|---|
| `student_id` | int | e.g. 1001 | Unique student identifier |
| `semester` | str | "Fall 2024" | Academic semester |
| `program` | str | Program name | Experiential learning pathway |
| `gender` | str | Female / Male / Non-binary / Prefer not to say | Self-reported |
| `race_ethnicity` | str | See values below | Self-reported |
| `first_generation` | bool | True / False | First in family to attend college |
| `year` | str | Freshman / Sophomore / Junior / Senior | Academic year |
| `college` | str | College/school name | Student's home college |
| `pre_confidence` | int | 1–5 | Pre-survey: confidence Likert score |
| `pre_skill_readiness` | int | 1–5 | Pre-survey: skill readiness Likert score |
| `pre_engagement` | int | 1–5 | Pre-survey: engagement Likert score |
| `post_confidence` | int | 1–5 | Post-survey: confidence Likert score |
| `post_skill_readiness` | int | 1–5 | Post-survey: skill readiness Likert score |
| `post_engagement` | int | 1–5 | Post-survey: engagement Likert score |
| `sessions_attended` | int | 0–total_sessions | Number of sessions attended |
| `total_sessions` | int | e.g. 12 | Total sessions in the program term |
| `attendance_rate` | float | 0.0–1.0 | sessions_attended / total_sessions |
| `persisted` | bool | True / False | attendance_rate >= 0.50 |
| `secured_internship_job` | bool | True / False | Outcome — internship or job secured |
| `gpa_change` | float | e.g. 0.15 | GPA change from prior semester (optional) |
| `open_response` | str | Free text | Open-ended survey response |

## race_ethnicity valid values
- Asian
- Black/African American
- Hispanic/Latino
- White
- Multiracial
- Other
- Prefer not to say

## Likert Scale Reference
1 = Strongly Disagree / Very Low  
2 = Disagree / Low  
3 = Neutral / Moderate  
4 = Agree / High  
5 = Strongly Agree / Very High  

## Data Quality Rules
- `pre_*` and `post_*` Likert scores must be integers 1–5; out-of-range values are clipped and flagged
- `attendance_rate` must be between 0 and 1
- `student_id` + `semester` should be unique per row
- `open_response` may be blank; blank values are treated as missing in qualitative analysis
- `gpa_change` is optional; rows with null values are excluded from GPA-related calculations only

## Collection Timeline

| Phase | When | Method |
|---|---|---|
| Pre-survey | Week 1 of program | Qualtrics or Google Forms |
| Attendance logging | Weekly throughout | Smartsheet / Airtable tracker |
| Post-survey | Final week of program | Qualtrics or Google Forms |
| Data merge & export | Within 1 week of program end | Manual CSV export + merge |
| Pipeline run & reporting | Within 2 weeks of program end | `python main.py` |
| Report distribution | End of semester | Email to program leads |
