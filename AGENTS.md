# AGENTS.md (Formerly JULES_INSTRUCTIONS.md)

**Project:** Gandalf Workshop

**Meta-Instructions for Future Jules Iterations:**
*   **At the end of your assigned task, you MUST perform these steps:**
    1.  **Overwrite this file (`AGENTS.md`)**: Do not create a new timestamped or uniquely named file. Always update this specific file.
    2.  **Summarize Your Accomplishments**: Briefly describe the task you just completed and the key changes you made or committed.
    3.  **Provide Clear Next Steps**: Based on the project's roadmap and your understanding of the current state, outline the most logical next task(s) for the subsequent Jules iteration.
    4.  **Include General Reminders**:
        *   Emphasize adherence to `CONTRIBUTING.md`.
        *   Point to the relevant roadmap document (e.g., `docs/roadmap/V1.md`, `docs/roadmap/V2.md`) for task identification.
        *   Remind to check alignment with the overall project vision (see `docs/VERSION_ROADMAP.md` and other strategic documents).
        *   Stress the importance of checking for and following instructions in any `AGENTS.md` files (like this one!).
*   **Your goal is to ensure a smooth handover to the next Jules, providing all necessary context and direction.**

---

**Your Current State & Context (as of this update):**
*   You (the current Jules iteration) just successfully implemented the V1 End-to-End (E2E) test for a "Hello, World!" application generation.
*   This involved:
    *   Refactoring `gandalf_workshop/workshop_manager.py`'s `run_v1_commission` method to call the actual V1 agent functions (`initialize_coder_agent_v1`, `initialize_auditor_agent_v1`) from `gandalf_workshop/artisan_guildhall/artisans.py`, removing its internal mock logic for these agents.
    *   Updating `gandalf_workshop/artisan_guildhall/artisans.py`:
        *   Modified `initialize_coder_agent_v1` to accept a specific `output_target_dir` (controlled by `WorkshopManager`) and to create `main.py` for the "Hello, World!" case.
        *   Refactored `initialize_auditor_agent_v1` to use the built-in `compile()` function for syntax checking, preventing issues with file modification (`.pyc` generation) that were causing `UnicodeDecodeError` in tests.
    *   Adapting the existing E2E test file `gandalf_workshop/tests/test_e2e_v1.py`:
        *   Removed mocks for agent functions (`initialize_planner_agent_v1`) and data models (`CodeOutput`, `AuditOutput`) to make the tests truly E2E for the success path.
        *   Updated `test_e2e_hello_world_generation` to verify file creation (`main.py`), content, successful execution via `subprocess`, and audit success.
        *   Refined `test_e2e_audit_failure_syntax_error` to use `monkeypatch` for the Coder to produce a file with a syntax error, ensuring the Auditor correctly reports the failure.
    *   Updating the unit tests for `WorkshopManager` in `gandalf_workshop/tests/test_workshop_manager.py` to mock the agent *initialization functions* rather than the data models, aligning with the `WorkshopManager` refactoring.
    *   Ensured all tests pass by running `python -m pytest ...` after resolving dependency and environment issues (initial `ModuleNotFoundError: No module named 'yaml'` and subsequent test failures due to code behavior and test assertions).
*   All these changes are staged for commit.
*   This `AGENTS.md` file has been updated with this summary and next steps.

**Next Steps & Focus Areas for the *Next* Jules Iteration:**

**1. Understanding Current State & V1 Goals:**

*   **Revised V1 Goal:** The primary goal for V1 of the Gandalf Workshop is to **prove the viability of LLM-based code generation for a non-trivial task.** This means the Coder agent (`initialize_coder_agent_v1`) **must** use an LLM to generate functional code beyond simple "Hello, World!" examples. Refer to `docs/roadmap/V1.md` for the updated detailed V1 goals and E2E test cases (including one for a utility application).
*   **Previous Coder State (Investigation Results):**
    *   My investigation (previously in `AUDITV1_2.md`, now summarized here) confirmed that the `initialize_coder_agent_v1` function in `gandalf_workshop/artisan_guildhall/artisans.py` was a **placeholder**.
    *   It did **not** use LLMs. Instead, it had hardcoded logic to either output a "Hello, World!" script or echo the task description into a text file (e.g., `task_output.txt` created in `gandalf_workshop/commission_work/commission_f7334504/` during a previous test run, which will be deleted).
    *   This placeholder behavior was the reason the workshop failed to produce actual code for prompts like "create a calculator app...".
    *   The project *does* include dependencies for LLM integration (e.g., `openai`, `litellm`, `crewai`, `langchain` in `requirements.txt`) and a detailed `CODER_CHARTER_PROMPT` in `gandalf_workshop/artisan_guildhall/prompts.py`. These were not used by the V1 Coder placeholder.
