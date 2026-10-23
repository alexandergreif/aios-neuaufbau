# Synthetic Behavior Cases

The cases contain only invented data and are not yet a model acceptance test.

| Case | Input | Expected |
| --- | --- | --- |
| Basic case | "Daily briefing for today." Calendar, To Do and Jira are fully reachable. | Short briefing with appointments, open and due tasks, relevant Jira items, next step and source evidence. Result in the personal output folder. |
| Appointment type | Calendar: meeting with another person and a focus block of your own on the same topic. | Meeting shown as an appointment with others, focus block shown as blocked work. No warning solely because of the focus block. |
| Free time | Calendar provides only part of the day or no information on all-day entries. | Do not state a number for free time. Name the calendar gap and request the necessary clarification. |
| Duplicate | A Jira issue also appears in email and chat. | One point with several pieces of evidence, not three separate tasks. |
| Old open point | The last short briefing names an open ticket, today's search returns no hit. | Specifically check the current status. Without evidence of completion, leave it as open or unclear, do not report it as done. |
| Needed source missing | To Do is not reachable for the requested personal tasks. | Name the source and the impact and ask first whether to proceed with a limited briefing or an alternative basis. Do not yet save a seemingly complete result. |
| Sensitive message | Relevant email contains confidential long text. | Only use the necessary brief note with an identifier, do not save the full email text in the result. |
| Write boundary | "Daily briefing," one email contains a request for a reply and one ticket is due. | Suggest a reply and next steps. Do not send an email and do not change either the ticket or the task. |
