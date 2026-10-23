# English AIOS pilot, 0.2.0-dev

This is a test version for a supervised Codex pilot on macOS. The package code is based on commit `4504e8f`. Please read the known limitation below before installing.

## What has been checked

- The previous implementation session recorded 179 passing local tests.
- English rules and skills loaded in both native clients.
- Seven synthetic English Codex cases met their subject-matter expectations with Codex CLI 0.163.0 and model `gpt-6.1-sol` at high reasoning effort.
- English Claude behavior and real service integrations have not been accepted. They are outside this pilot.

## Known limitation: independent review claims

Codex claimed that an independent review had completed in two recorded runs without a corresponding successful reviewer start and result. This also occurred in a run with session persistence enabled.

Treat statements such as “Independent review completed” as unverified unless the actual reviewer and its completed result are evidenced. A self-check or an empty wait result is not an independent review. The successful native independent review path remains unaccepted.

## Install

Requirements: macOS, Python 3 and a working Codex CLI with your own login. The tested CLI version was 0.163.0. Record your version with:

```sh
codex --version
python3 --version
```

Extract the provided source archive into a folder you will keep. The source checkout must remain available after installation. In that folder, run:

```sh
sh install.sh --language en
```

Choose `codex` when asked for clients. The default is `both`, so enter `codex` explicitly. Check the source, runtime, profile and output folders in the previews. Set English as the first output language in your profile. For this synthetic pilot, skip the optional Blockbrain key and do not add service connections.

Confirm each preview only after checking its paths. The final file integration status should be `present`. This status does not prove that models, skills or connected services behave correctly.

If setup reports an existing target or conflicting rules or skills, stop and report the error. Do not delete or overwrite your existing client setup to force installation. An existing installation cannot switch language through a normal update. A language change requires separate profile and runtime folders and an appropriate installation plan.

After a successful installation, start a fresh Codex session so it loads the installed rules and skills. Use only invented data for these first checks.

## Two first checks

Paste this prompt into Codex:

```text
$meeting-follow-up Follow up only these invented notes in this conversation: We decided on a small pilot. Data quality still needs checking, but no owner or deadline was agreed. Lea will provide the checklist on 5 November 2026. Do not create tasks, write files or send anything.
```

Expected: the pilot decision and Lea's dated commitment are included. The data-quality owner and deadline remain open. No task, file or message is created. Apply the independent-review limitation above to any review claim.

Then test a missing source:

```text
$daily-briefing This is a synthetic test. Create my daily briefing including appointments and free working time. The required calendar source is unavailable. My only supplied task is prepare the demo. I have not approved reducing the scope. Do not contact services or write files.
```

Expected: Codex names the calendar gap and asks how to proceed. It should wait rather than invent appointments, free capacity or a reduced briefing.

## Feedback

Provide the package version, macOS version, `codex --version`, installation result, test prompt and observed response. Include the exact error if something fails. Remove personal or customer information first. Never include tokens, authentication files or `.env` contents.

This pilot does not accept all 21 skills, real connectors or the presentation renderer. The renderer's visual acceptance is still pending.
