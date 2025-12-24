# Data Analysis Project: Retention & A/B Testing

A comprehensive data analysis project demonstrating retention analysis, A/B testing, and user segmentation using Python and Streamlit.

## 📋 Project Overview

This project implements a complete data analysis pipeline for a mobile app scenario, including:
- **Synthetic data generation** for 10,000+ users with realistic behavior patterns
- **Retention analysis** with cohort-based metrics (D1, D3, D7, D14, D30)
- **A/B testing** with statistical significance testing
- **User segmentation** using K-means clustering
- **Interactive dashboard** built with Streamlit

## 🛠️ Tech Stack

- **Python 3.8+** - Core programming language
- **SQLite** - Lightweight database for data storage
- **Pandas & NumPy** - Data manipulation and analysis
- **SciPy & Statsmodels** - Statistical testing
- **Scikit-learn** - Machine learning and clustering
- **Streamlit** - Interactive dashboard framework
- **Matplotlib, Seaborn, Plotly** - Data visualization

## 📁 Project Structure

```
apply-demo-2/
├── data/                          # Data storage
│   ├── app_data.db               # SQLite database
│   └── analysis_results/         # Analysis outputs (JSON)
├── src/                          # Source code
│   ├── data_generation/          # Data generation modules
│   │   ├── create_db.py         # Database schema creation
│   │   ├── generate_users.py    # User data generation
│   │   ├── generate_logs.py     # Behavior log generation
│   │   ├── generate_ab_test.py  # A/B test data generation
│   │   └── run_all.py           # Data generation pipeline
│   ├── analysis/                 # Analysis modules
│   │   ├── retention_analysis.py    # Retention metrics
│   │   ├── ab_test_analysis.py      # A/B test statistics
│   │   ├── segment_analysis.py      # User segmentation
│   │   └── run_all_analysis.py      # Analysis pipeline
│   └── dashboard/                # Streamlit dashboard
│       └── app.py               # Main dashboard app
├── tests/                        # Test code
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/baobabkim/apply-demo-2.git
cd apply-demo-2
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate data
```bash
python src/data_generation/run_all.py
```

This will create:
- SQLite database with 10,000 users
- 700,000+ behavior event logs
- A/B test assignments and conversions

**Expected output:**
```
[1/4] Creating database schema...
[2/4] Generating user data...
[3/4] Generating behavior logs...
[4/4] Generating A/B test data...
Total time: ~30 seconds
```

### 5. Run analysis
```bash
python src/analysis/run_all_analysis.py
```

This will generate:
- Retention analysis (D1-D30 metrics)
- A/B test statistical testing
- User segmentation (K-means clustering)

**Expected output:**
```
[1/3] Running retention analysis...
[2/3] Running A/B test analysis...
[3/3] Running segment analysis...
Total time: ~20 seconds
```

### 6. Launch dashboard
```bash
streamlit run src/dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📊 Key Features

### Retention Analysis
- **Cohort-based retention tracking** (D1, D3, D7, D14, D30)
- **Reward impact analysis**: Comparison of users who earned rewards vs those who didn't
- **Statistical significance testing**: Chi-square tests for retention differences
- **Cohort analysis**: Weekly cohort retention patterns

**Key Finding:** Users earning rewards within 24 hours show 97%+ retention vs 70-75% for non-reward users (p < 0.0001)

### A/B Testing
- **Two-proportion z-test** for conversion rate comparison
- **Chi-square test** for independence
- **Effect size calculation** (Cohen's h)
- **95% confidence intervals**
- **Statistical power analysis**

**Key Finding:** Treatment shows 6.69% relative lift but is not statistically significant (p = 0.1152, power = 35%)

### User Segmentation
- **K-means clustering** with optimal cluster determination
- **Elbow Method** and **Silhouette Score** for cluster validation
- **Segment-specific retention** and conversion metrics
- **Heterogeneous Treatment Effect (HTE)** analysis

**Key Finding:** Three distinct segments identified:
- Low-engagement (51%): 30 avg events, 84% D7 retention
- Medium-engagement (37%): 95 avg events, 99.9% D7 retention
- High-engagement (12%): 205 avg events, 100% D7 retention

## 📈 Dashboard Pages

1. **Overview**: KPIs and project summary
2. **Retention Analysis**: Retention curves and cohort analysis
3. **A/B Test Results**: Statistical test results and recommendations
4. **User Segmentation**: Cluster characteristics and HTE analysis
5. **Insights & Actions**: Key findings and recommended actions

## 🧪 Testing

Run tests (when implemented):
```bash
pytest tests/
```

## 📝 Documentation

- **PRD.md**: Product Requirements Document
- **TASK.md**: Implementation task list
- **Idelation.md**: Initial ideation and planning

## 🎯 Success Metrics

### Primary Metrics
- ✅ D7 Retention: 92.91%
- ✅ Reward impact: 27% higher retention for reward users
- ⚠️ A/B test: Not statistically significant (needs longer test)

### Technical Metrics
- ✅ Data generation: ~30 seconds for 10K users
- ✅ Analysis pipeline: ~20 seconds
- ✅ Dashboard load time: <2 seconds

### Product Metrics
- ✅ Interactive visualizations with Plotly
- ✅ Clear insights and actionable recommendations
- ✅ Comprehensive statistical analysis

## 🔧 Development

### Adding new analysis modules
1. Create new file in `src/analysis/`
2. Implement analysis function
3. Add to `run_all_analysis.py`
4. Update dashboard to display results

### Modifying data generation
1. Edit relevant file in `src/data_generation/`
2. Re-run `run_all.py` to regenerate data
3. Re-run analysis pipeline

## 📚 Key Insights

1. **Reward Timing is Critical**: Getting users to earn rewards within 24 hours dramatically improves retention
2. **Segment-Specific Strategies**: Low-engagement users respond best to treatment variant
3. **Statistical Power Matters**: Current A/B test needs larger sample or longer duration
4. **Cohort Patterns**: Retention is consistent across signup cohorts

## 🚀 Recommended Actions

1. **Optimize onboarding** to guide users to first reward within 24 hours
2. **Implement personalized engagement** based on user segments
3. **Continue A/B test** to reach statistical significance
4. **Monitor high-engagement users** for any negative treatment effects

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

**baobabkim**
- GitHub: [@baobabkim](https://github.com/baobabkim)

## 🙏 Acknowledgments

This project demonstrates best practices in:
- Product analytics and experimentation
- Statistical hypothesis testing
- Data visualization and storytelling
- Reproducible data science workflows

---

**Status**: ✅ Complete (All 7 phases implemented)

**Last Updated**: December 2024
