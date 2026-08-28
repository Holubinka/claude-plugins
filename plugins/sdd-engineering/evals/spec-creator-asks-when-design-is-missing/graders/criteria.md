The response passes only if **all** of the following hold.

1. **It stops and asks rather than writing a spec.** The output is a clarification block, not
   a specification. No file is written under any `specs/` directory.
2. **It names the missing artefact.** The response says explicitly that the design was referred
   to but not provided, and asks for a path or the pasted contents. Referring vaguely to
   "more information" is not enough.
3. **It does not record the absence and continue.** A response that writes a spec containing a
   note such as "no design was provided" is a **failure**, even if everything else is correct.
   This is the specific behaviour the case exists to test.
4. **It offers a default assumption.** The clarification ends with what it would assume if told
   to go ahead, so the reply can be one word.

Fail the response if it invents layout details, produces acceptance criteria describing a visual
arrangement, or asks a question whose answer it could have found by reading the repository.
