/** Ranking, in one place so the browser and the probe-query tests cannot drift.
 *
 *  Skill descriptions are written as trigger conditions (docs/tmp/site.md), so the
 *  user's question and the field we rank against are the same genre of sentence. That
 *  alignment — not the algorithm — is what makes lexical search enough here. */

import MiniSearch from 'minisearch';

export const FIELDS = ['title', 'description', 'keywords', 'headings', 'body'];
export const BOOST = { title: 6, keywords: 4, description: 4, headings: 2, body: 1 };

export const STORED = [
  'id', 'type', 'plugin', 'name', 'title', 'description', 'keywords',
  'tokens', 'url', 'invocation', 'category', 'body', 'headings',
];

/** Lead-ins people type that carry no meaning for ranking. */
export const BOILERPLATE = [
  'i need a', 'i need', 'i want a', 'i want', 'is there a', 'is there',
  'do you have a', 'do you have', 'something to', 'something that',
  'help me', 'how do i', 'how to', 'a skill for', 'a skill that',
  'a plugin for', 'a plugin that', 'an agent for', 'an agent that',
  'looking for a', 'looking for', 'show me',
];

/** Stripped from queries only. The index keeps them, so a phrase search still works;
 *  a query has too few words to spend any of them on "how" or "the". */
export const STOPWORDS = new Set(
  ('a an and are as at be by can do does for from has have i if in into is it its me my of on or '
   + 'please need needs want something anything explain explains explaining '
   + 'that the this to use used uses user was what when where which who will with without you your')
    .split(' '),
);

export const TYPE_WORDS = {
  skill: 'skill', skills: 'skill',
  agent: 'agent', agents: 'agent',
  command: 'command', commands: 'command',
  hook: 'hook', hooks: 'hook',
  mcp: 'mcp', server: 'mcp', servers: 'mcp',
  doc: 'doc', docs: 'doc', documentation: 'doc',
};

/** @param {string} input */
export function normalise(input) {
  let text = input
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  for (const phrase of BOILERPLATE) {
    if (text.startsWith(phrase + ' ')) {
      text = text.slice(phrase.length + 1);
      break;
    }
  }

  // A type word steers ranking, it never filters: the user is guessing at our taxonomy.
  let type = null;
  const words = text.split(' ').filter(Boolean);
  const kept = words.filter((word) => {
    const hit = TYPE_WORDS[word];
    if (hit && !type) { type = hit; return false; }
    return !STOPWORDS.has(word);
  });

  return { query: (kept.length ? kept : words).join(' '), type };
}

export function createEngine(docs) {
  const mini = new MiniSearch({
    fields: FIELDS,
    storeFields: STORED,
    extractField: (doc, field) => {
      const value = doc[field];
      return Array.isArray(value) ? value.join(' ') : (value ?? '');
    },
  });
  mini.addAll(docs);
  return mini;
}

/** @param {MiniSearch} engine @param {string} raw */
export function runSearch(engine, raw) {
  const { query, type } = normalise(raw);
  if (query.trim().length < 2) return [];

  // People type "roll back" for a section called "Rollback". Searching the joined form
  // of each adjacent pair as well costs nothing when it matches nothing, and rescues the
  // compound when it matches a title.
  const words = query.split(' ').filter(Boolean);
  const joined = [];
  for (let i = 0; i < words.length - 1; i += 1) {
    const pair = words[i] + words[i + 1];
    if (pair.length <= 24) joined.push(pair);
  }
  const expanded = words.concat(joined).join(' ');

  const options = {
    boost: BOOST,
    prefix: true,
    fuzzy: (term) => (term.length > 4 ? 0.2 : 0),
    boostDocument: (_id, _term, stored) => {
      let weight = 1;
      if (type && stored?.type === type) weight *= 1.5;
      const name = String(stored?.name ?? '').toLowerCase();
      if (name && name === query.trim()) weight *= 4;
      return weight;
    },
  };

  // AND is for a query that *names* something — one or two words, where every word is
  // meant. A longer query is a question, and conjunction over a question is a coincidence
  // filter: a 30 KB agent body contains all four words by chance while the two-paragraph
  // section that actually answers it does not, so the right answer is not merely ranked
  // low, it is absent from the result set. Measured when the catalogue went from docs-only
  // to docs plus fifteen components: two probes that had passed for a year began returning
  // "not returned at all", and only because AND had started succeeding.
  if (words.length <= 2) {
    const strict = engine.search(query, { ...options, combineWith: 'AND' });
    if (strict.length > 0) return strict;
  }

  // Plain OR lets a document that caught one common word outrank one that caught most of
  // the question, which is what the floor below is for.
  const loose = engine.search(expanded, { ...options, combineWith: 'OR' });
  // Two matched terms is the line between "this is about what you asked" and "this
  // document happens to contain one common word". Demanding a proportion of a padded
  // question instead throws out the right answer.
  const asked = words.length;
  const floor = Math.min(2, asked);
  const enough = loose.filter((result) => result.terms.length >= floor);
  return enough.length > 0 ? enough : loose;
}
