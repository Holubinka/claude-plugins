import { useEffect, useMemo, useRef, useState } from 'preact/hooks';
import type { SearchResult } from 'minisearch';
import { createEngine, runSearch } from '../lib/search-core.js';
import '../styles/search.css';

interface Doc {
  id: string;
  type: string;
  plugin: string | null;
  name: string;
  title: string;
  description: string;
  keywords: string[];
  headings: string[];
  body: string;
  url: string;
  invocation: string | null;
  tokens: { always: number; onLoad: number } | null;
  category: string | null;
}

interface Props {
  /** Prefixed with the site base already. */
  docsUrl: string;
  base: string;
  issueUrl: string | null;
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** Highlight matched terms without trusting anything into innerHTML. */
function mark(text: string, terms: string[]) {
  if (!terms.length || !text) return text;
  const pattern = new RegExp(`(${terms.map(escapeRegExp).join('|')})`, 'ig');
  const pieces = text.split(pattern);
  return pieces.map((piece, index) =>
    index % 2 === 1 ? <mark key={index}>{piece}</mark> : piece,
  );
}

/** A window of the field that actually matched, so a fuzzy hit is never mistaken
 *  for a good one. */
function excerpt(text: string, terms: string[], radius = 90): string {
  if (!text) return '';
  const flat = text.replace(/\s+/g, ' ').trim();
  const lower = flat.toLowerCase();
  let at = -1;
  for (const term of terms) {
    at = lower.indexOf(term.toLowerCase());
    if (at !== -1) break;
  }
  if (at === -1) return flat.slice(0, radius * 2) + (flat.length > radius * 2 ? '…' : '');
  const start = Math.max(0, at - radius);
  const end = Math.min(flat.length, at + radius);
  return (start > 0 ? '…' : '') + flat.slice(start, end).trim() + (end < flat.length ? '…' : '');
}

type Facets = { type: Set<string>; plugin: Set<string>; category: Set<string> };

function readUrl(): { q: string; facets: Facets } {
  const params = new URLSearchParams(location.search);
  const split = (key: string) => new Set((params.get(key) ?? '').split(',').filter(Boolean));
  return {
    q: params.get('q') ?? '',
    facets: { type: split('type'), plugin: split('plugin'), category: split('category') },
  };
}

export default function Search({ docsUrl, base, issueUrl }: Props) {
  const [docs, setDocs] = useState<Doc[] | null>(null);
  const [failed, setFailed] = useState(false);
  const [raw, setRaw] = useState('');
  const [facets, setFacets] = useState<Facets>({ type: new Set(), plugin: new Set(), category: new Set() });
  const [active, setActive] = useState(0);
  const input = useRef<HTMLInputElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const initial = readUrl();
    setRaw(initial.q);
    setFacets(initial.facets);
    started.current = true;

    fetch(docsUrl)
      .then((response) => (response.ok ? response.json() : Promise.reject(new Error(String(response.status)))))
      .then((data: Doc[]) => setDocs(data))
      .catch(() => setFailed(true));
  }, [docsUrl]);

  const engine = useMemo(() => (docs ? createEngine(docs) : null), [docs]);

  const results = useMemo(
    () => (engine ? (runSearch(engine, raw) as SearchResult[]) : []),
    [engine, raw],
  );

  const filtered = useMemo(
    () =>
      results.filter(
        (r) =>
          (facets.type.size === 0 || facets.type.has(r.type as string)) &&
          (facets.plugin.size === 0 || facets.plugin.has(String(r.plugin))) &&
          (facets.category.size === 0 || facets.category.has(String(r.category))),
      ),
    [results, facets],
  );

  const counts = useMemo(() => {
    const tally = (key: 'type' | 'plugin' | 'category') => {
      const out = new Map<string, number>();
      for (const r of results) {
        const value = r[key] as string | null;
        if (value) out.set(value, (out.get(value) ?? 0) + 1);
      }
      return [...out].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    };
    return { type: tally('type'), plugin: tally('plugin'), category: tally('category') };
  }, [results]);

  const searching = raw.trim().length >= 2;
  const ready = docs !== null;

  // The prerendered browse listing stays the content until a query is active.
  useEffect(() => {
    document.getElementById('browse')?.toggleAttribute('hidden', searching);
  }, [searching]);

  // Shareable searches, without flooding history.
  useEffect(() => {
    if (!started.current) return;
    const id = setTimeout(() => {
      const params = new URLSearchParams();
      if (raw) params.set('q', raw);
      for (const key of ['type', 'plugin', 'category'] as const) {
        const values = [...facets[key]];
        if (values.length) params.set(key, values.join(','));
      }
      const search = params.toString();
      history.replaceState(null, '', search ? `?${search}` : location.pathname);
    }, 300);
    return () => clearTimeout(id);
  }, [raw, facets]);

  useEffect(() => setActive(0), [raw, facets]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const typing = target && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName);
      // Cmd+K belongs to the palette, which is mounted on every page.
      if (event.key === '/' && !typing) {
        event.preventDefault();
        input.current?.focus();
      }
    };
    addEventListener('keydown', onKey);
    return () => removeEventListener('keydown', onKey);
  }, []);

  function onFieldKey(event: KeyboardEvent) {
    if (!filtered.length) return;
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setActive((i) => Math.min(i + 1, filtered.length - 1));
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (event.key === 'Enter') {
      event.preventDefault();
      const chosen = filtered[active];
      if (chosen) location.href = base + String(chosen.url);
    } else if (event.key === 'Escape') {
      setRaw('');
    }
  }

  function toggle(key: keyof Facets, value: string) {
    setFacets((current) => {
      const next = new Set(current[key]);
      if (next.has(value)) next.delete(value);
      else next.add(value);
      return { ...current, [key]: next };
    });
  }

  return (
    <div class="search">
      <div class="search__box">
        <div class="search__field">
          <input
            ref={input}
            type="search"
            role="combobox"
            aria-expanded={searching}
            aria-controls="search-results"
            aria-autocomplete="list"
            placeholder="What do you need? e.g. a skill that reviews migrations"
            value={raw}
            disabled={failed}
            onInput={(event) => setRaw((event.target as HTMLInputElement).value)}
            onKeyDown={onFieldKey}
          />
          <span class="search__hint"><kbd>/</kbd></span>
        </div>
        <p class="search__keys">
          <span><kbd>↑</kbd><kbd>↓</kbd> move</span>
          <span><kbd>⏎</kbd> open</span>
          <span><kbd>⌘</kbd><kbd>K</kbd> jump anywhere</span>
          <span><kbd>esc</kbd> clear</span>
        </p>
        {failed && <p class="search__loading">Search index failed to load. The pages below still work.</p>}
        {!docs && !failed && <p class="search__loading">Loading index…</p>}
      </div>

      {searching && counts.type.length > 0 && (
        <div class="facets">
          {(['type', 'plugin', 'category'] as const).map((key) =>
            counts[key].length > 1 ? (
              <fieldset key={key}>
                <legend>{key}</legend>
                {counts[key].map(([value, n]) => (
                  <label class="facet" key={value} data-on={facets[key].has(value) ? 'true' : 'false'}>
                    <input
                      type="checkbox"
                      checked={facets[key].has(value)}
                      onChange={() => toggle(key, value)}
                    />
                    {value} <span class="n">{n}</span>
                  </label>
                ))}
              </fieldset>
            ) : null,
          )}
        </div>
      )}

      {searching && ready && (
        <p class="search__count" aria-live="polite">
          {filtered.length === 0
            ? `Nothing matches “${raw}”`
            : `${filtered.length} ${filtered.length === 1 ? 'match' : 'matches'}`}
        </p>
      )}

      {searching && filtered.length > 0 && (
        <ul class="results" id="search-results" role="listbox">
          {filtered.map((result, index) => {
            const matchedFields = new Set(Object.values(result.match ?? {}).flat());
            const onlyDeep =
              !matchedFields.has('description') &&
              !matchedFields.has('title') &&
              !matchedFields.has('keywords');
            const source = matchedFields.has('headings') ? 'headings' : 'body';
            const deep = onlyDeep
              ? excerpt(
                  source === 'headings'
                    ? ((result.headings as string[]) ?? []).join(' · ')
                    : String(result.body ?? ''),
                  result.terms,
                )
              : '';

            return (
              <li
                class="result"
                key={result.id}
                data-active={index === active ? 'true' : 'false'}
                role="option"
                aria-selected={index === active}
              >
                <div class="result__head">
                  <span class="chip chip--type">{result.type}</span>
                  {result.plugin && (
                    <a class="result__plugin" href={`${base}/p/${result.plugin}/`}>{result.plugin}</a>
                  )}
                  {result.tokens && (
                    <span class="tokens">
                      <span>always <b>≈{(result.tokens as { always: number }).always}</b></span>
                    </span>
                  )}
                </div>
                <p class="result__title">
                  <a href={base + String(result.url)}>
                    {mark(String(result.invocation || result.title), result.terms)}
                  </a>
                </p>
                <p class="result__trigger">{mark(String(result.description ?? ''), result.terms)}</p>
                {deep && (
                  <p class="result__where">
                    <b>{source}</b> — {mark(deep, result.terms)}
                  </p>
                )}
                {Array.isArray(result.keywords) && result.keywords.length > 0 && (
                  <p class="result__keywords">
                    {(result.keywords as string[]).map((k) => (
                      <span class="chip chip--quiet" key={k}>{k}</span>
                    ))}
                  </p>
                )}
              </li>
            );
          })}
        </ul>
      )}

      {searching && ready && filtered.length === 0 && (
        <div class="search__empty">
          <p>No artifact in this marketplace matches that.</p>
          {issueUrl && (
            <a
              class="button"
              href={`${issueUrl}?title=${encodeURIComponent(`Plugin request: ${raw}`)}&body=${encodeURIComponent(
                `Searched the catalogue for:\n\n> ${raw}\n\nNothing matched. Is this worth building?`,
              )}`}
            >Ask for it</a>
          )}
          <p class="search__loading">
            A search that finds nothing is the only demand signal a site without a backend can collect.
          </p>
        </div>
      )}
    </div>
  );
}
