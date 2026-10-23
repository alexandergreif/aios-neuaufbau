---
name: prepare-time-entries
description: Prepares a substantiated time proposal for a chosen period from explicitly selected project and session sources, without booking hours.
---

# Prepare Time Entries

Follow the [core rules](../../rules/core.md) and [storage](../../references/storage.md). Clarify the period, the explicitly chosen project folders and the approved session sources. Record this selection locally for the current run. There is no default folder search and no blanket full scan. If a needed source or approval is missing, first ask how to proceed and wait for the decision before continuing on a limited basis.

Collect only relevant work traces within the selection. Order events by day, activity and possible project. Link every proposed time allocation to its evidence. A commit, an open PR, an agent session or a time window proves activity, but not automatically billable duration. Separate measured time, confirmed information and estimate. Check for overlaps, duplicates, parallel work and gaps. For an unclear assignment or duration, ask a targeted question instead of choosing the most plausible customer. An empty search result does not prove a free day.

Deliver a verifiable proposal with date, activity, project assignment, duration with status and open questions. An existing collection script is not yet implemented in this package and must not be assumed to be an executable step. This preparation does not book anything and does not upload any work traces to an external service without being asked. For a later Planhat task, use [Planhat Time Tracking](../planhat-time-tracking/SKILL.md).

[Synthetic test cases](references/test-cases.md) describe later behavior checks, not passed model tests.
