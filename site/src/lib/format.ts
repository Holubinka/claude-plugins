export function date(iso: string | null | undefined): string {
  if (!iso) return '—';
  const value = new Date(iso);
  if (Number.isNaN(value.valueOf())) return '—';
  return value.toISOString().slice(0, 10);
}

export function plural(n: number, one: string, many = `${one}s`): string {
  return `${n} ${n === 1 ? one : many}`;
}

export function authorName(author: { name?: string } | string | null): string | null {
  if (!author) return null;
  return typeof author === 'string' ? author : author.name ?? null;
}
