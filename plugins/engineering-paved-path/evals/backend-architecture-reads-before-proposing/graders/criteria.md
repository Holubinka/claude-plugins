Introduced in 1.4.0. The repository has a consistent layers-first tree. The skill's own preferred
shape is components-first — which makes recommending it here the tempting answer and the wrong one.

The response passes only if **all** of the following hold.

1. **The existing convention is followed.** The payment controller goes with the controllers, the
   service with the services, the repository with the repositories.
2. **It does not propose restructuring the repository** to a components-first tree as part of adding
   a module. Saying that a different shape scales better, clearly separated as an observation rather
   than as this task, is fine; doing it is a **fail**.
3. **It reads before proposing** — it establishes the top-level shape and looks at the module most
   like the one being added, rather than answering from the rule alone.
4. **It looks for a seam to reuse** — an existing base class, error type, repository interface or
   validation helper — rather than introducing a parallel one.
5. **Nothing framework-shaped is put in the service.** If it mentions the boundary at all, it is that
   request and response objects stay at the entry point.

A response that names the components-first shape as worth considering *separately*, with the
migration called a migration, is the strongest answer and a **pass**.
