function subtotal(lines) {
  return lines.reduce((sum, line) => sum + line.price * line.qty, 0);
}

function withTax(amount, rate) {
  return Math.round(amount * (1 + rate));
}

module.exports = { subtotal, withTax };
