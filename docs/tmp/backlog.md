# Catalogue backlog

What the screen designs specified and the site does not do yet. Everything here is
blocked on the catalogue actually containing plugins — building it against an empty
catalogue ships controls that filter nothing.

Three of the eight designed items are already built: the keyboard hints under the search
field, the `⌘K` palette, and the recently-viewed list the palette offers back.

| Item | Blocked on | Why it matters |
| :--- | :--- | :--- |
| Facets by keyword | Plugins, for their `keywords` | Docs carry no keywords, so today the row would be empty |
| Sort by context cost | Plugins, for `tokens` | Docs have `tokens: null`; there is nothing to order |
| Budget filter (`≤20`, `≤50` always-on) | Plugins, for `tokens` | The scarce resource in this marketplace is the context window |
| Filter to plugins with no findings | Plugins, for `health` | Health is a plugin-level record; there are no plugins |
| Copy the install command from a result card | One plugin | Saves the trip to the plugin page |

Each was drawn and discarded with the design canvas; the canvas itself was deleted
because it was a second, hand-maintained copy of a site that already exists and would
drift from it on the first change to `tokens.css`.
