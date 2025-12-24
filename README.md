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
├── data/                      # Data storage (SQLite database, generated files)
├── src/                       # Source code
│   ├── data_generation/       # Data generation modules
│   ├── analysis/              # Analysis modules
│   └── dashboard/             # Streamlit dashboard
├── tests/                     # Test code
├── docs/                      # Documentation
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🚀 Installation

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

## 📊 Usage

### Generate Data
```bash
python src/data_generation/run_all.py
```

### Run Analysis
```bash
python src/analysis/run_all_analysis.py
```

### Launch Dashboard
```bash
streamlit run src/dashboard/app.py
```

## 🎯 Key Features

### Retention Analysis
- Cohort-based retention tracking
- Comparison of reward-earning vs non-reward users
- Statistical significance testing

### A/B Testing
- Two-proportion z-test
- Chi-square test
- Effect size calculation (Cohen's h)
- 95% confidence intervals
- Statistical power analysis

### User Segmentation
- K-means clustering
- Optimal cluster determination (Elbow Method, Silhouette Score)
- Heterogeneous treatment effect (HTE) analysis
- Segment-specific retention and conversion metrics

## 📈 Success Metrics

- **Primary Metrics**: Retention rates, conversion rates, statistical significance
- **Technical Metrics**: Code quality, test coverage, performance
- **Product Metrics**: Dashboard usability, insight actionability

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

**baobabkim**
- GitHub: [@baobabkim](https://github.com/baobabkim)

## 🙏 Acknowledgments

This project was created as a demonstration of data analysis best practices for product analytics.

---

**Status**: 🚧 In Development (Phase 1 Complete)
