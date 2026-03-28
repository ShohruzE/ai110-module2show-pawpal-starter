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
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
