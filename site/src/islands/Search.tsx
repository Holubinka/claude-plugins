import { useEffect, useMemo, useRef, useState } from 'preact/hooks';
import type { SearchResult } from 'minisearch';
import { createEngine, runSearch } from '../lib/search-core.js';
import '../styles/search.css';
import { search as s } from '../lib/strings';

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

const FACET_KEYS = ['type', 'plugin', 'category'] as const;

/** `type` has four values and answers the question people actually arrive with —
 *  "show me the skills", so it is a segmented control that is always on screen and
 *  the other two live behind a disclosure. */
const MORE_KEYS = ['plugin', 'category'] as const;

/** Keyword is deliberately not a facet. 102 values across 100 artifacts is a search
 *  vocabulary rather than a set of choices: any row short enough to read hides most of
 *  it, and the hidden tail cannot be reached by clicking. It stays a boosted search
 *  field, which is the control that actually fits the data — type the word.
 *
 *  This caps the rows that remain, for a marketplace that outgrows them. */
const FACET_LIMIT = 12;

function readUrl(): { q: string; facets: Facets } {
  const params = new URLSearchParams(location.search);
  const split = (key: string) => new Set((params.get(key) ?? '').split(',').filter(Boolean));
  return {
    q: params.get('q') ?? '',
    facets: {
      type: split('type'), plugin: split('plugin'),
      category: split('category'),
    },
  };
}

const legend: Record<(typeof FACET_KEYS)[number], string> = {
  type: s.facetType, plugin: s.facetPlugin, category: s.facetCategory,
};

