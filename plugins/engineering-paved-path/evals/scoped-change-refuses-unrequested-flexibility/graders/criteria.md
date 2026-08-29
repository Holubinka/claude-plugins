Introduced in 1.3.0. The request explicitly asks for flexibility, which makes building the
abstraction the obedient-looking answer and the wrong one — no second strategy exists, and an
interface with one implementation is a layer every reader traverses to reach the code that works.

The response passes only if **all** of the following hold.

1. **It asks what the second case is**, or says plainly that a named second strategy would justify
   the abstraction and an unnamed one would not. Building a pluggable strategy interface without
   asking is the **fail**.
2. **What it proposes to build is the token bucket**, directly, with the swap treated as a change to
   make when a second strategy actually arrives.
3. **It does not add configuration nobody specified** — no strategy registry, no factory, no options
   object covering values that were never named.
4. **It does not refuse the request.** A rate limiter is wanted and the answer must deliver one.
5. **The reasoning is about cost to the reader**, not about effort: an option is a permanent branch
   and a promise to support every value of it.

Proposing the limit itself as a parameter — the actual number of requests — is a **pass**: that is a
value the request implies, not an architecture. Proposing an interface so the *algorithm* can be
swapped is not.
