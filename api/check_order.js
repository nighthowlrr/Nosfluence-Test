const fetch = require('node-fetch');

module.exports = async (req, res) => {
  const { email, order_id, limit = 1 } = req.query;

  const SHOPIFY_STORE = process.env.SHOPIFY_STORE;
  const SHOPIFY_ACCESS_TOKEN = process.env.SHOPIFY_ACCESS_TOKEN;

  if (!SHOPIFY_STORE || !SHOPIFY_ACCESS_TOKEN) {
    return res.status(500).json({ error: "Missing Shopify config." });
  }

  if (!email && !order_id) {
    return res.status(400).json({ error: "Missing email or order ID" });
  }

  const headers = {
    'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
    'Content-Type': 'application/json'
  };

  let url = '';
  if (email) {
    url = `https://${SHOPIFY_STORE}/admin/api/2023-10/orders.json?email=${encodeURIComponent(email)}&status=any&limit=${limit}&order=created_at desc`;
  } else {
    url = `https://${SHOPIFY_STORE}/admin/api/2023-10/orders.json?name=${encodeURIComponent(order_id)}&status=any`;
  }

  try {
    const response = await fetch(url, { headers });
    const data = await response.json();

    if (!data.orders || data.orders.length === 0) {
      return res.status(404).json({ status: "No order found" });
    }

    // If multiple orders returned (via email)
    if (email) {
      const summaries = data.orders.map(order => ({
        order_id: order.name,
        created_at: order.created_at,
        status: order.fulfillment_status || "Unfulfilled",
        tracking: order.fulfillments?.[0]?.tracking_number || "Not yet shipped"
      }));

      return res.status(200).json({
        count: summaries.length,
        orders: summaries
      });
    }

    // If order_id was used, return single order
    const order = data.orders[0];
    const status = order.fulfillment_status || "Unfulfilled";
    const tracking = order.fulfillments?.[0]?.tracking_number || "Not yet shipped";

    return res.status(200).json({
      order_id: order.name,
      status,
      tracking
    });

  } catch (err) {
    return res.status(500).json({ error: "Shopify API error", details: err.message });
  }
};
