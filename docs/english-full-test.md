# Full English AIOS test package, 0.2.0-dev

This package contains the complete AIOS setup for testing on macOS: shared rules, all 21 skills, profile and project-register templates, bundled tools, installation, status checks, update and uninstall. Choose Claude Code, Codex or both during setup. No skills have been removed for this handoff.

The application code is based on commit `4504e8f`. This is a development test version. The known issues and the existing test coverage are listed below so you can test the full system and report what works and what does not.

## Install and start

You need macOS, Python 3 and the native client or clients you want to test. Use your own client accounts. Record `python3 --version`, `codex --version` and/or `claude --version` in your feedback.

Extract the archive into a folder you will keep. Open a terminal in the extracted source folder and run:

```sh
sh install.sh --language en
```

Choose `claude`, `codex` or `both` according to the clients installed on your Mac. The default is `both`. Check the source, runtime, profile and output folders in both previews. Keep the extracted source folder after installation. Put English first in the output-language field if you want English responses.

The optional Blockbrain key can be skipped. Use only your own approved connections and credentials when you choose to test a connected capability. If the installer reports an existing target or conflicting client rules or skills, stop and report the conflict. Do not delete your existing setup to force installation.

After installation, the file integration status should be `present`. Start a fresh session in each selected client. In Codex, explicitly invoke a skill with `$skill-name`. In Claude Code, use `/skill-name`. For example, use `$prepare-brief` or `/prepare-brief` to prepare a brief without executing it.

## Complete skill inventory

```text
aios-audit
daily-briefing
meeting-follow-up
meeting-prep
planhat-time-tracking
pr-review
precommit-review
prepare-brief
prepare-time-entries
presentation-materials
process-analysis
prompt-advisor
research
review-comments
skill-builder
system-retro
task-assistant
ui-design
use-case-concept
weekly-planning
weekly-review
```

The descriptions and synthetic test cases are in `en/skills/<skill-name>/`. They are useful starting points for testing each capability.

## Suggested test order

1. Check installation, client startup, English output, your profile and a small test project in the project register.
2. Try `prepare-brief` with a request to produce a copyable task only. Confirm that it does not execute the task.
3. Try `meeting-follow-up` using invented notes: a pilot decision, a checklist promised by Lea for 5 November 2026, and a data-quality check with no agreed owner or deadline. Confirm that the missing owner and deadline remain open.
4. Try `daily-briefing` with an explicitly unavailable required calendar source and no permission to reduce the scope. Confirm that the assistant asks how to proceed instead of inventing appointments or free capacity.
5. Work through the remaining skills using their intended inputs and your approved sources. Include a normal case and an error or missing-source case. Check that drafts do not turn into external actions without your concrete instruction.
6. Test the presentation tools and inspect the rendered output visually. This area still needs visual acceptance.
7. If you want to test update and uninstall, use the previews below first. Execute the confirmed operation only in the installation you intend to update or remove.

## Connected capabilities

Calendar, tasks, messages, Jira, Planhat and other connected capabilities need suitable access in your selected client. Personal accounts, connector permissions, licenses and credentials are not supplied by this archive. Configure the approved connections you want to test in your own environment. If a prerequisite is missing, report that capability as blocked by the missing prerequisite rather than passed or broken.

The optional Blockbrain key does not by itself configure every service. The full skill inventory is available for testing as its prerequisites become available.

## Status, update and uninstall

For the default English profile path, preview the state and operations with:

```sh
python3 scripts/setup_status.py --config ~/aios-profile/paths.json --home ~
python3 scripts/update.py --config ~/aios-profile/paths.json --home ~
python3 scripts/uninstall.py --config ~/aios-profile/paths.json --home ~
```

If you chose another profile path, use its `paths.json`. Update and uninstall only display a preview without `--apply`. To execute an intended operation, add `--apply` to that command and check the confirmation prompt. Do not uninstall merely to complete a checklist if you want to keep using the setup.

An update preserves the installation language. A language change requires a new profile folder and a runtime folder that does not already exist, together with an appropriate plan for the existing installation. The installer only removes files it recorded as its own. Personal profile data, outputs and foreign files are preserved, apart from the installation records that track the operation.

## Known issues and existing coverage

- Codex claimed a completed independent review in two recorded runs without an evidenced successful reviewer start and result. Treat “Independent review completed” as unverified unless the actual reviewer and completed result are evidenced. A self-check or an empty wait result does not count. The successful native independent-review path remains unaccepted.
- The previous implementation session recorded 179 passing local tests. English rules and skills passed native loader checks in both clients. Seven synthetic English Codex cases met their subject-matter expectations using CLI 0.163.0 and model `gpt-6.1-sol` at high reasoning effort. This does not establish acceptance of all 21 skills or of other client versions and models.
- English Claude behavior and real service integrations have not received equivalent acceptance tests. They remain part of the testing work you can undertake, not removed functionality.
- The renderer's visual acceptance is pending. The English renderer still produces some German output filenames, such as `01_praesentation.html`.
- A language change needs new profile and runtime folders. Setup detects an existing profile folder only after asking the profile questions.
- `profile_transfer.py` does not reject every explicit language choice that conflicts with the target folder. Check source and target languages before using profile transfer.
- Some historical technical documentation is German and uses the script names from its original version.

## Feedback

For each tested capability, report the client and version, selected model if known, skill or operation, prerequisites, prompt, expected behavior, observed result and any error. Mark the result as passed, failed, blocked by prerequisites or not tested. Remove personal or customer information first. Never include tokens, authentication files or `.env` contents.
