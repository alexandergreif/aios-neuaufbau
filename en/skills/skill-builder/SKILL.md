---
name: skill-builder
description: Creates or improves an AIOS skill when given a concrete task, checks for overlaps and has content, format and behavior independently reviewed.
---

# Build and Improve Skills

Follow the [core rules](../../rules/core.md) and [storage](../../references/storage.md). Clarify only essential gaps regarding purpose, trigger, desired outcome, needed context, authority and verifiable completion. If a needed source or technical capability is missing, ask first and wait for the decision.

Before building a new skill, check the existing capabilities for overlaps. Recommend an extension or a merge when that covers the same purpose more clearly. Separate shared working rules, task-specific instructions and references loaded only when needed. Do not copy general rules, personal details, customer data, credentials or fixed user paths into the skill.

Edit the canonical sources in the confirmed source folder. Installed copies and generated mirrors are not an editing source. Changes to existing general rules still need the matching task. Do not derive available models or client commands from old skills. Check the client formats currently needed against suitable official sources when the existing reviewed package state does not cover them.

Create concrete test cases for the usual flow, missing needed sources, relevant ambiguities and the boundary between suggestion and requested action. Check local references, prerequisites and both intended client formats. An existing general skill creator can help after review but is not a mandatory dependency. A single format validator can wrongly reject client-specific fields and does not replace a native test.

Have an independent review agent assess the skill against the task, the sources and the test cases. Fix confirmed findings within the requested scope and have the affected parts checked in a follow-up review. For existing bugs, the diagnosis approval remains authoritative. In the intended client, check invocation and loading as well as actual behavior. Prefer synthetic data. Use external actions and additional services only within the approved scope.

Report separately what has been drafted, formally reviewed, natively loaded and verified in behavior. Missing model tests, access or integration checks stay explicitly open. Install or publish only within the specifically requested scope.

[Test cases](references/test-cases.md) are test specifications, not model tests already passed.
