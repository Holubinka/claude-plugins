A negative case. The question asks *which models*, which presumes the fan-out. The presumption is the
thing to answer.

The response passes only if **all** of the following hold.

1. **It says not to fan out**, and gives the reason as cost against benefit for a change this size —
   four context loads to produce one small answer.
2. **It does not simply assign four models.** Answering the question as asked, with a tier per agent,
   is the **fail**.
3. **It names where the savings actually are** — not duplicating work, rather than making agents
   cheaper. At least one of: partition the scope and name the other lanes, point them at a map first,
   ask for a compact structured return.
4. **It does not claim a cheaper tier reduces token count.** That is the specific confusion between
   the two knobs, and a response that makes it is a fail even if its final advice is right.

Recommending one reviewer, or an inline read with no dispatch at all, is a **pass**.