*   **Output Standardization:** The output path for commissions has been changed. All artifacts generated by running `python main.py --prompt "..."` will now be placed in an `outputs/<commission_id>/` directory in the repository root (modified in `gandalf_workshop/workshop_manager.py`).

**2. Crucial Next Task: Implement LLM-Based Coder for V1 Compliance:**

The **immediate and highest priority** is to modify `initialize_coder_agent_v1` in `gandalf_workshop/artisan_guildhall/artisans.py` to meet the V1 LLM-based code generation requirement.

*   **Action:** Enhance `initialize_coder_agent_v1` to:
    1.  Integrate with an LLM (e.g., using the `openai` or `litellm` libraries). API key management will be essential (assume environment variables or a secure method).
    2.  Utilize the `CODER_CHARTER_PROMPT` (or a refined version) to instruct the LLM.
    3.  Effectively use the `PlanOutput` from the Planner agent to guide the LLM's code generation.
    4.  Ensure the LLM generates functional Python code for a non-trivial task (e.g., the word count CLI tool specified in `docs/roadmap/V1.md`'s Test Case 2).
    5.  Save the generated Python code to a file (e.g., `app.py` or `main.py`) within the correct `outputs/<commission_id>/` directory.
    6.  Return a `CodeOutput` object pointing to the generated file.

**3. How to Verify V1 Coder Compliance:**

To check if the Coder agent meets the revised V1 goals, you should:

*   **Run a Test Commission:** Execute the main pipeline with a suitable prompt, for example:
    ```bash
    python main.py --prompt "Create a Python CLI tool that takes a text file as input and counts the occurrences of each word, then prints the top 5 words and their counts."
    ```
*   **Inspect Output:**
    *   A new directory should be created, e.g., `outputs/commission_xxxxxxxx/` (where `xxxxxxxx` is the generated ID).
    *   Inside this directory, you should find one or more Python files (e.g., `app.py`).
    *   The content of these files **must be functional Python code** that attempts to solve the prompted task, generated by an LLM. It should not be a simple "Hello, World!" (unless that was the specific prompt) or an echo of the task.
*   **Confirm LLM Usage (if necessary):**
    *   Ideally, the `CodeOutput.message` from `initialize_coder_agent_v1` might include details about the LLM interaction or the filename.
    *   If LLM usage isn't obvious, you might need to temporarily add logging within `initialize_coder_agent_v1` to confirm an LLM call was made and what its response was.
*   **Functional Check:** Attempt to run the generated Python code with sample input to see if it works as expected by the prompt.

**4. Other V1 Agent Enhancements (Supporting the LLM Coder):**

Once the Coder agent is capable of LLM-based generation, review and enhance other V1 agents:

*   **`feature/V1-planner-agent-basic`**: Ensure `initialize_planner_agent_v1` produces plans detailed and structured enough to be useful for the LLM-based Coder.
*   **`feature/V1-auditor-agent-basic`**: Expand `initialize_auditor_agent_v1` to perform more meaningful static analysis on the LLM-generated code. Consider adding basic functional checks if feasible for V1 (e.g., does the generated script run without immediate errors for a given input?).
*   **`feature/V1-orchestrator-loop`**: Review if `WorkshopManager` needs changes to better support an iterative LLM-based coding loop (e.g., feeding audit results back to the Coder for revision via LLM). This might be post-V1, but consider the hooks.
*   **`feature/V1-communication-protocol`**: Review if `PlanOutput`, `CodeOutput`, `AuditOutput` data models need refinement for the LLM-based workflow.

**5. General Guidance:**

*   **Follow Test-Driven Development (TDD):** For the new Coder LLM logic, write unit tests. Ensure E2E tests from `docs/roadmap/V1.md` (especially Test Case 2 for the utility app) pass.
*   **Branching:** Use `feature/V1-coder-agent-llm` (or similar) for the Coder implementation.
*   **Consult Documentation:** Refer to `docs/roadmap/V1.md` (for updated V1 goals/tests) and `gandalf_workshop/artisan_guildhall/prompts.py` (for `CODER_CHARTER_PROMPT`).
*   **AGENTS.md:** Update this file with your progress and next steps for the subsequent iteration.

Good luck implementing the LLM-powered V1 Coder!
