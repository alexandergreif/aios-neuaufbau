---
name: ui-design
description: When explicitly tasked, designs websites or user interfaces to match the design system, content and target audience and checks appearance and usability in the running system.
---

# UI Design

Follow the [core rules](../../rules/core.md) and [storage](../../references/storage.md). This process applies to explicitly requested websites and user interfaces. Read the briefing, the existing design system, relevant repository rules and the affected components. If a needed source or a capability needed for checking is missing, name the gap, ask first how to proceed and wait for the decision.

Derive a concrete visual direction from purpose, target audience and content. Use colors, typography, spacing, imagery and structure deliberately and within the existing design system. Visual elements are meant to improve orientation or understanding. Write clear interface text. Pay attention to responsive layouts, keyboard operation, visible focus, sufficient contrast and appropriate motion. Change existing components and styles only to the requested extent.

Check the change in the running local system visually and functionally, including a narrow view and an error case. For browser work use only a dedicated Chrome session via Chrome DevTools MCP and close it afterward. If this path is not available, ask how to proceed. Do not silently switch to another browser tool and do not claim visual or functional acceptance without a live check. Also have the change independently reviewed per the core rules. This skill replaces neither a requested publication nor the separate presentation process.

[Synthetic test cases](references/test-cases.md) describe later behavior checks, not passed model tests.
