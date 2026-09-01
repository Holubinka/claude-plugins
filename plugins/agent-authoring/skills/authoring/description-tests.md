# Four tests for a description

Reference for `authoring`. Run these before shipping a skill or an agent, in this order.

## 1 — The procedure test

**Read the description and ask: could someone act on this without opening the body?**

If yes, that is what will happen. A description listing steps, phases or an ordered workflow is a
summary the model will follow *instead of* the file — and nothing errors, so you find out only when a
run confidently skips the rule the skill exists for.

Fix by deleting the mechanism and keeping the occasion. If the removed steps were doing real work, it
is because the trigger was vague; sharpen the trigger rather than putting the steps back.

## 2 — The symptom test

**Would the sentence a frustrated person actually types match this?**

People do not describe the category of their problem. They paste an error, name a file, or say the
thing that is annoying them. A description written in the author's vocabulary — "manages", "handles",
"provides guidance on" — matches none of that.

List three real requests this should fire on, in the words someone would use. If none of them shares
vocabulary with the description, rewrite the description around them.

## 3 — The negative test

**Name a request that is close but must NOT fire this.** Then check the description does not match it.

This is the test that catches greed. It is easy to raise a trigger rate by widening a description
until it matches everything nearby — and the cost is paid on every turn, by every other skill that now
competes with it. A description that cannot be made to fail is not a trigger, it is a category label.

Where a near miss *does* match, the fix is usually a **When NOT to use** row in the body plus a
narrower clause in the description, not a longer one.

## 4 — The overlap test

**Compare it against its siblings.** Two descriptions that share most of their vocabulary will
compete, and which one wins is not something you control.

Some catalogues score this mechanically — cosine similarity over the description text, with a
threshold. Whether or not yours does, the manual form is the same question: if both descriptions were
in front of you and you knew nothing else, could you say which request goes to which?

If not, one of three things is true, and they have different fixes:

| What is actually wrong | Fix |
| :--- | :--- |
| They are the same skill with two names | Merge them |
| They are different, but the descriptions describe the same category | Rewrite both around what distinguishes them, not around what they have in common |
| One is a special case of the other | Say so explicitly in the narrower one's description, and give the broader one a **When NOT to use** row |

**Short descriptions score worse than long ones on this**, which is counterintuitive: a short
description shares a larger fraction of its total vocabulary with anything it overlaps. Lexically
specific and a little longer beats terse and generic.

## What none of these tests can tell you

Whether the body is any good. These four are about the line that decides whether the body is ever
read — a perfect description in front of a bad skill produces a reliably bad run, which is worse than
an unreliable one because it is repeatable.
