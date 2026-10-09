# SmartShop v4 — Upgrade Notes

## 1. Badges (`backend/routes/compare.py`)
- **Best Deal** badge → listing with strictly the lowest price (ties broken by AI score)
- **Best Value** badge → listing with highest AI score (ties broken by lowest price)
- **Combined badge** shown when both are the same listing
- Each badge has its own colour: green (Best Deal), indigo (Best Value), amber (Combined)

## 2. UI Clarity (`frontend/static/js/product.js`, `app.js`)
- Best Deal explanation: *"Lowest price among all stores. Save ₹X compared to the most expensive listing."*
- Best Value explanation: *"Best overall choice based on price, rating, and reviews. AI Score N/100 — rated X★, excellent reviews."*
- Savings = max_price − min_price (calculated server-side)
- Highlighted listing rows with left-border accent

## 3. AI Score Consistency (`backend/ml/ai_score.py`)
- Re-weighted: **Price 40 % | Rating 30 % | Reviews 20 % | Recency 10 %**
- Price is now the largest single factor (the cheapest listing usually, but not always, has the top AI score)
- Review sentiment falls back to keyword mapping from `reviews` text when numeric sentiment is missing

## 4. Forecasting (`backend/ml/predictor.py`)
- **Base price = best-deal (lowest) price** — consistent with comparison UI
- ML pipeline kept: Gradient Boosting primary, Polynomial Ridge fallback
- Synthetic series uses tighter noise (0.3–1.5 %) for a more stable anchor
- Post-processing: light EMA (α = 0.40) + deterministic ±2 % noise seeded by product name
- 30-day forecast is stable across repeated calls AND server restarts (seed uses crc32, not Python's randomised hash())

## 5. Recommendation
- `WAIT`  → avg change < −3 %
- `HOLD`  → −3 % ≤ change ≤ +2 %
- `BUY`   → change > +2 %
- Explanation text always matches the predicted direction

## 6. Confidence
- Clamped to **70–85 %** (realistic UI range)
- Formula: `85 − MAPE × 1.5`, floored at 70

## 7. Consistency
- `current_price` in forecast response = cheapest listing price = same number shown in comparison UI
- All three surfaces (comparison cards, forecast header, recommendation) derive from the same base price

## 8. Pre-release fixes
- Added missing `flask-cors` to `requirements.txt` (app failed to start without it); added `.gitignore`, removed committed `__pycache__`
- `/api/predict` and `/api/compare` now share one name-matching helper (`utils/matching.py`): exact match first, then substring; `/api/predict` returns 404 for unknown products
- `page` / `per_page` validated (`per_page` 1–100); search text is matched literally (no regex errors)
- AI scores computed once on the full dataset and cached → ~100× faster and identical across search / compare / product / summary
- Frontend: escaped error messages, `http(s)`-only product links with `rel="noopener noreferrer"`, safer `escAttr`
