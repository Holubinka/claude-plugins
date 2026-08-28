/** Command palette, mounted on every page. The catalogue index is fetched the first
 *  time it opens, so a visitor who never presses the key pays nothing for it. */

import { useEffect, useMemo, useRef, useState } from 'preact/hooks';
import '../styles/palette.css';

interface Doc {
  id: string;
  type: string;
  plugin: string | null;
  name: string;
  title: string;
  description: string;
  invocation: string | null;
  url: string;
}

interface Row {
  key: string;
  kind: string;
  name: string;
  desc: string;
  url: string;
}

interface Props {
  docsUrl: string;
  base: string;
  pages: { name: string; desc: string; url: string }[];
}

const RECENT_KEY = 'dw:recent';

export function readRecent(): Row[] {
  try {
    const raw = localStorage.getItem(RECENT_KEY);
    const list = raw ? (JSON.parse(raw) as Row[]) : [];
    return Array.isArray(list) ? list.slice(0, 5) : [];
  } catch {
    return [];
  }
}

export default function Palette({ docsUrl, base, pages }: Props) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [active, setActive] = useState(0);
  const [docs, setDocs] = useState<Doc[] | null>(null);
  const [recent, setRecent] = useState<Row[]>([]);
  const input = useRef<HTMLInputElement>(null);
  const restoreTo = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.key === 'k' || event.key === 'K') && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        restoreTo.current = document.activeElement as HTMLElement | null;
        setQuery('');
        setActive(0);
        setRecent(readRecent());
        setOpen((was) => !was);
      } else if (event.key === 'Escape') {
        setOpen(false);
      }
    };
    addEventListener('keydown', onKey);
    return () => removeEventListener('keydown', onKey);
  }, []);

  useEffect(() => {
    if (!open) {
      restoreTo.current?.focus?.();
      return;
    }
    input.current?.focus();
    if (docs === null) {
      fetch(docsUrl)
        .then((response) => (response.ok ? response.json() : Promise.reject(new Error('index'))))
        .then((data: Doc[]) => setDocs(data))
        .catch(() => setDocs([]));
    }
  }, [open, docs, docsUrl]);

  const pageRows: Row[] = useMemo(
    () => pages.map((p) => ({ key: p.url, kind: 'page', name: p.name, desc: p.desc, url: p.url })),
    [pages],
  );

  const groups = useMemo(() => {
    const q = query.trim().toLowerCase();
    const match = (row: Row) => !q || (row.name + ' ' + row.desc).toLowerCase().includes(q);

    const fromDocs = (keep: (d: Doc) => boolean, kindOf: (d: Doc) => string): Row[] =>
      (docs ?? []).filter(keep).map((d) => ({
        key: d.id,
        kind: kindOf(d),
        name: d.invocation || d.title,
        desc: d.description,
        url: d.url,
      })).filter(match).slice(0, 6);

    const out: { label: string; rows: Row[] }[] = [];
    if (!q && recent.length) out.push({ label: 'Recently viewed', rows: recent });
    const invocable = fromDocs((d) => ['skill', 'agent', 'command'].includes(d.type), (d) => d.type);
    if (invocable.length) out.push({ label: 'Skills and agents', rows: invocable });
    const docPages = fromDocs((d) => d.type === 'doc', () => 'doc');
    if (docPages.length) out.push({ label: 'Documentation', rows: docPages });
    const listedPages = pageRows.filter(match);
    if (listedPages.length) out.push({ label: 'Pages', rows: listedPages });
    return out;
  }, [docs, query, recent, pageRows]);

  const flat = useMemo(() => groups.flatMap((g) => g.rows), [groups]);

  function go(row: Row | undefined) {
    if (!row) return;
    setOpen(false);
    location.href = row.url.startsWith('http') ? row.url : base + row.url;
  }

  function onKeyDown(event: KeyboardEvent) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setActive((i) => Math.min(i + 1, flat.length - 1));
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (event.key === 'Enter') {
      event.preventDefault();
      go(flat[active]);
    }
  }

  if (!open) return null;

  let index = -1;
  return (
    <div class="pal-scrim" onClick={(event) => { if (event.target === event.currentTarget) setOpen(false); }}>
      <div class="pal" role="dialog" aria-modal="true" aria-label="Jump to">
        <input
          ref={input}
          type="text"
          value={query}
          placeholder="Jump to a skill, a doc or a page…"
          onInput={(event) => { setQuery((event.target as HTMLInputElement).value); setActive(0); }}
          onKeyDown={onKeyDown}
        />
        <div class="pal__groups">
          {flat.length === 0 && (
            <p class="pal__empty">{docs === null ? 'Loading…' : 'Nothing matches that.'}</p>
          )}
          {groups.map((group) => (
            <div key={group.label}>
              <p class="pal__label">{group.label}</p>
              {group.rows.map((row) => {
                index += 1;
                const at = index;
                return (
                  <button
                    type="button"
                    class="pal__row"
                    key={row.key}
                    data-active={at === active ? 'true' : 'false'}
                    onMouseEnter={() => setActive(at)}
                    onClick={() => go(row)}
                  >
                    <span class="chip chip--type">{row.kind}</span>
                    <span class="pal__name">{row.name}</span>
                    <span class="pal__desc">{row.desc}</span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
        <div class="pal__foot">
          <span><kbd>↑</kbd><kbd>↓</kbd> move</span>
          <span><kbd>⏎</kbd> open</span>
          <span><kbd>esc</kbd> close</span>
        </div>
      </div>
    </div>
  );
}
