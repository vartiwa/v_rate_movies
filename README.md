# 🎬 Fandango Movie Ratings Bias Analysis

A simple, interactive data analysis project replicating Walt Hickey's FiveThirtyEight investigation: *"Be Suspicious Of Online Movie Ratings, Especially Fandango's"*.

Includes an interactive web dashboard, SQL analytics sandbox, and statistical tests.

---

## 🚀 Quickstart (Run in 2 Steps)

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the app
```bash
# Windows (or simply double-click run.bat)
python -m app.main

# Or with uvicorn
python -m uvicorn app.main:app --reload
```

Open your browser and go to: **`http://localhost:8000`**

---

## 📁 Project Structure

```
├── app/                        # Web Dashboard & API
│   ├── main.py                 # FastAPI backend server
│   ├── static/                 # CSS styling & JS visualizers
│   └── templates/index.html    # Interactive dashboard UI
├── src/                        # Python Analytics Modules
│   ├── data_loader.py          # Data ingestion & validation
│   ├── analysis.py             # Calculations & distributions
│   ├── statistics.py           # Hypothesis testing (p-values & effect sizes)
│   ├── database.py             # In-memory SQLite SQL query engine
│   └── config.py               # Settings & column definitions
├── tests/                      # Automated test suite (pytest)
├── fandango_score_comparison.csv # 2015 4-platform comparison dataset
├── fandango_scrape.csv         # 2015 HTML scrape dataset
├── movie_ratings_16_17.csv     # 2016-2017 post-article dataset
├── fandango_analysis_audited.ipynb # Audited Jupyter Notebook
├── requirements.txt            # Python dependencies
├── run.bat                     # 1-click Windows launcher
└── .gitignore                  # Git ignore rules
```

---

## 📤 How to Push to GitHub

```bash
# 1. Initialize git
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit: Fandango movie rating analytics and interactive dashboard"

# 4. Link to your GitHub repository (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 5. Push to GitHub
git branch -M main
git push -u origin main
```

---

## ⚡ How to Deploy to Vercel (1-Click)

1. Go to **[vercel.com](https://vercel.com)** and sign in with your GitHub account.
2. Click **"Add New..."** → **"Project"**.
3. Select your GitHub repository (`v_rate_movies` / your repo name).
4. Click **"Deploy"** (Vercel automatically detects [`vercel.json`](file:///d:/Downloads/v_rate_movies/vercel.json) and [`api/index.py`](file:///d:/Downloads/v_rate_movies/api/index.py)).
5. Your live public URL will be ready in ~30 seconds (e.g. `https://your-project.vercel.app`)!

---

## 🧪 Run Tests

To verify that all calculations and data tests pass:
```bash
pytest
```

---

## 📊 Key Findings

1. **Upward Rounding Glitch**: In the 2015 dataset, **130 of 146 films (89.0%)** were rounded up on Fandango, causing an average artificial inflation of **+0.24 stars** (up to **+0.5 stars** boost).
2. **Competitor Comparison**: Fandango displayed stars averaged **4.09**, compared to **3.04** on Rotten Tomatoes, **2.94** on Metacritic, and **3.37** on IMDB.
3. **Post-Article Correction**: In 2016–2017 data, Fandango's displayed star rating dropped to **3.89**, closely matching 2015's true HTML baseline (3.85).
