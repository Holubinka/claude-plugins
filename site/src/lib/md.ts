import { Marked } from 'marked';

function escapeHtml(value: string): string {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const marked = new Marked({ gfm: true, breaks: false });

/** Plugin READMEs and skill bodies arrive through pull requests, so raw HTML in them
 *  would become raw HTML on this site. Neutralising the html tokens — rather than
 *  escaping the source before parsing — leaves code spans and fences intact, so a
 *  documented `<name>` placeholder still reads as `<name>`. */
marked.use({
  renderer: {
    html(token: unknown) {
      const text = typeof token === 'string' ? token : String((token as { text: string }).text ?? '');
      return escapeHtml(text);
    },
  },
});

export function renderMarkdown(source: string | null | undefined): string {
  if (!source) return '';
  return marked.parse(source) as string;
}
