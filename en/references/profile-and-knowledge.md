# Setting Up and Maintaining Profile and Knowledge

This reference is needed for setup, profile maintenance, knowledge intake or profile transfer. It is not an additional startup file and not a loading plan. Package templates under `../templates/` stay empty. Actual content belongs in the configured private profile folder.

## Setup

1. Use existing confirmed details. Use targeted questions to clarify details still missing on name, role, language, time zone, working hours, working style and priorities. Do not derive anything from the username or other private files. The Language field determines the output language, and with several entries, the one named first. With several languages, ask for the preferred one and enter it first.
2. Show a preview of the details to be saved. Mark anything unanswered as open. Only after confirmation create `profile.md` in the chosen profile folder. Do not silently overwrite existing files.
3. Ask for coding and customer project roots per Mac. Registering concrete projects is a separate assignment, not a task to search all subfolders. Keep unique keys and confirmed folders in the private `projects.md`.
4. Use `knowledge/INDEX.md` and short topic notes only for actual knowledge intake. Keep technical state data under `state/`. These private subfolders are neither updated from the package nor removed when it is uninstalled.

## Maintenance

- Propose new lasting details as a concrete change with a preview and have it confirmed. A clear "remember this" already counts as a request to save.
- Small, explicitly stated lasting preferences, such as response length or output format, may be saved without asking. Mention it briefly and allow correction or deletion. On conflict with an existing rule, clarify first.
- Guesses, sensitive details, grants of authority, commitments and rule changes do not fall under this exception. Wishes stated only for one task stay limited to it.
- Project decisions belong in the project's working files. Do not additionally maintain them as a general profile rule. Personal tasks stay in To Do, project tickets in Jira.

## Knowledge

Propose reusable insights with source, location, date, scope of validity and open uncertainties. Save as lasting knowledge and link in the index only after confirmation. An explicit save request is enough. Do not automatically import full chats, messages or documents. On conflicting sources, the shared core rules apply.

## Deliberate Transfer to Another Mac

The export/import process shows the selected profile fields and a change preview. Personal profile details can be transferred. Folder assignments are reconfirmed on the target Mac. The local path configuration is not a transferable profile.

`.env`, other credentials, OAuth files, the action journal, diagnostic logs and output files do not belong in the profile export. An export must not blindly copy the entire profile folder. Do not follow links to files outside the confirmed selection. On differing existing details, present a merge for decision instead of overwriting automatically.

The package contains `scripts/profile_transfer.py` for this. It exports only the seven profile fields and small preferences. During import, differing values are shown individually. The first version offers an explicitly confirmed replacement of the profile with a backup, not an automatic merge. Paths, project register and knowledge stay local. The synthetically tested process is described in `docs/profiltransfer.md`.
