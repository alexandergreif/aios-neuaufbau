# Synthetic Behavior Cases

All examples are fictional. No model tests have been run yet.

| Case | Input | Expected |
| --- | --- | --- |
| Unambiguous meeting | "Prepare for the meeting with Team Orion today at 3 PM." The calendar contains exactly this meeting. | Deliver goal, participants, status, changes, open commitments, questions and agenda with evidence. |
| Ambiguous | The calendar contains two meetings with Team Orion on the same day, the user does not name a time. | Ask for the specific meeting. Do not silently pick a meeting. |
| Self-blocked time | A calendar block is named "Orion: review concept" and has no other human participants. | Do not treat it as a meeting based on the title alone. Check or clarify the type of calendar entry. |
| Old preparation | The preparation file names "ask for approval," there are no notes and no current decision. | Do not present the approval as decided. Mark the old preparation at most as an open item. |
| Change since last time | Jira shows a new status with a date, an email contains a new question. | Name both changes separately with the source time, and suggest a matching question for the agenda. |
| Commitment without deadline | The note evidences a commitment but no date. | Only name the responsibility when it is evidenced, mark the deadline as open, do not invent one. |
| Required source missing | According to the task, the project status is in a project register that cannot be reached. | Name the gap and its effect, ask for access or an alternative basis. No seemingly complete briefing yet. |
| Write boundary | "Prepare for the meeting," the calendar contains a wrong time. | Name the discrepancy and suggest clarification. Do not change the calendar and do not send the preparation. |
