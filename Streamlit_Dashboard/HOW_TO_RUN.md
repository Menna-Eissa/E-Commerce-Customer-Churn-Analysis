# How to Open the Streamlit Dashboard

## Requirements
- Python 3.9 or newer (https://www.python.org/downloads/). During installation, tick **"Add Python to PATH"**.

## Option 1: Double-click (Windows, easiest)
1. Download or clone the project.
2. Open the `Streamlit_Dashboard` folder.
3. Double-click **`run_dashboard.bat`**.
4. The dashboard opens in your browser at `http://localhost:8501`.

## Option 2: From the terminal
```bash
cd Streamlit_Dashboard
pip install -r requirements.txt
python -m streamlit run app.py
```

## Notes
- Keep `app.py`, `logo_round.png`, and `cleaned_customer_churn.csv` in the **same folder**.
- To stop the dashboard, press `Ctrl + C` in the terminal (or close the window).
- If `streamlit` is not recognized, always use `python -m streamlit run app.py`.
- If the dashboard shows old numbers after you update the CSV, refresh the page.
