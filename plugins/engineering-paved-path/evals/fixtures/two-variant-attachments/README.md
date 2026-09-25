# two-variant-attachments

A fixture. `AttachmentList.vue` renders its attachments in two branches — `compact` for the
composer, the full list for a sent message — and each branch sets its own vertical gap. The
spacing is also inflated by a `line-height` inherited from the form-item wrapper, which no rule on
the attachment itself mentions.

Both facts are load-bearing. The two branches are what make "done" after editing one of them a
false claim; the inherited `line-height` is what makes every cause read off the component's own
CSS wrong.
