---
name: planhat-time-tracking
description: Prepares concrete Planhat time entries when asked for a weekly close or monthly reconciliation and transfers confirmed entries as verified drafts only on a booking instruction.
---

# Planhat Time Tracking

Follow the [core rules](../../rules/core.md), [storage](../../references/storage.md) and for requested writes the [action journal](../../references/external-writes.md). The shared process has two explicit entry points: **weekly close** for a selected week and **monthly reconciliation** for a selected month. Both start manually. Scope and the approved sources needed depend on the concrete task. If a needed source, assignment or technically verified Planhat connection is missing in the current client, ask first how to proceed and wait for the decision. A connection working in another environment is not proof it works here.

Merge work traces from the requested period, reconcile them against existing Planhat entries and remove duplicates and overlaps. If needed, use the suggestion from [Prepare Time Entries](../prepare-time-entries/SKILL.md). Mark estimated times as such and never guess a customer assignment. Before any booking, show the concrete entries with date, duration, activity and assignment, along with evidence and open questions. Weekly close may stay brief, monthly reconciliation checks the entire selected period including already booked times. An overview or preview is not yet a booking instruction.

Transfer only confirmed entries on a concrete booking instruction through a Planhat MCP access verified in the current client, as a **draft**. Before each entry, check the target and possible duplicates and afterward read back the stored entry including its draft status. Record external write actions briefly in the action journal. On timeout or an uncertain outcome, check Planhat first and do not blindly retry. Report what was actually stored and what remained open. Final submission happens manually in Planhat, never through this process.

[Synthetic test cases](references/test-cases.md) describe later behavior checks, not passed model tests.
