# 📊 E-Commerce Customer Churn Analysis

An end-to-end data project that answers one question: **why do customers leave, and who is most at risk?**

The project has two parts:

1. **Jupyter Notebook:** data cleaning, exploratory analysis, and statistics.
2. **Streamlit Dashboard:** an interactive dashboard built on the cleaned data.

> Built by **[Menna Muhammad Ali]** and team: **[Noura Ibrahim Labeb]**, **[Amin Mohammed Amin]**, **[Mariam Reda Ahmed]**, **[Mohamed Ahmed Abdel Fattah]**


## 📁 Project Structure

```
E-Commerce-Customer-Churn-Analysis/
├── Jupyter_Notebook_Python_Code/
│   ├── E-Commerce-Customer-Churn-Analysis.ipynb   # Cleaning + analysis
│   ├── customer churn.csv                         # Raw dataset (10,300 rows)
│   ├── cleaned_customer_churn.csv                 # Cleaned dataset (10,000 rows)
│   ├── churn_dashboard.png
│   └── payment-methods.jpg
├── Streamlit_Dashboard/
│   ├── app.py                                     # Streamlit dashboard
│   ├── logo_round.png                             # Sidebar logo
│   ├── cleaned_customer_churn.csv                 # Data used by the dashboard
│   └── requirements.txt
└── README.md
```

---

## 🗂️ Dataset

Each row is one e-commerce customer.

| Column | Description |
|---|---|
| `Customer_ID` | Unique customer identifier |
| `Gender` | Male, Female, Non-Binary, Unknown |
| `Region` | East, West, North, South |
| `Subscription_Plan` | Basic, Plus, Pro |
| `Payment_Method` | Credit Card, PayPal, E-Wallet, Crypto, Unknown |
| `Age` | Customer age |
| `Days_Since_Last_Login` | Days since the customer last logged in |
| `Customer_Service_Calls` | Number of service calls |
| `Monthly_Spend` | Monthly spend |
| `Churn` | 1 = churned, 0 = retained |

---

## 🧹 Data Cleaning (10,300 raw rows → 10,000 clean customers)

| Issue found | How it was handled |
|---|---|
| 300 duplicate rows | Removed duplicates |
| Inconsistent capitalization (Region had 8 values, Subscription Plan had 6) | Standardized to 4 regions and 3 plans |
| Invalid ages (e.g. -10 and 150) and 995 missing ages | Ages outside 18–70 treated as invalid, then filled with the median |
| Monthly Spend outliers (from -10 up to 99,999.99) and 500 missing values | Values below 0 or above 312 treated as invalid, then filled with the median of each subscription plan |
| Negative `Customer_Service_Calls` | Replaced with the median |
| 700 missing `Payment_Method` values | Kept as `"Unknown"` (see below) |

### Why Payment Method stayed "Unknown"

Three approaches were compared: filling with `"Unknown"`, grouping by plan and age group, and a Random Forest classifier. Both predictive methods reached only about **24% accuracy**, which is no better than guessing among 4 options. So predicting the values would have added incorrect information, and they were kept as `"Unknown"`.

### Why Age used the median

A Random Forest regressor was compared with median imputation. The median performed better (MAE 7.15 vs 7.67), so it was used.

---

## 📈 Dashboard Features

- **KPI cards:** total customers, churn rate, average monthly spend, average service calls, average age
- **Sidebar filters:** region, subscription plan, gender, payment method, age range, customer status
- **Overview tab:** retained vs churned, payment method distribution, age distribution, customers by gender
- **Churn Drivers tab:** churn by login activity, days since last login, plan, and region, plus service calls and spend by status
- **Correlation tab:** correlation matrix of the numeric variables
- **Bivariate Analysis tab:** monthly spend by plan, churn rate by region and plan
- **Data tab:** browse and download the filtered data as CSV

---

## 🛠️ Tech Stack

Python • Pandas • NumPy • Scikit-learn • Matplotlib • Seaborn • Plotly • Streamlit • Jupyter

---

