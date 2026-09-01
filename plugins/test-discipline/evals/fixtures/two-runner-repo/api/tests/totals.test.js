const test = require("node:test");
const assert = require("node:assert/strict");
const { subtotal, largestLine } = require("../src/totals");

test("subtotal sums price by quantity", () => {
  assert.equal(subtotal([{ price: 2, qty: 3 }, { price: 1, qty: 1 }]), 7);
});

test("largestLine returns an empty array when nothing is over the threshold", () => {
  assert.deepEqual(largestLine([{ price: 1, qty: 1 }], 100), []);
});
