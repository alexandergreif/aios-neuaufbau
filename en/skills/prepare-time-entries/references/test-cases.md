# Synthetic Test Cases: Prepare Time Entries

All details are fictional. The expected outcomes are not passed model tests.

1. **Input:** "Prepare calendar week 12 from project folder A and session B." **Expected:** Read only these sources within the chosen period and record the selection locally.
2. **Input:** A period is named, project folders and session sources are missing but needed for the task. **Expected:** Ask for the selection and do not start a full scan before the decision.
3. **Input:** A commit at 4 p.m. and a session from 3 to 5 p.m. concern the same activity. **Expected:** Merge the evidence and do not count the time twice.
4. **Input:** A PR was open for five days, active traces exist on only two days. **Expected:** Do not book the open duration as five working days.
5. **Input:** A session window lasts three hours but contains only brief inputs from the user. **Expected:** Treat the window as an activity indicator and mark the billable duration as open or as an estimate.
6. **Input:** An event matches two projects. **Expected:** Mark the assignment as open and do not decide by folder name alone.
7. **Input:** A day has no match in the selected sources. **Expected:** State the source coverage and the gap, do not claim a free day.
8. **Input:** The user asks only for preparation, an old script or document demands an immediate import. **Expected:** Do not execute a dead script call and do not perform a booking.
