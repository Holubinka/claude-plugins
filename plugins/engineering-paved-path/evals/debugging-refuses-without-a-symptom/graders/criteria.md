A negative case, added after a routing probe caught `systematic-debugging` firing here. There is no
observed symptom, so there is no cause to find.

The response passes only if **all** of the following hold.

1. **It reviews the function**, rather than declining to help. The user's request is answerable.
2. **It does not run a root-cause investigation.** No reproduction hunt, no bisect, no four-phase
   debugging procedure — there is nothing to reproduce.
3. **If it names the distinction**, it names it correctly: debugging starts from a symptom you can
   point at; judging whether code looks right without one is review.
4. **Any defect it finds is stated with the input that exercises it** — a boundary value, an empty
   window — rather than as an impression.
5. **It does not manufacture a symptom** to justify a procedure.

Saying the bounds are correct, and showing which inputs it checked, is a **pass**. So is finding a
real off-by-one. What fails is treating a suspicion as a defect under investigation.
