---
name: precommit-review
description: When tasked, reviews your own uncommitted changes in a read-only way with a separate reviewer, repository context and relevant test results before a commit.
---

# Review Your Own Changes

Follow the [core rules](../../rules/core.md) and, for a stored report, [storage](../../references/storage.md). First determine the diff that belongs to the task, including staged and unstaged changes. Parallel changes made by someone else stay outside the assessment and untouched. Load the relevant repository rules, requirements, code context and relevant test results. If a needed source or a separate review agent is missing, name the gap, ask first about how to proceed and wait for the decision.

Have a reviewer not involved in creating the changes look at them critically. Trace changed control flows through functions, call sites and sibling paths. Check correctness, security, contracts and the performance and type questions relevant to the change. A defect needs the changed file and line, a concrete trigger, expected and actual behavior and the impact. Separate confirmed bugs from questions and optional notes. State which parts and tests were checked and which remain open.

The process is read-only. It does not change any files, does not create a commit and does not clean up changes made by someone else. For a fix of an existing bug, the diagnosis approval from the core rules applies. A pull request from someone else belongs to [PR review](../pr-review/SKILL.md), existing threads on your own pull request belong to [comment triage](../review-comments/SKILL.md).

[Synthetic test cases](references/test-cases.md) describe later behavior checks, not passed model tests.
