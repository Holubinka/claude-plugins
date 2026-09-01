import { describe, it, expect } from "vitest";
import { currency } from "./format";

describe("currency", () => {
  it("renders cents as a decimal", () => {
    expect(currency(1250)).toBe("12.50");
  });
});
