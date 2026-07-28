# FreightFox — Shipment Analytics Dashboard

A Streamlit-based analytics dashboard analyzing ~5,000 shipment records to identify delivery performance issues, cost anomalies, and data quality problems.

## 🚀 Live Dashboard

**[→ View Live Dashboard](https://freightfox1.streamlit.app/)** 

## 📋 Deliverables

| # | Deliverable | Location |
|---|------------|----------|
| 1 | Source Code | This repo |
| 2 | Live Dashboard | [https://freightfox1.streamlit.app/] |
| 3 | README | This file |
| 4 | Business Answers | [`BUSINESS_ANSWERS.md`](./BUSINESS_ANSWERS.md) |
| 5 | Screen Recording | [Loom link] |

## 🛠️ Setup & Run Locally

### Prerequisites
- Python 3.10+
- pip

### Install & Run

```bash
# Clone the repo
git clone https://github.com/SidharthaKumarMalla/FreightFox.git
cd freightfox

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## 📊 Approach

### Data Exploration
I started by exploring the raw CSV to understand data shape, distributions, missing values, and quality issues. Key findings:
- 5,015 rows, 15 columns, 5 regions, 15 carriers, 120 customers
- ~30% missing `actual_delivery_date` (including In-Transit and Cancelled)
- CARR_07 charges 10× more than all other carriers
- 15 duplicate shipment IDs

### Analysis Framework
For each business question, I:
1. Computed the relevant metrics (late %, avg delay, cost residuals, etc.)
2. Cross-tabulated by dimensions (region × carrier, customer × carrier) to find root causes
3. Validated findings against data quality issues to avoid misleading conclusions

### Dashboard Design
Built with **Streamlit + Plotly** for interactive exploration:
- **Overview**: KPI cards, status breakdown, monthly trends
- **Regional Performance**: Late % by region, region×carrier heatmap, drill-down analysis
- **Cost vs Distance**: Scatter with regression, carrier deviation chart, CARR_07 outlier analysis
- **Customer Delays**: Top delayed customers, root-cause breakdown by carrier/region
- **Data Quality**: All 8 issues documented with severity and handling decisions

### Key Insights
1. **Central region** has the worst on-time performance (50.3% late), driven by CARR_08 and CARR_02
2. **CARR_07** is a 10× cost outlier — likely a premium/express carrier
3. **Customer delays are systemic**, not carrier-driven — top 5 worst customers have delays across multiple carriers and regions
4. **The `status` field is unreliable** — 499 non-Delivered rows have delivery dates, 588 Delivered rows don't

## 🗂️ Project Structure

```
├── app.py                  # Streamlit dashboard
├── shipments.csv           # Source data
├── requirements.txt        # Python dependencies
├── BUSINESS_ANSWERS.md     # Written answers to all 5 questions
├── README.md               # This file
└── explore.py              # Exploratory analysis script
```

## 🧰 Tech Stack

- **[Streamlit](https://streamlit.io/)** — Dashboard framework
- **[Plotly](https://plotly.com/)** — Interactive charts
- **[Pandas](https://pandas.pydata.org/)** — Data manipulation
- **[NumPy](https://numpy.org/)** — Numerical computations
