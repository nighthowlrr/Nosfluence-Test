import os
import requests

def handler(request):
    email = request.args.get("email")
    order_id = request.args.get("order_id")

    SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
    SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

    if not email and not order_id:
        return {"statusCode": 400, "body": "Missing email or order ID"}

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
        return {"statusCode": 500, "body": "Shopify API error"}

    orders = response.json().get("orders", [])
    if not orders:
        return {"statusCode": 404, "body": "No order found"}

    order = orders[0]
    status = order["fulfillment_status"] or "Unfulfilled"
    tracking = (
        order.get("fulfillments", [{}])[0].get("tracking_number", "Not yet shipped")
    )

    return {
        "statusCode": 200,
        "body": {
            "order_id": order["name"],
            "status": status,
            "tracking": tracking
        }
    }
