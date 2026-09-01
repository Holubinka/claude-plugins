function subtotal(lines) {
  return lines.reduce((sum, line) => sum + line.price * line.qty, 0);
}

// Returns the first line over the threshold, or undefined when none is.
function largestLine(lines, threshold) {
  return lines.find((line) => line.price * line.qty > threshold);
}

module.exports = { subtotal, largestLine };