export default function Search({ docsUrl, base, issueUrl }: Props) {
  const [docs, setDocs] = useState<Doc[] | null>(null);
  const [failed, setFailed] = useState(false);
  const [raw, setRaw] = useState('');
  const [facets, setFacets] = useState<Facets>({
    type: new Set(), plugin: new Set(), category: new Set(),
  });
  const [active, setActive] = useState(0);
  const [showMore, setShowMore] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const initial = readUrl();
    setRaw(initial.q);
    setFacets(initial.facets);
    if (MORE_KEYS.some((key) => initial.facets[key].size > 0)) setShowMore(true);
    started.current = true;

    fetch(docsUrl)
      .then((response) => (response.ok ? response.json() : Promise.reject(new Error(String(response.status)))))
      .then((data: Doc[]) => setDocs(data))
      .catch(() => setFailed(true));
  }, [docsUrl]);

  const engine = useMemo(() => (docs ? createEngine(docs) : null), [docs]);

  const searching = raw.trim().length >= 2;

  // With no query there is nothing to rank, so the whole corpus is the pool and the
  // facets tally over it. That is what lets someone narrow the catalogue by hand
  // instead of having to guess a word first.
  const results = useMemo(() => {
    if (!engine || !docs) return [] as SearchResult[];
    if (searching) return runSearch(engine, raw) as SearchResult[];
    return docs.map((doc) => ({ ...doc, terms: [], match: {}, score: 0 })) as unknown as SearchResult[];
  }, [engine, docs, raw, searching]);

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
    // Every facet is tallied over the results already narrowed by the OTHER facets, so a
    // number says what that option would actually return if it were clicked next.
    // Tallying the whole pool instead offered `documentation 59` beside a single hook,
    // and eleven of the twelve options on screen led to "nothing matches those filters".
    //
    // A facet never narrows its own tally: within one facet the values are alternatives
    // (skill OR agent), so counting `agent` against a chosen `skill` would zero out every
    // sibling and put multi-select out of reach.
    const passes = (r: SearchResult, except: (typeof FACET_KEYS)[number]) =>
      FACET_KEYS.every(
        (key) => key === except || facets[key].size === 0 || facets[key].has(String(r[key])),
      );

    const tally = (key: (typeof FACET_KEYS)[number]) => {
      const out = new Map<string, number>();
      for (const r of results) {
        if (!passes(r, key)) continue;
        const value = r[key] as string | null;
        if (value) out.set(value, (out.get(value) ?? 0) + 1);
      }
      // A chosen value stays on screen at zero — it is the only way to switch it off.
      for (const value of facets[key]) if (!out.has(value)) out.set(value, 0);
      return [...out].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    };
    return { type: tally('type'), plugin: tally('plugin'), category: tally('category') };
  }, [results, facets]);

  const ready = docs !== null;
  const chosen = FACET_KEYS.some((key) => facets[key].size > 0);
  const activeTotal = FACET_KEYS.reduce((n, key) => n + facets[key].size, 0);
  // An option that would return nothing is not a choice — it goes. Unless it is the one
  // currently on, which stays at zero because hiding it would strand the filter.
  const visible = (key: (typeof FACET_KEYS)[number]) =>
    counts[key].filter(([value, n]) => n > 0 || facets[key].has(value));
  // What clearing `type` would leave, rather than the size of the whole catalogue.
  const allCount = counts.type.reduce((n, [, c]) => n + c, 0);
  // Which rows still offer a choice. Narrow enough and none of them do — one hook has
  // one plugin and one category — and then the disclosure would open on nothing, so the
  // button that opens it goes too.
  const moreRows = MORE_KEYS.filter((key) => visible(key).length > 1 || facets[key].size > 0);
  const hiddenActive = MORE_KEYS.reduce((n, key) => n + facets[key].size, 0);
  // Either a query or a facet puts the island in charge of what is on screen.
  const filtering = searching || chosen;

  // The prerendered browse listing stays the content until a query is active.
  useEffect(() => {
    document.getElementById('browse')?.toggleAttribute('hidden', filtering);
  }, [filtering]);

  // Shareable searches, without flooding history.
  useEffect(() => {
    if (!started.current) return;
    const id = setTimeout(() => {
      const params = new URLSearchParams();
      if (raw) params.set('q', raw);
      for (const key of FACET_KEYS) {
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

  function clearAll() {
    setFacets({ type: new Set(), plugin: new Set(), category: new Set() });
  }

  return (
    <div class="search">
      <div class="search__box">
        <div class="search__field">
          <input
            ref={input}
            type="search"
            role="combobox"
            aria-expanded={filtering}
            aria-controls="search-results"
            aria-autocomplete="list"
            placeholder={s.placeholder}
            value={raw}
            disabled={failed}
            onInput={(event) => setRaw((event.target as HTMLInputElement).value)}
            onKeyDown={onFieldKey}
          />
          <span class="search__hint"><kbd>/</kbd></span>
        </div>
        <p class="search__keys">
          <span><kbd>↑</kbd><kbd>↓</kbd> {s.keyMove}</span>
          <span><kbd>⏎</kbd> {s.keyOpen}</span>
          <span><kbd>⌘</kbd><kbd>K</kbd> {s.keyJump}</span>
          <span><kbd>esc</kbd> {s.keyClear}</span>
        </p>
        {failed && <p class="search__loading">{s.failed}</p>}
        {!docs && !failed && <p class="search__loading">{s.loading}</p>}
      </div>

      {ready && counts.type.length > 0 && (
        <div class="filters">
          <div class="filters__bar">
            <div class="filters__seg" role="group" aria-label={s.facetAllLabel}>
              {/* Not a checkbox: "all" is the absence of a type filter, so it clears
                  rather than toggles, and it stays lit while nothing is chosen. */}
              <button
                type="button"
                class="filters__opt"
                data-on={facets.type.size === 0 ? 'true' : 'false'}
                aria-pressed={facets.type.size === 0}
                onClick={() => setFacets((current) => ({ ...current, type: new Set() }))}
              >
                {s.facetAll} <span class="n">{allCount}</span>
              </button>
              {visible('type').map(([value, n]) => (
                <label class="filters__opt" key={value} data-on={facets.type.has(value) ? 'true' : 'false'}>
                  {/* The checkbox stays in the DOM and keeps the keyboard and screen
                      reader behaviour; only its own rendering is dropped. */}
                  <input
                    class="vh"
                    type="checkbox"
                    checked={facets.type.has(value)}
                    onChange={() => toggle('type', value)}
                  />
                  {value} <span class="n">{n}</span>
                </label>
              ))}
            </div>

            <div class="filters__tools">
              {chosen && <span class="filters__active">{s.activeCount(activeTotal)}</span>}
              {chosen && (
                <button type="button" class="filters__clear" onClick={clearAll}>
                  {s.clearAll}<span aria-hidden="true"> ×</span>
                </button>
              )}
              {moreRows.length > 0 && (
              <button
                type="button"
                class="filters__more"
                aria-expanded={showMore}
                aria-controls="more-filters"
                onClick={() => setShowMore((open) => !open)}
              >
                <span class="filters__chevron" data-open={showMore ? 'true' : 'false'} aria-hidden="true">›</span>
                {showMore ? s.moreClose : s.moreOpen}
                {/* Collapsed filters still filter. Without this the panel can hide the
                    reason the result count is small. */}
                {hiddenActive > 0 && <span class="filters__badge">{hiddenActive}</span>}
              </button>
              )}
            </div>
          </div>

          {showMore && moreRows.length > 0 && (
            <div class="filters__panel" id="more-filters">
              {moreRows.map((key) => {
                const live = visible(key);
                const shown = live.slice(0, FACET_LIMIT);
                const hidden = live.length - shown.length;
                return (
                  <div class="filters__row" key={key}>
                    <span class="filters__label">{legend[key]}</span>
                    <div class="filters__values">
                      {shown.map(([value, n]) => (
                        <label class="filters__tag" key={value} data-on={facets[key].has(value) ? 'true' : 'false'}>
                          <input
                            class="vh"
                            type="checkbox"
                            checked={facets[key].has(value)}
                            onChange={() => toggle(key, value)}
                          />
                          {value} <span class="n">{n}</span>
                        </label>
                      ))}
                      {hidden > 0 && <span class="filters__tail">{s.facetMore(hidden)}</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {ready && (
        <p class="search__count" aria-live="polite">
          {filtered.length === 0
            ? (searching ? s.noMatch(raw) : s.noMatchFiltered)
            : filtering
              ? s.matchCount(filtered.length)
              : s.browsing(filtered.length)}
        </p>
      )}

      {filtering && filtered.length > 0 && (
        <ul class="results" id="search-results" role="listbox">
          {filtered.map((result, index) => {
            const matchedFields = new Set(Object.values(result.match ?? {}).flat());
            const onlyDeep =
              searching &&
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
                      <span>{s.always} <b>≈{(result.tokens as { always: number }).always}</b></span>
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

      {filtering && ready && filtered.length === 0 && (
        <div class="search__empty">
          <p>{s.emptyTitle}</p>
          {issueUrl && (
            <a
              class="button"
              href={`${issueUrl}?title=${encodeURIComponent(s.issueTitle(raw))}&body=${encodeURIComponent(
                s.issueBody(raw),
              )}`}
            >{s.askForIt}</a>
          )}
          <p class="search__loading">{s.emptyAside}</p>
        </div>
      )}
    </div>
  );
}
