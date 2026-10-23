# Outputs and Project Assignment

This reference applies when a skill needs an output file or a project folder must be assigned or newly created. The confirmed local `paths.json` names source code, runtime, profile and output as well as coding and customer roots. Use the configuration path given during setup. If it is missing, ask for it. Do not derive it from a username, an old skill or a suggested default path.

Check the configuration with `scripts/check_config.py --config <paths.json>` from the package. The script does not create folders. A configuration value is not an approval to search the content located there.

For a concrete project assignment, `projects.md` lives in the configured profile folder. Use `scripts/check_register.py --config <paths.json> --register <projects.md> --project <key>`. Only an active, unambiguous and confirmed assignment yields a project path. Clarify a missing, paused or ambiguous assignment instead of guessing a folder or falling back to the personal storage.

## New Project

If a new project needs a folder and none exists yet, distinguish by type. A customer project lives under `<customer root>/<customer>/<project>/`, an internal repository with no customer relation under `<coding root>/<repository>/`. The roots are in `paths.customer_roots` and `paths.coding_roots`. If type, customer, project name or root is ambiguous, ask. Before creating anything, state the full folder and the planned register row, and create the folder only after confirmation. Create only the folders actually needed, no substructure in advance. Afterward, always enter the project in `projects.md`, with a unique key, an absolute folder path without `~` and status `active`, and check the entry with the `check_register.py` call named above. If a row for the project already exists with status `to-assign`, complete it instead of creating a second one. If a project folder already exists, it is not moved, only registered after the register row is confirmed. If it lies outside the configured roots, state that and ask whether a further root should be added in `paths.json`. After adding it, check the configuration with `check_config.py`. Without a new root, the folder stays unregistered, and you clarify how to proceed.

## Storing Outputs

Customer and project outputs live in the assigned project and follow its existing storage rules. Personal outputs with no project assignment live under `paths.output`. Sessions with no project reference also start there. Completed folders in `paths.output` are moved to `paths.output/archive/` only when tasked, and not deleted. The installed package folder, client configuration folder and AIOS source code are not an output storage location. A requested change to AIOS itself, by contrast, happens in the source code.

Choose an understandable file name that fits the task. Check before writing whether the file already exists. Small requested corrections update the working state. Extensive revisions or replacing an approved version keep the previous version. State the path actually created in the result. A plain chat answer needs no additional file unless the process calls for saving one.

Profile, knowledge and technical execution traces are not output files. Their own respective references apply to them. The next session does not carry over any commitment or completion from earlier outputs without current evidence.
