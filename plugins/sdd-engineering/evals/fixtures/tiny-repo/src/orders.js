// The only module. A route handler that also talks to the database, which is the
// boundary violation some cases ask an agent to notice.
export async function createOrder(req, db) {
  const row = await db.query('INSERT INTO orders (customer_id) VALUES ($1) RETURNING *', [
    req.body.customerId,
  ]);
  return row;
}
