# Executing External Write Actions Safely

Use this for a concrete task to write in the target system. This reference grants no authority and does not replace a service-specific permission check. Content already clearly requested needs no renewed approval. If target, content or scope is missing, clarify them before writing.

## Preparing

Determine the target account, service, object and requested change unambiguously. Use stable object identifiers. Read the existing state and possible duplicates. A preparation or summary is not a request to create a task or send a message.

In the private profile folder under `state/actions/`, keep a minimal local execution trace. Required are an action identifier, service, target, time, status and known object identifiers. A short action type such as "reschedule appointment" is enough. Do not store full messages, transcripts or credentials. Needed original content stays in the authorized source system or in a separately requested output artifact.

## Executing and Verifying

1. Record status "started" before the external call.
2. Send only the specifically requested change.
3. Verify the result against the target account and object identifier, comparing relevant fields with the task. Report as "confirmed" only after this proof.
4. On timeout, cancellation or an ambiguous result, keep status "unclear". First check in the target system whether the action was executed. A timeout alone does not prove non-execution.
5. Plan a retry only when non-execution is proven and the task still stands. If the state remains unclear, stop the affected step and ask. Report other successful actions specifically and do not roll them back automatically.

A local action identifier does not guarantee idempotency in the external service. If the target system supports its own idempotency key, the adapter must verify its actual behavior. Proof of an already executed task prevents its duplicate execution. A new, independent task gets a new identifier.

## Limits

- Calendar: before a change, recheck availability and the current object state. Do not change a recurring series instead of the requested single appointment.
- Planhat: transfer confirmed entries via MCP as drafts, check for duplicates and verify. Final submission stays manual.
- Missing required access: ask first. The mere existence of an API key does not prove rights or approval.
- The journal is not a task list, not a memory import and not a complete communication archive. Technical installation logs stay separate from it.

The executable journal process and the service-specific adapters still need to be built and checked with synthetic error cases.
