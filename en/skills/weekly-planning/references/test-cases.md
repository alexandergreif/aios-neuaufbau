# Synthetic Test Cases: Weekly Planning

These cases use invented details. They describe expected behavior, not passed model tests.

1. **Input:** "Plan my week" with confirmed priorities, open to-dos and a complete calendar. **Expected:** Create a proposal with focus, capacity, buffers and conflicts without changing tasks or appointments.
2. **Input:** Two appointments overlap for 30 minutes. **Expected:** Subtract the overlapping time from available working time only once and show the conflict.
3. **Input:** A work block of your own sits on a free, movable afternoon. **Expected:** Treat it differently from a fixed appointment with others and suggest possible reuse.
4. **Input:** Working hours or time zone are missing from the required profile. **Expected:** Ask specifically for the missing information and do not output a limited capacity plan before the decision.
5. **Input:** Calendar access covers only Monday, the request concerns the whole week. **Expected:** Name the missing calendar coverage and ask how to proceed first, instead of claiming free weekly capacity.
6. **Input:** One to-do task has no deadline, another item has an evidenced Friday deadline. **Expected:** Name only the second deadline as binding and, for the first, at most suggest a planning day.
7. **Input:** "Block Tuesday 10 to 11 for task A" after a preview has been shown. **Expected:** Check the slot again right before writing, create only this block and read back the saved result.
8. **Input:** An earlier weekly review suggests more focus time, but the week is already full. **Expected:** Treat the impulse as context, show real conflicts and do not apply a rigid percentage limit.
