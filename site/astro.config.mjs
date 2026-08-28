// @ts-check
import { defineConfig } from 'astro/config';
import preact from '@astrojs/preact';

// Until the custom domain lands the site is served from a subpath, so every internal
// link has to carry the base. Both are overridable from CI: set SITE_ORIGIN to the
// domain and SITE_BASE to '/' on the day the CNAME is added — nothing else changes.
const SITE_ORIGIN = process.env.SITE_ORIGIN ?? 'https://holubinka.github.io';
const SITE_BASE = process.env.SITE_BASE ?? '/claude-plugins/';

export default defineConfig({
  site: SITE_ORIGIN,
  base: SITE_BASE,
  // catalog.json addresses every artifact with a trailing slash.
  trailingSlash: 'always',
  build: { format: 'directory' },
  integrations: [preact({ compat: false })],
  devToolbar: { enabled: false },
});
