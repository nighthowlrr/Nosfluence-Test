import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")  # e.g. your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")  # from env

@app.route("/check_order", methods=["GET"])
def check_order():
    email = request.args.get("email")
    order_id = request.args.get("order_id")

    if not email and not order_id:
        return jsonify({"error": "Missing email or order ID"}), 400

    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    if email:
        url = f"https://{SHOPIFY_STORE}/admin/api/2023-10/orders.json?email={email}"
    else:
        url = f"https://{SHOPIFY_STORE}/admin/api/2023-10/orders.json?name={order_id}"

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return jsonify({"error": "Shopify API error", "details": response.text}), 500

    orders = response.json().get("orders", [])
    if not orders:
        return jsonify({"status": "No order found"}), 404

    order = orders[0]
    status = order["fulfillment_status"] or "Unfulfilled"
    tracking_info = order.get("fulfillments", [])
    tracking_number = "Not yet shipped"

    if tracking_info and "tracking_number" in tracking_info[0]:
        tracking_number = tracking_info[0]["tracking_number"]

    return jsonify({
        "order_id": order["name"],
        "status": status,
        "tracking": tracking_number
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
