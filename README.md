# Pulse Sales Analytics

A professional local sales dashboard for exploring revenue, profit, targets, category performance, and product leaders. It runs in your browser but stays on your computer; uploaded CSV data is not sent anywhere.

## Windows application

For everyday use, open `release/Pulse Sales Analytics/Pulse Sales Analytics.exe`. No Python installation is required. Keep the files in that release folder together when moving the app to another Windows computer.

## Run from source (developers)

1. Install **Python 3.10 or newer** from [python.org](https://www.python.org/downloads/). During installation, select **Add Python to PATH**.
2. Open Command Prompt in this folder and run:

```bat
python -m pip install -r requirements.txt
```

## Start the app

Double-click `run_app.bat`, or run:

```bat
python -m streamlit run app.py
```

The dashboard opens automatically at `http://localhost:8501`.

## CSV format

Required columns: `Product`, `Category`, `Sales`, `Profit`.

Optional columns: `Month` (for example, `January`) or `Date` (for example, `2026-08-01`). When a date is provided, the app derives the month automatically.

Use the sidebar to upload a CSV, narrow the period and categories, set a sales target, and export the selected transaction view.
