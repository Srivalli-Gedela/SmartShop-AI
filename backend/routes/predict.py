from flask import Blueprint, request, jsonify
from utils.data_loader import get_dataframe
from utils.matching import resolve_product_name
from ml.predictor import predict_future_price

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict")
def predict():
    name = request.args.get("name", "").strip()
    days = request.args.get("days", type=int, default=30)
    days = max(7, min(days, 90))

    if not name:
        return jsonify({"error": "Product name required"}), 400

    df = get_dataframe()
    resolved = resolve_product_name(df, name)
    if resolved is None:
        return jsonify({"error": "No products found", "name": name}), 404
    result = predict_future_price(resolved, df, days)
    result["product_name"] = resolved
    return jsonify(result)
