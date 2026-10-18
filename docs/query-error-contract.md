# Graph Query Error Contract

Stable application error codes:

- `ENTITY_NOT_FOUND`
- `AMBIGUOUS_ENTITY`
- `TENANT_MISMATCH`
- `INVALID_INPUT`
- `QUERY_TIMEOUT`
- `DATABASE_UNAVAILABLE`

Errors include a human-readable message and a retryable flag. Connection and timeout driver exceptions are converted at the executor boundary; domain errors are emitted by repositories.
