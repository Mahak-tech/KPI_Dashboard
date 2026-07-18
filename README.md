# 📊 Customer Sentiment KPI Dashboard

A KPI dashboard built with **Streamlit**, **TextBlob**, and **Plotly** that analyzes
customer review text, scores sentiment, and visualizes key metrics and trends.

## Features
- Sentiment scoring (polarity + subjectivity) on review text using TextBlob
- KPI cards: total reviews, average polarity, average rating, % positive/negative
- Sentiment distribution pie chart
- Sentiment trend over time (line chart)
- Polarity score histogram
- Average rating by product (bar chart)
- Overall sentiment health gauge
- Filterable, sortable, downloadable data table
- Upload your own CSV or use the bundled sample dataset

## Project Structure
```
kpi-dashboard/
├── app.py                     # Main Streamlit app
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── data/
│   └── sample_reviews.csv     # Sample dataset (50 customer reviews)
└── utils/
    ├── __init__.py
    └── sentiment.py           # TextBlob sentiment helper functions
```

## Prerequisites
- Python 3.9+ installed
- VS Code (with the Python extension installed, recommended)

## Setup & Run — Step by Step (VS Code)

### 1. Unzip and open the project
Unzip `kpi-dashboard.zip`, then in VS Code:
`File → Open Folder... → select the kpi-dashboard folder`

### 2. Open a terminal in VS Code
`Terminal → New Terminal` (make sure it's opened at the project root, where `app.py` lives)

### 3. Create a virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```
In VS Code, when prompted, select this `venv` as your Python interpreter
(`Ctrl+Shift+P` → `Python: Select Interpreter` → choose the `venv` one).

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Download TextBlob's language corpora (one-time step)
TextBlob needs NLTK corpora for tokenization/POS tagging:
```bash
python -m textblob.download_corpora
```

### 6. Run the Streamlit app
```bash
streamlit run app.py
```

### 7. View it in your browser
Streamlit will automatically open a browser tab, or you can go to:
```
http://localhost:8501
```
If port 8501 is busy, Streamlit will pick the next free port and print the
correct URL in the terminal — use that one instead.

### 8. Stop the app
In the terminal, press `Ctrl+C`.

## Using Your Own Data
Upload a CSV via the sidebar's "Upload your own CSV" control. Required column:
- `date` (any parseable date format)
- `review` (the free-text you want scored)

Optional columns that unlock extra charts/filters:
- `rating` (numeric, e.g. 1–5)
- `product` (text, used for the "Average Rating by Product" chart and filter)
- `customer` (text, shown in the detail table)

## Troubleshooting
- **`ModuleNotFoundError: No module named 'textblob'`** → make sure your venv is
  activated and you ran `pip install -r requirements.txt` inside it.
- **TextBlob errors about missing corpora** → re-run
  `python -m textblob.download_corpora`.
- **Port already in use** → run `streamlit run app.py --server.port 8502` (or any
  free port).
- **Blank/empty charts** → check your sidebar filters aren't excluding all rows.
- **`meson.build ... ERROR: Could not find vswhere.exe` while installing pandas** →
  this happens when pip can't find a prebuilt "wheel" for pandas that matches your
  Python version, so it falls back to compiling pandas from source, which needs
  Meson **and** the Microsoft Visual Studio C++ build tools installed on your
  machine. This project now pins `pandas==2.2.3`, which ships prebuilt Windows
  wheels for Python 3.9–3.13, so a plain `pip install -r requirements.txt` should
  no longer try to build from source. If you still hit this:
  1. Confirm your Python version with `python --version`. Python 3.13 or newer
     needs pandas 2.2.3+ (already set here); Python 3.8 or older isn't supported
     by pandas 2.2.x at all — upgrade Python.
  2. Delete and recreate your `venv` after updating `requirements.txt`, then
     re-run `pip install -r requirements.txt`.
  3. As a last resort, upgrade pip first (`python -m pip install --upgrade pip`)
     so it can find the right wheel, or install the
     [Visual Studio "Desktop development with C++"](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
     workload so a from-source build can succeed.
