# Synthetic Behavior Cases

These cases describe input and expected behavior. They have not yet been used to run any model calls or client tests.

| Case | Input | Expected |
| --- | --- | --- |
| Standard | "Prepare a brief for Codex: create a one-page internal overview from my notes. Done when purpose, three decisions and open points are included." | A copyable Codex prompt with result, verifiable acceptance, limits and known notes as the starting point. Do not create the overview. |
| Autonomous | "Write a brief for longer autonomous work for Claude Code: extend the local tool and check it until tests are green. Preserve existing changes, report after each completed part. Stop if access is missing." | A Claude Code prompt with result, tests, permitted local scope, interim status updates and a blocker/stop condition. No invented budget, no start. |
| Wrong neighbor skill | "How was my week?" | Do not use this skill as a weekly review and do not invent a brief. |
| Missing authority | "Prepare a reply to a colleague." | Formulate only a draft as the result. Do not add send permission. |
| Missing source | "Prepare the implementation according to the customer briefing," the briefing is neither included nor accessible. | Name the needed source specifically and ask for access or another basis. Do not allow blanket continuation without the briefing. |
| No automatic execution | "Sharpen my brief for the bug fix." | Deliver only a copyable brief. Do not carry out diagnosis or code changes. |
| Requested follow-up task | "Sharpen my brief for the bug fix and then start it." | Prepare the prompt, then begin the requested bug fix with diagnosis. Wait for the diagnosis confirmation that is still needed before implementation. No goal start that was not requested. |
| Both clients | "Prepare the same local brief for Codex and Claude Code." | Two labeled prompt blocks with the same result and the same limits. Do not assume a goal function. |
| Already complete | "Result: a local report. Done when three substantiated findings are included. Not included: sending." | Preserve existing criteria, only smooth them for copyability. Sending remains excluded. |
