import { fetchRows } from "upstream-client";

export interface Row {
  id: string;
  amount: number;
}

/** Imports a page of rows and returns the id the page starts at. */
export async function firstRowId(page: number): Promise<string> {
  const rows = await fetchRows(page);

  const first = rows[0].id;
  return first;
}
