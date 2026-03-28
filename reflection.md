# PawPal+ Project Reflection

## 1. System Design

3 core actions a user should be able to perform are:

- Entering their own information and their pets'
- Add and edit tasks
- Generate a daily schedule/plan based on constraints and priorities

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
  There should be User, Pet, Task, and Schedule Entities. A user should be able to perform all of the main actions. They should be able to create pets, tasks, and schedules.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
  - Yes, one change that I made was switched regular ID's to UUIDs to ensure production standards.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  Time, priority, duration/capacity, recurrence and completion.
- How did you decide which constraints mattered most?
  Ensuring urgent/time‑bound tasks run on time minimizes missed care; priority and duration then maximize useful work within available time.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  The scheduler uses a greedy, priority-first scheduler instead of an optimal solution.
- Why is that tradeoff reasonable for this scenario?
  This tradeoff is reasonable for this scenario because it's fast and simple enough to understand and explain to an owner, and prevents urgent tasks from being pushed late.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  I used GitHub Copilot for design brainstorming, debugging, and refactoring.
- What kinds of prompts or questions were most helpful?
  The prompts or questions that were most helpful were those that seemed very similar to what I would ask another person, like someone with more experience than me in standard human language as if it was a conversation.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  One moment I did not accept an AI suggestion as-is was when it was creating the skeleton code of the UML diagram. It had thinked too large-scale even though we wanted to limit the scope of this project. It had generated full code following the UML diagram exactly, which isn't inherently incorrect but not the goal given the prompt I gave and specifics of our task.
- How did you evaluate or verify what the AI suggested?
  I evaluated or verified what the AI suggested by carefully reading the output and comparing that to what I had asked/what my intended goal was.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

- **What behaviors did I test:**
  - Task ordering via `Task.sort_by_time()` to ensure tasks display in chronological order (tasks without a due time sort last).
  - Recurring-task advancement: marking a `daily`/`weekly` task complete creates the next occurrence and attaches it to the same `Pet`.
  - Schedule generation (`Schedule.generate()`): tasks are ordered by priority then due time and packed greedily from the day start.
  - Conflict detection: `detect_desired_time_conflicts()` flags identical requested start times; `detect_conflicts()` reports overlapping schedule slots.
  - Basic UI integration: `app.py` shows sorted tasks and surfaces warnings using Streamlit components.

  - **Why these tests matter:** They verify the core user-facing behaviors — correct ordering, reliable recurrence, and early detection of scheduling problems — so an owner can trust the plan and avoid missed care.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

- **Confidence level:** I am moderately confident (about 4/5) that the scheduler handles typical daily workflows correctly: priority-first ordering, basic recurring tasks, and the implemented conflict detections behave as intended.

- **Edge cases to test next:**
  - Daylight Saving Time transitions and timezone-aware datetime handling.
  - Tasks that span midnight or have very long durations (overnight care).
  - Complex recurrence rules (monthly boundaries, leap days, end-of-month behavior).
  - Concurrent tasks across multiple pets where the owner cannot perform both simultaneously — test recommended resolutions.
  - Performance and correctness with large task sets and overlapping durations.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  I am most satisfied with the UML generation and resulting class-based schema design.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  One thing I would improve or redesign is the UI. Everything is a single column, which doesn't work great for the UX and convenience of the app.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  One important thing I learned about designing systems or working with AI on this project is that its important to retain control and understanding of the project. If you let the AI make the decisions for you, you begin to lose control and understanding and you become the bottleneck at that point.
