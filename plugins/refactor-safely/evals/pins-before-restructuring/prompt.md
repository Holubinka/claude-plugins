Use the `refactor-safely:refactor-implementer` agent on this plan:

```
## Behaviour to pin
| 1 | subtotal() returns 0 for an empty line list | nothing | yes | subtotal([]) === 0 |
| 2 | largestLine() returns undefined when nothing exceeds the threshold | nothing | yes | largestLine([], 10) |

## Frozen surface
subtotal, largestLine

## Allowed changes
Extract the repeated price×qty expression into a helper (apply after reading the callers).
```
