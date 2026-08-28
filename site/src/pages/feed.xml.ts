import type { APIRoute } from 'astro';
import { timeline, marketplace } from '../lib/catalog';

const escape = (value: string) =>
  value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export const GET: APIRoute = ({ site }) => {
  const origin = (site ?? new URL('https://example.invalid')).origin;
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const home = `${origin}${base}/`;
  const entries = timeline().slice(0, 50);
  const updated = entries[0]?.release.date ?? new Date(0).toISOString();
  const name = marketplace.name ?? 'catalogue';

  const body = `<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>${escape(name)} releases</title>
  <subtitle>${escape(marketplace.description ?? '')}</subtitle>
  <link href="${home}" />
  <link rel="self" href="${origin}${base}/feed.xml" />
  <id>${home}</id>
  <updated>${updated}</updated>
${entries
  .map(({ plugin, release }) => {
    const url = `${origin}${base}/p/${plugin}/`;
    const summary = release.changes.length ? release.changes.join('\n') : `${plugin} ${release.version}`;
    return `  <entry>
    <title>${escape(plugin)} ${escape(release.version)}</title>
    <link href="${url}" />
    <id>${origin}${base}/releases/${escape(release.tag)}</id>
    <updated>${release.date}</updated>
    <summary>${escape(summary)}</summary>
  </entry>`;
  })
  .join('\n')}
</feed>
`;

  return new Response(body, { headers: { 'Content-Type': 'application/atom+xml; charset=utf-8' } });
};
