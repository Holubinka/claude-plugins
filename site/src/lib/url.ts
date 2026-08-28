/** Every internal link has to carry the base path while the site lives on a subpath.
 *  Vite inlines BASE_URL at build time, so this works in islands too. */
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

export function href(path: string): string {
  return `${BASE}${path.startsWith('/') ? path : `/${path}`}`;
}

export function asset(path: string): string {
  return href(path);
}
