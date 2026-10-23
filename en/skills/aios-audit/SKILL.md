---
name: aios-audit
description: On invocation, checks the evidenced setup state of the AIOS per capability and client, names gaps and next steps and compares against a prior audit when needed.
---

# AIOS Status Assessment

Follow the [core rules](../../rules/core.md), [storage](../../references/storage.md) and for personal content [profile and knowledge](../../references/profile-and-knowledge.md). Check the current overall state. Reviewing specific work sessions is the job of system-retro.

Determine the confirmed installation scope and the target clients. A package manifest substantiates only its actual content, not the completeness of every selected capability. If the confirmed target list, a required piece of evidence or necessary access is missing, ask first and wait for the decision before a limited check. Do not read credentials or subject-matter content solely for an inventory.

Check the canonical rule sources, generated mirrors, integrations actually in use and task-relevant prerequisites. Use existing read-only check scripts and evidenced native check paths. In Claude Code, the available native prompt audit can be part of the check. Check availability and meaning in the actual client instead of assuming the same command for both clients. Do not install missing tools and do not change configuration as part of a plain status assessment.

Classify each selected capability per client in a traceable way:

| Status | Meaning |
| --- | --- |
| Missing | The required capability or integration is demonstrably not present. |
| Present | Files or integrations are present, but sufficient proof of function is missing. |
| Limited | A specifically named prerequisite or partial function is missing or fails. |
| Verified | The agreed behavior is demonstrated for this state and client with matching evidence. |

For each status, give evidence, date or checked revision, the specific limitation and the next step. An installation, a green format check or a successful load alone does not substantiate usable subject-matter function. Old evidence loses its validity when the relevant source, integration or dependency has changed. What is unknown stays unknown and is not claimed as missing or verified.

Compare against a selected prior audit on request. Distinguish actual improvements from merely new files or outdated check results. Do not award points for file length, regular use or existing briefings. Suggest a few concrete next steps. Changes and external write actions remain separately requested work.

[Test cases](references/test-cases.md) are test specifications, not model tests already passed.
