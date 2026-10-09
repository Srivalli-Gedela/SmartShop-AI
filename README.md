# ⚡ SmartShop AI — Laptop Price Intelligence

A full-stack ML web application for comparing laptop prices across **Amazon**, **Flipkart**, and **BestBuy**, with AI scoring, AI summaries, and future price prediction.

---

## 📁 Folder Structure

```
smartshop_v4/
├── requirements.txt
├── .gitignore
├── CHANGES.md
├── backend/
│   ├── app.py                    # Flask entry point
│   ├── data/
│   │   └── products.csv          # Your dataset (3,370 laptops)
│   ├── ml/
│   │   ├── ai_score.py           # AI Score calculation (weighted ML)
│   │   ├── summarizer.py         # AI Summary generation
│   │   └── predictor.py          # Linear Regression price forecasting
│   ├── routes/
│   │   ├── search.py             # GET /api/search
│   │   ├── compare.py            # GET /api/compare
│   │   ├── predict.py            # GET /api/predict
│   │   └── summary.py            # GET /api/summary/<id>
│   └── utils/
│       ├── data_loader.py        # CSV loading + data cleaning
│       └── matching.py           # Shared product-name matching (compare + predict)
└── frontend/
    ├── templates/
    │   ├── index.html            # Home page
    │   └── product.html          # Product detail page
    └── static/
        ├── css/
        │   └── style.css         # Full dark-theme UI
        └── js/
            ├── app.js            # Search, compare, forecast logic
            └── product.js        # Product detail page logic
```

---

## 🚀 Setup & Run

### 1. Install Python dependencies
```bash
cd smartshop_v4
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Flask server
```bash
cd backend
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?q=dell&website=amazon&sort=ai_score&page=1` | Search + filter + paginate |
| GET | `/api/product/<id>` | Single product detail |
| GET | `/api/compare?name=Dell XPS 15` | Cross-site price comparison |
| GET | `/api/predict?name=HP TPN-Q279&days=30` | ML price forecast |
| GET | `/api/summary/<id>` | AI-generated text summary |

### Filter parameters for `/api/search`:
- `q` — search query
- `website` — `all`, `amazon`, `flipkart`, `bestbuy`
- `sort` — `ai_score`, `price_asc`, `price_desc`, `rating`
- `min_price`, `max_price` — INR price range
- `page`, `per_page` — pagination (`per_page` is capped at 100)

---

## 🤖 ML Features

### AI Score (0–100)
Weighted combination (computed on the full dataset, so a product's score is the same on every page):
- **Price competitiveness** (40%) — how cheap vs. other listings of the same product
- **Rating** (30%) — numeric 1–5 star rating
- **Review sentiment** (20%) — review text mapped to a 1–5 scale
- **Recency** (10%) — how recent the listing date is

Price is the biggest factor, so the cheapest listing usually — but not always — has the highest score.

### AI Summary
Parses `product_description` to extract specs (Processor, RAM, Storage, OS, Display) and generates a readable summary.

### Price Forecast
Gradient Boosting (Polynomial Ridge fallback) over lag / rolling / day-of-week features, predicting step by step, then lightly smoothed. Forecasts are deterministic per product.

> **Note:** the dataset only spans ~2 days of scraped prices, so there is no real price history. When a product has too few rows the model trains on a *synthetic* series anchored to the lowest listing price, and the confidence value is clamped to 70–85%. Treat the forecast as a **demo of the ML pipeline, not financial advice**. `WAIT` < −3%, `HOLD` −3%…+2%, `BUY` > +2%.

---

## 📊 Dataset Details

| Field | Notes |
|-------|-------|
| `ratings` | String — `"4.5"` or `"Not Available"` → cleaned to float |
| `reviews` | Sentiment text — mapped to 1–5 score |
| `price` | Float (INR) — range ₹3,734 to ₹5,06,299 |
| `website` | Amazon · Flipkart · BestBuy |
| `image_link` | Mostly `"Not Available"` → replaced with placeholder |
| `date` | Datetime string → parsed for recency scoring |

---

## 🎨 UI Features
- Dark theme inspired by Flipkart/Amazon
- Product grid with AI Score bars
- Review sentiment tags (Excellent / Very Good / Average / Poor)
- Price comparison modal (cross-site)
- Price forecast modal with bar chart
- Product detail page with specs table + AI summary
- Pagination, filters, sort controls
- Fully responsive
