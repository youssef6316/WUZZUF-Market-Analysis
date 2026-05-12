# WUZZUF Market Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Built with Jupyter](https://img.shields.io/badge/Built%20with-Jupyter-orange.svg)](https://jupyter.org/)

## Overview

The **WUZZUF Job Market Intelligence Platform** transforms public, unstructured job data into strategic business intelligence. By automating collection and analysis of Egypt's largest job platform, we create actionable insights for:

- **Individuals** - Career guidance and salary expectations
- **Educators** - Curriculum alignment with market demands
- **Companies** - Competitive intelligence and talent trend analysis

## Project Goals

- Automate data collection from WUZZUF job listings
- Clean and standardize unstructured job market data
- Perform comprehensive exploratory data analysis (EDA)
- Visualize key insights and trends
- Generate actionable business intelligence

## Project Structure
```bash
WUZZUF-Market-Analysis/   
├── README.md                                  # Project documentation  
├── requirements.txt                           # Python dependencies   
├── 01-Data_Cleaning.ipynb                     # Data cleaning and preprocessing   
├── visuals.py                                 # Visualization utilities and functions   
├── Scraper/                                   # Web scraping scripts   
│ └── (scraper modules)   
├── Data/                                      # Data storage   
│ ├── raw/                                     # Raw scraped data   
│ └── processed/                               # Cleaned and processed data   
└── .devcontainer/                             # Development container config
```


## Key Features

### Data Collection
- Automated web scraping from WUZZUF platform
- Efficient data extraction and storage
- Respect for website terms of service and ethical guidelines

### Data Processing
- Comprehensive data cleaning and validation
- Handling missing values and duplicates
- Data normalization and transformation
- Feature engineering for analysis

### Analysis & Insights
- Salary analysis by job title, company, and experience
- Skills demand and market trends
- Job location distribution
- Employment type analysis
- Career path insights

### Visualization
- Interactive dashboards and plots
- Professional visualizations for stakeholder presentations
- Trend analysis charts
- Distribution and comparison visualizations

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| **Python 3.8+** | Core programming language |
| **Pandas** | Data manipulation and analysis |
| **NumPy** | Numerical computing |
| **Plotly** | Interactive visualizations |
| **Streamlit** | Web application framework |
| **Jupyter Notebook** | Interactive analysis and exploration |
| **BeautifulSoup/Selenium** | Web scraping |

## Requirements
streamlit pandas plotly numpy

Code

For complete dependencies, see `requirements.txt`

## 💻 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/youssef6316/WUZZUF-Market-Analysis.git
cd WUZZUF-Market-Analysis
```
Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
🚀 Usage
Running Data Cleaning
```bash
jupyter notebook 01-Data_Cleaning.ipynb
```
Running Web Scraper
```bash
python Scraper/scraper.py
```
Launching Streamlit Dashboard
```bash
streamlit run app.py
```

# Analysis Outputs
The project generates the following insights:

Salary Statistics: Mean, median, and distribution by various factors
Skills Demand: Most sought-after technical and soft skills
Market Trends: Growth areas and declining sectors
Geographic Analysis: Job distribution across Egypt
Company Insights: Top hiring companies and industry leaders
Career Pathways: Progression patterns and salary growth trajectories

# Data Pipeline

Code
Raw Data (WUZZUF)
        ↓
    Scraper
        ↓
Raw Dataset (CSV/JSON)
        ↓
Data Cleaning (01-Data_Cleaning.ipynb)
        ↓
Processed Dataset
        ↓
Analysis & Visualization (visuals.py)
        ↓
Business Intelligence Dashboard

# Use Cases
Career Planning - Job seekers can identify high-demand skills and salary trends
Curriculum Development - Educational institutions can align programs with market needs
Recruitment Strategy - Companies can benchmark salaries and identify talent pools
Market Research - Investors can analyze employment trends and economic indicators
Skill Gap Analysis - Identify emerging skills and training opportunities

# Contributing
Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

# License
This project is licensed under the MIT License - see the LICENSE file for details.

# Disclaimer
Educational Purpose: This project is for educational and research purposes
Data Usage: Ensure compliance with WUZZUF's Terms of Service and robots.txt
Ethical Scraping: Implement rate limiting and respect website policies


Last Updated: May 2026

