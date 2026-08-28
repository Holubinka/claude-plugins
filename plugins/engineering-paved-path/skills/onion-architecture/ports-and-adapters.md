# Ports and adapters — the outside, inverted

A port is the shape the inside needs. An adapter is the technology that satisfies it. The point is that the application can be "developed and tested in isolation from its eventual run-time devices and databases" — not that you will ever swap your database.

Code samples below are illustrations of shape. Map the file names onto the repository's own conventions first ([SKILL.md](SKILL.md) §0).

---

## 1. Does this need a port?

| The dependency… | Port? |
|---|---|
| makes a network call | **Yes** |
| touches the filesystem or spawns a process | **Yes** |
| reads a secret | **Yes** — and it is the secrets port, which usually already exists |
| is non-deterministic (clock, randomness) | **Yes**, but as a parameter — see §6 |
| is the primary database, reached through the ORM | **No** — the repository *is* the port |
| is a pure library | **No** — unless you need a second implementation |

The test is **two implementations, not purity.** A pure tokenizer library still earns a port when there is an approximate fallback path, because the fallback is the second implementation.

## 2. Where the interface goes

**Answer this first: is the consumer a service or an executor?** If yes, the port belongs in the shared contracts file and the other two rows do not apply. The reason is that boundary gates usually close the alternatives from both sides:

- a port in a module's own `types.ts` → the adapter must import the module → *no adapter may import a feature module*.
- a port declared beside the adapter → the service must import the adapter → *no service may import an adapter implementation*.

A shared contracts file is the only place both an executor and an adapter may name.

| Used by | Interface lives in |
|---|---|
| a service or executor — **or** 2+ modules, or shared with another package | the shared contracts file |
| one module, consumed *below* the service layer | that module's `types.ts` |
| only its own adapter's callers, none of them a service | beside the adapter |

The third row is narrow and easy to get wrong. A port sits beside its adapter only when every consumer is itself below the service layer — a pipeline step, another adapter. One service importing it moves it to row one.

**Verify direction by probe, not by reading.** Boundary rules frequently count `import type` as a real edge (dependency-cruiser does when `tsPreCompilationDeps` is on and the rule sets no `dependencyTypesNot`). A type-only import in each direction is a two-minute check that settles where a port may live; reasoning about it is slower and less reliable.

**If contracts are vendored into more than one package, they have a canonical copy.** Change it first, then mirror, and keep whatever gate does the `diff`. Type-checking cannot see this drift, because each package compiles against its own copy.

## 3. The three obligations of a new port

A port is not finished until all three are done.

**1 — The interface, in terms of the domain.** Ask for what you need, not for how it is fetched: `readFile(repo, path)`, not `exec(cmd)`. Nothing driver-shaped may appear in the signature — no query builders, no `Response`, no SDK error types.

**2 — A mock implementation, beside the real ones.** Tests reach mocks through the application factory's override parameter — never real network, never real keys. A port without a mock is a port that every test has to work around, which is how `vi.mock` of a deep module path gets into a test suite.

**3 — A slot on the container.** A getter for a synchronous dependency, an async method when a secret must be resolved first, and an override that always wins:

```ts
get git(): GitClient {
  if (this.overrides.git) return this.overrides.git;
  this._git ??= new SimpleGitClient(this.config.cloneDir);
  return this._git;
}
```

Overrides-first is what makes `buildApp({ overrides: { git: new MockGitClient() } })` work. An override checked *after* the cached instance is built silently does nothing in the second test of a file.

## 4. Secrets

Only through the secrets port. Never through the config object, never `process.env` at the point of use. Widening the environment schema to carry an API key is the most-repeated version of this mistake, because it looks like configuration and behaves like a credential.

Resolution happens in the container, at construction time, and fails loudly:

```ts
const key = await this.secrets.get('PROVIDER_API_KEY');
if (!key) throw new ConfigError('PROVIDER_API_KEY is not configured');
return new ProviderClient(key, {
  estimateCost: (model, tokensIn, tokensOut) =>
    this.priceBook.estimate(model, tokensIn, tokensOut),
});
```

Two things to copy from those lines: the secret never reaches the adapter's caller, and `estimateCost` is **injected as a callback**, so the client holds no pricing table. That is the pattern for anything the core needs but must not own.

Make `set` optional on the secrets port on purpose — a read-only backend may omit it, and callers branch on its presence. After writing a key, invalidate the caches: providers are usually cached by construction, so the new value otherwise applies on the next process start rather than the next request.

## 5. Degraded contracts

An optional enrichment must never take the request down. Set one rule for the whole codebase and keep it:

- Object-returning methods carry an inline `degraded?: boolean` (plus an optional `reason`).
- Array-returning methods return `[]` when degraded — empty already means "no enrichment" to every consumer.

No `{ degraded, data }` wrappers; call sites stay natural. Taken to its conclusion, this means one try/catch around a whole optional analysis, returning `[]` on any failure — so a malformed config in a user-supplied repository degrades the ranking instead of failing the whole index.

**Decide per port whether failure is degradation or an error.** A missing API key is a configuration error. A dependency graph that would not build is `[]`. Getting this backwards in either direction is expensive: a degraded credential failure produces an empty result nobody can explain, and a hard-failing enrichment takes down a request that did not need it.

## 6. Clock, randomness, logging

No global ports for these. The established patterns, in order of preference:

1. **Take it as a parameter** — `deriveStatus(…, now: number)`. Cleanest: the function stays pure and testable with no injection machinery.
2. **A constructor default** — `constructor(private now: () => number = () => Date.now())`.
3. **A structural type, not an interface import.** Declare the four-method `Logger` shape you actually use and let the route pass the framework's logger. The consumer then names neither the web framework nor the logging library, so it stays callable from a job.

Calling `Date.now()` directly is acceptable where the value is not asserted on. If a test needs to control time, use pattern 1 rather than mocking globals.

## 7. Adapters point outward only

An adapter implements a port and knows nothing about features. The two ways this breaks:

- **An adapter imports a constant from a feature module.** When that happens, the constant is in the wrong place. Move it beside the adapter, or onto the port.
- **An adapter mutates global process state** — writing `process.env` from a constructor path so that subprocesses inherit a setting. Sometimes it is the only way, but it is a real cost: it affects every other user of that process. Do it once, deliberately, with the reason recorded beside it, and do not copy the move.
