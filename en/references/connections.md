# Connections and Actual Capabilities

An installed skill does not prove available service access. Check the tools actually offered in the chosen client, the signed-in service and the rights needed for the concrete task. Access in Blockbrain or in the other client is not proof for this client.

The following connections are selected for the first version. This list documents the desired scope, not connections that are already set up:

| Service | Desired scope | Responsibility and limit |
| --- | --- | --- |
| Outlook Calendar | Targeted reading of appointments, specifically requested changes | Observe selected calendars, time range and time zone. |
| Microsoft To Do | Read personal tasks and edit as requested | Authoritative personal task list. Propose recognized tasks first. |
| Outlook Mail | Targeted search and reading, create drafts | Sending and mailbox changes only when specifically requested. |
| Jira | Read tickets and project status, make requested changes | Authoritative source for tickets. No second personal task list. |
| Slack | Read relevant messages and threads, drafts | External write actions only when specifically requested. |
| Microsoft Teams | Read relevant chats and channel posts, drafts | Check which search and write options are actually available. |
| Confluence | Search pages, read and prepare drafts | Publishing and changing existing pages only when specifically requested. |
| Planhat | Transfer approved time entries via MCP as drafts and verify | Final submission stays manual. |
| GitHub | Read repositories, issues, PRs and check results | Commits, pushes and other GitHub write actions only when requested. |
| Sentry | Read and diagnose selected errors | No automatic fix or change to monitoring. |
| Datadog | Read and diagnose selected logs, metrics and traces | No changes to monitors or configuration. |
| Blockbrain | Check existing technical access for selected agents and workflows | Inclusion depends on evidenced benefit, rights and function. No Atrio plugin import. |

SharePoint and OneDrive are deferred for now. There is no ongoing monitoring or automatic full synchronization of these services.

If a needed source or capability is missing, name the specific gap and ask before working on a limited basis. A similar tool or a service with the same name does not silently replace the needed source. Check contradictions by recency, context and evidenced changes. Present remaining relevant uncertainties with sources for a decision.

Setup happens service by service in the respective client. Use the intended sign-in path. Required API keys belong in the private local `.env`, never in package sources, profile text or review reports. Empty fields and a skipped sign-in are allowed and shown as not yet set up. Do not output key values through inventories or status outputs.

For external write actions, [external-writes.md](external-writes.md) applies. If a matching concrete request already exists, do not ask for it again. On an uncertain outcome, verify in the target system and do not blindly repeat the action.
