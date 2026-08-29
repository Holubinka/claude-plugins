const { db } = require("../lib/db");

// The handler talks to the database directly. Whether that is a violation depends
// entirely on rules this repository has never written down.
async function listOrders(req, res) {
  const rows = await db.query("select * from orders where customer_id = $1", [req.params.id]);
  res.json(rows);
}

module.exports = { listOrders };
