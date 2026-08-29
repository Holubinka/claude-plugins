export function total(rows: any[]) {
  const first = rows[0] as { amount: number };
  return first.amount;
}
