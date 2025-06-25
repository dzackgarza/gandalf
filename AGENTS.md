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

The V1 E2E test provides a basic validation of the core workflow. Now, the individual agent capabilities need to be developed beyond their current placeholder/basic implementations. Based on `docs/roadmap/V1.md` and the original JULES_INSTRUCTIONS:

1.  **Establish `develop/V1` Branch:**
    *   If it doesn't exist, create a `develop/V1` integration branch from the current `main` or an appropriate base. This branch will be where `feature/V1-*` branches are merged. *(Self-correction: This was listed in original instructions but might be superseded by current practices. Verify if this branch is actively used or if features are merged to main/another branch.)*

2.  **Enhance Core Agent Functionality (Implement features from `docs/roadmap/V1.md`):**
    *   **`feature/V1-orchestrator-loop`**: While the `WorkshopManager` has a basic sequence, this task likely implies more robust state management, error handling, and potentially iterative capabilities if required for V1 (though V1 is simple sequential). Review `gandalf_workshop/workshop_manager.py` and the V1 roadmap description for this feature.
    *   **`feature/V1-communication-protocol`**: The current `PlanOutput`, `CodeOutput`, `AuditOutput` are basic. This task involves formally defining and implementing any more complex data structures or schemas needed for V1, as outlined in `gandalf_workshop/specs/data_models.py` and `docs/2_operational_framework/communication_protocols.md`. Ensure V1 focuses on simplicity.
    *   **`feature/V1-planner-agent-basic`**: The current planner is a placeholder. Develop `initialize_planner_agent_v1` in `gandalf_workshop/artisan_guildhall/artisans.py` to take a user prompt and produce a more structured plan (e.g., a list of steps as a string or simple list within the defined communication protocol). Refer to prompts in `gandalf_workshop/artisan_guildhall/prompts.py`.
    *   **`feature/V1-coder-agent-basic`**: The current coder is also basic. Enhance `initialize_coder_agent_v1` to better interpret plans from the Planner and generate corresponding code beyond the "Hello, World" and generic text file.
    *   **`feature/V1-auditor-agent-basic`**: The current auditor only does a syntax check. Expand `initialize_auditor_agent_v1` to perform more meaningful (though still basic for V1) static analysis or checks.

**General Guidance for Next Iteration:**

*   **Follow Test-Driven Development (TDD):** For any new Python code (orchestrator logic, agent functionality), write unit tests first. Augment with integration tests where appropriate.
    *   Look at existing tests in `gandalf_workshop/tests/` for examples.
    *   Ensure `Makefile` targets like `test` and `lint` (via `make audit`) are used and pass.
*   **Adhere to `CONTRIBUTING.md`:** This file provides guidelines for development.
*   **Branching Strategy:**
    *   Create specific `feature/V1-*` branches for each component as outlined in `docs/roadmap/V1.md`.
    *   Merge completed features into the designated integration branch (e.g., `develop/V1` or `main` as per project conventions).
*   **Small, Atomic Commits:** Keep commits focused on a single logical change.
*   **Consult Documentation:** The `docs/` folder, especially `docs/roadmap/V1.md` and `docs/VERSION_ROADMAP.md`, is critical.
*   **AGENTS.md:** Always check this file for the latest context and meta-instructions.

Good luck with the continued V1 implementation!
