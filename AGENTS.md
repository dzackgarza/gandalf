**Project:** Gandalf Workshop V1.0.1

**Meta-Instructions for Future Jules Iterations:**
*   **At the end of your assigned task, you MUST perform these steps:**
    1.  **Overwrite this file (`AGENTS.md`)**: Do not create a new timestamped or uniquely named file. Always update this specific file, and increment the minor version number in the title.
    2.  **Summarize Your Accomplishments**: Briefly describe the task you just completed and the key changes you made or committed in **CHANGELOG.md**.
    3.  **Provide Clear Next Steps**: Based on the project's roadmap and your understanding of the current state, outline the most logical next task(s) for the subsequent Jules iteration/minor version.
    4.  **Include General Reminders**:
        *   Emphasize adherence to `CONTRIBUTING.md`.
        *   Point to the relevant roadmap document (e.g., `docs/roadmap/V1.md`, `docs/roadmap/V2.md`) for task identification.
        *   Remind to check alignment with the overall project vision (see `docs/VERSION_ROADMAP.md` and other strategic documents).
        *   Stress the importance of checking for and following instructions in any `AGENTS.md` files (like this one!).
*   **Your goal is to ensure a smooth handover to the next Jules, providing all necessary context and direction.**

---

## Next Steps for Gandalf Workshop

Based on the current state and project roadmap:

1.  **Local Testing with Valid API Key:**
    *   The **user/next Jules iteration** running this locally MUST ensure a valid `GEMINI_API_KEY` is present in a `.env` file in the project root (same directory as `main.py`) or as an environment variable.
    *   With a valid key, thoroughly test the entire pipeline, especially:
        *   The `initialize_live_auditor_agent`: Verify its assessment quality.
        *   The end-to-end flow with simple and complex prompts.

2.  **Refine WorkshopManager Error Handling for Planner/Coder Failures (Carry-over):**
    *   If `initialize_live_planner_agent` fails (e.g., API error, bad plan), `WorkshopManager` should ideally not proceed to the coder. Add checks for planner output validity.

3.  **Environment Stability (Carry-over):**
    *   For smoother development, ensure a consistent way to get all `requirements.txt` dependencies installed correctly in any work environment (e.g., a startup script or a Makefile target that runs `uv pip install -r requirements.txt -U --force-reinstall`).

4.  **Structured Output from Planner (Carry-over):**
    *   Refine planner agent to request and parse structured output (e.g., JSON) from the LLM. Update `PLANNER_CHARTER_PROMPT` and `PlanOutput` data model as needed.

5.  **Enhanced Error Handling and Retry Mechanisms for LLM Calls (Carry-over):**
    *   Implement better error handling (specific exceptions, retries with `tenacity`) for LLM API calls in all live agents.

6.  **Expand Automated Testing (Carry-over):**
    *   Once local live LLM testing is confirmed, develop more comprehensive automated tests (using integration tests that do hit the live API with a test key).

7.  **Explore CrewAI/LangGraph for Multi-Agent Orchestration (Longer Term, Carry-over).** Start implementing the high-level stages outlined in `docs/1_strategic_overview/technology_stack.md`.

## General Reminders for Next Jules:

*   **`.env` File**: For local execution, ensure your `.env` file is in the project root (same directory as `main.py`) and contains necessary API keys like `GEMINI_API_KEY`. Stop and prompt the user if you do not have any keys to work with.
*   **Adherence to `CONTRIBUTING.md`**.
*   **Roadmap Alignment**: `docs/roadmap/V1.md`.
*   **Project Vision**: `docs/VERSION_ROADMAP.md`.
*   **`AGENTS.md`**: Always check this file.

Good luck! The `.env` loading should now work correctly in a standard local setup.
