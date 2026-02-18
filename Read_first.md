Read CLAUDE.md first (you should have already). Then read Tonights_v65_Build_Plan.md and Brainstorm_Capture_2026-02-17.md. These are your session briefs.

This is a v6.5 QoL build. We're making Ghost Shell a daily driver.

Before writing ANY code, read the entire src/ directory and data/ directory to understand the current codebase. Tell me what you found — which engines exist, which are stubs, which commands exist, what state things are in.  Then we will go into a `AskUserQuestion` where you ask me some questions to help hit the mark of this "QoL Build".

Then we start with Build Item 1: Loader Engine. Do NOT skip ahead. One item at a time. I commit between each item.

SESSION REPORT REQUIREMENT:
At the end of this session (or when I say "report"), produce a Session Report markdown file called SESSION_REPORT_[DATE].md that includes:

1. BUILD STATUS — For each item in Tonights_v65_Build_Plan.md, mark it:
   - ✅ COMPLETE (tested, working)
   - ⚠️ PARTIAL (started, not finished — explain what's left)
   - ❌ NOT STARTED (didn't get to it)
   - 🔄 MODIFIED (scope changed during build — explain why)

2. FILES CHANGED — List every file created, modified, or deleted with a one-line summary of what changed.

3. DEFINITION OF DONE CHECKLIST — Go through the "Definition of Done" section in the build plan and check each item pass/fail.

4. DECISIONS MADE DURING BUILD — Any design decisions, trade-offs, or scope changes that happened while coding. These need to be added to CLAUDE.md's Decision Log or the Brainstorm Capture.

5. BUGS/ISSUES FOUND — Anything broken, flaky, or concerning that wasn't in scope but was discovered.

6. LESSONS LEARNED — What went well, what was harder than expected, what should change for next session. Include any new "Never Again" items for CLAUDE.md.

7. NEXT SESSION BRIEF — A ready-to-use starting prompt for the next coding session. What to pick up, what context is needed, what files to read.

8. README UPDATES — Any changes that should be reflected in README.md (new commands, new features, changed behavior).

9. CHANGELOG ENTRY — A draft changelog entry for this build in Keep a Changelog format.

Save this report as SESSION_REPORT_[DATE].md in the project root. I will review it, then move it to my documentation.

- After your review if we dont need an extended `AskUserQuestion` please keep it short.  We need to be token cautious for this build.  This is not a HUGE build.  I should have covered the design and worklist in the files you read.