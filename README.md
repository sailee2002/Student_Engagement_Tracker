# 📊 Student Engagement & Outcomes Tracker

A data analytics pipeline for tracking, analyzing, and reporting on student engagement, persistence, and learning outcomes across experiential learning programs. Built to support higher education program teams in making evidence-based decisions using both quantitative and qualitative data.

---

## 🎯 Project Purpose

Higher education programs collect rich data on student demographics, survey responses, attendance, and outcomes — but it often lives in disconnected spreadsheets with no systematic analysis workflow. This project provides:

- A **structured data tracking system** for multi-semester student records
- **Pre/post survey analysis** to measure learning gains across pathways
- **Multi-year trend synthesis** to identify patterns for strategic planning
- **Qualitative theme extraction** from open-response survey data
- **Equity analysis** disaggregated by demographics (first-gen, race/ethnicity)
- **Auto-generated written summaries** translating data findings into actionable recommendations
- **Documented, transferable workflows** for sustainable program tracking

---

## 📁 Repository Structure

```
student-engagement-tracker/
│
├── data/
│   ├── generate_data.py          # Mock data generator (replace with real data)
│   └── student_engagement_data.csv
│
├── notebooks/
│   └── analysis_notebook.ipynb   # Interactive step-by-step analysis
│
├── reports/
│   ├── figures/                  # Auto-generated visualizations (6 charts)
│   └── summary_report.txt        # Auto-generated written summary report
│
├── docs/
│   └── DATA_DICTIONARY.md        # Field definitions and data collection SOP
│
├── analysis.py                   # Core analysis functions
├── visualizations.py             # All chart generation
├── main.py                       # Full pipeline runner
├── requirements.txt
└── README.md
```

---

## 🔧 Setup & Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate sample data (or plug in your own)

```bash
python data/generate_data.py
```

To use **real data**: replace `data/student_engagement_data.csv` with your own file. See `docs/DATA_DICTIONARY.md` for required columns and formatting.

### 3. Run the full pipeline

```bash
python main.py
```

This will:
- Load and clean the data
- Run quantitative and qualitative analysis
- Generate 6 visualizations in `reports/figures/`
- Write a narrative summary to `reports/summary_report.txt`

### 4. Explore interactively

Open `notebooks/analysis_notebook.ipynb` in Jupyter for step-by-step walkthrough with inline outputs.

---

## 📊 What Gets Analyzed

| Analysis | Description |
|---|---|
| **Demographic breakdown** | Gender, race/ethnicity, first-gen status, year, college |
| **Pre/Post survey gains** | Confidence, skill readiness, engagement — by program and semester |
| **Persistence tracking** | % of students completing ≥50% of sessions |
| **Outcome rates** | Internship/job secured, GPA change |
| **Multi-semester trends** | Enrollment, persistence, and gain trends over time |
| **Equity analysis** | Outcome gaps by first-gen status and race/ethnicity |
| **Qualitative themes** | Keyword-based theme extraction from open-response survey data |
| **Sentiment analysis** | Positive/neutral/negative response classification |
| **Narrative report** | Auto-generated written summary with recommendations |

---

## 📈 Sample Outputs

**6 auto-generated charts:**
1. Pre vs. Post survey scores (grouped bar)
2. Enrollment, persistence & learning gains by semester (dual-axis trend)
3. Program performance heatmap
4. Qualitative theme frequency (horizontal bar)
5. Equity analysis — gains by first-gen status and race/ethnicity
6. Attendance rate vs. learning gains (scatter with trendline)

**Auto-generated report excerpt:**
```
STUDENT ENGAGEMENT & OUTCOMES TRACKER — STRATEGIC SUMMARY REPORT

1. LEARNING GAINS: Students showed an average overall gain of 1.02 points
   across confidence, skill readiness, and engagement metrics.

2. PROGRAM PERFORMANCE: 'Experiential Learning' consistently produced the
   highest learning gains. Cross-program replication recommended.

3. PERSISTENCE: 57% of students persisted through ≥50% of sessions.
   Among persisters, 39% secured an internship or job.

RECOMMENDATIONS:
• Scale delivery elements from highest-performing program to other pathways.
• Introduce mid-semester check-in surveys for early at-risk identification.
• Add flexible scheduling options (flagged in qualitative themes).
```

---

## 🗂️ Data Collection SOP

### Step 1 — Pre-Survey (Program Start)
Collect via Qualtrics or Google Forms. Required fields:
- Student ID, semester, program enrolled
- Demographic info (gender, race/ethnicity, first-gen, year, college)
- Likert ratings: confidence (1–5), skill readiness (1–5), engagement (1–5)

### Step 2 — Attendance Tracking
Log weekly via Smartsheet or Airtable tracker. Fields: student_id, session_date, attended (Y/N).
Export as CSV at end of semester; compute `sessions_attended` and `attendance_rate`.

### Step 3 — Post-Survey (Program End)
Same Likert questions as pre-survey, plus:
- Open-response: *"What was most valuable about this program? What could be improved?"*
- Outcome: *"Have you secured an internship or job since joining this program?"*

### Step 4 — Data Consolidation
Merge pre/post surveys on `student_id` and `semester`. Export final CSV matching the schema in `docs/DATA_DICTIONARY.md`. Run `python main.py` to generate analysis and report.

### Step 5 — Review & Distribution
Share `reports/summary_report.txt` and figures with program leads after each semester. Archive raw data and reports by semester in a shared drive.

---

## 🔄 Extending This Project

- **Swap in real data**: match your CSV to the schema in `docs/DATA_DICTIONARY.md`
- **Add Airtable/Smartsheet integration**: use their APIs to auto-pull tracker data instead of manual CSV export
- **Add a Tableau/Power BI layer**: connect to the CSV for live dashboarding
- **Automate with Airflow**: schedule `main.py` to run after each semester data freeze
- **Add SPSS-style statistics**: extend `analysis.py` with t-tests, chi-square, regression

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core analysis and pipeline |
| Pandas | Data cleaning, transformation, aggregation |
| NumPy | Numerical operations |
| Matplotlib / Seaborn | Data visualization |
| Jupyter Notebook | Interactive exploration |
| CSV / Excel | Data storage (mirrors real-world higher ed tools) |
| Qualtrics / Google Forms | Survey collection (external, documented in SOP) |
| Smartsheet / Airtable | Attendance tracking (external, documented in SOP) |

---

## 👩‍💻 Author

**Sailee Choudhari**  
M.S. Data Analytics Engineering, Northeastern University  
[LinkedIn](https://www.linkedin.com/in/sailee-choudhari/) 




