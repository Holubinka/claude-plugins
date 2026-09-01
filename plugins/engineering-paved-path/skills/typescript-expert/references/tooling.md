# Type testing and debugging tools

Reference for `typescript-expert`. How to assert on types, and the CLI tools for a slow or
confusing compile.

## Type testing

**Vitest Type Testing (Recommended)**
```typescript
// in avatar.test-d.ts
import { expectTypeOf } from 'vitest'
import type { Avatar } from './avatar'

test('Avatar props are correctly typed', () => {
  expectTypeOf<Avatar>().toHaveProperty('size')
  expectTypeOf<Avatar['size']>().toEqualTypeOf<'sm' | 'md' | 'lg'>()
})
```

**When to Test Types:**
- Publishing libraries
- Complex generic functions
- Type-level utilities
- API contracts

## Debugging Mastery

### CLI Debugging Tools
```bash
# Debug TypeScript files directly (if tools installed)
command -v tsx >/dev/null 2>&1 && npx tsx --inspect <path/to/file.ts>
command -v ts-node >/dev/null 2>&1 && npx ts-node --inspect-brk <path/to/file.ts>

# Trace module resolution issues
<runner> tsc --traceResolution > resolution.log 2>&1
grep "Module resolution" resolution.log

# Debug type checking performance (use --incremental false for clean trace)
<runner> tsc --generateTrace trace --incremental false
# Analyze trace (if installed)
command -v @typescript/analyze-trace >/dev/null 2>&1 && npx @typescript/analyze-trace trace

# Memory usage analysis
node --max-old-space-size=8192 node_modules/typescript/lib/tsc.js
```

### Custom Error Classes
```typescript
// Proper error class with stack preservation
class DomainError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number
  ) {
    super(message);
    this.name = 'DomainError';
    Error.captureStackTrace(this, this.constructor);
  }
}
```


