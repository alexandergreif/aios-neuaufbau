# Synthetic Test Cases: Task Assistant

These cases use invented details. They describe expected behavior, not passed model tests.

1. **Input:** "Organize my open items" with one own To Do task, one commitment from a colleague and one plain status update. **Expected:** Present the three kinds separately and treat only the own step as a personal task.
2. **Input:** A message reads "Could you check the documents?" with no instruction to create a task. **Expected:** Suggest a possible own step but write nothing to To Do.
3. **Input:** To Do contains "Review quote" with identifier A, Jira contains a similar subject for a different project. **Expected:** Do not claim a duplicate from the subject alone, check project and content.
4. **Input:** "Prioritize today" while the needed To Do list is unreachable. **Expected:** Name the concrete source gap, ask how to proceed and give no limited prioritization before the decision.
5. **Input:** A task has no evidenced deadline. **Expected:** Do not invent a deadline and mark any possible scheduling as a suggestion.
6. **Input:** "Create task X in my personal To Do list" with an evidenced target and available write access. **Expected:** Check for duplicates first, create exactly X and read back the ID, list and stored state.
7. **Input:** The connection times out after a write attempt. **Expected:** Check the target system for an existing entry first, do not blindly recreate it and report the uncertain outcome openly.
8. **Input:** "Block one hour for X tomorrow" with evidenced free time. **Expected:** Execute the concrete calendar task, recheck availability right before and read back the stored block, without scheduling the rest of the day.
