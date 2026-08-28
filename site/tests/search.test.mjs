/** Probe queries against the real index, using the same ranking the browser runs.
 *  Run: node tests/search.test.mjs   (after npm run index) */

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { createEngine, runSearch } from '../src/lib/search-core.js';

const here = dirname(fileURLToPath(import.meta.url));
const docs = JSON.parse(readFileSync(join(here, '../public/data/search-docs.json'), 'utf8'));
const { probes } = JSON.parse(readFileSync(join(here, 'queries.json'), 'utf8'));

const engine = createEngine(docs);
let failed = 0;

console.log(`Indexed ${docs.length} documents.\n`);

for (const probe of probes) {
  const results = runSearch(engine, probe.query);
  const at = results.findIndex((result) => result.id === probe.expect);
  const ok = at !== -1 && at < probe.within;
  if (!ok) failed += 1;
  console.log(`${ok ? 'ok  ' : 'FAIL'} "${probe.query}"`);
  console.log(`     want ${probe.expect} within ${probe.within}`);
  console.log(
    `     got  ${at === -1 ? 'not returned at all' : `position ${at + 1}`}` +
      ` · top: ${results.slice(0, 3).map((r) => r.id).join(', ') || '—'}`,
  );
}

console.log(`\n${probes.length - failed}/${probes.length} probes passed.`);
process.exit(failed ? 1 : 0);
