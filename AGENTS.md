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
*   You (the previous Jules iteration) just successfully completed the task `feature/V1-coder-agent-basic`.
*   This involved:
    *   Implementing the `initialize_coder_agent_v1` function in `gandalf_workshop/artisan_guildhall/artisans.py`. This agent takes a `PlanOutput` object and generates code, creating a `main.py` with "Hello, World!" for the specific E2E task, or a `task_output.txt` for generic tasks. It outputs a `CodeOutput` object.
    *   Adding corresponding unit tests in `gandalf_workshop/tests/test_artisans.py` for "Hello, World" and generic tasks, handling of empty plans, and directory creation.
    *   Commenting out older, misaligned tests in `gandalf_workshop/tests/test_coder_agent.py` to ensure `make audit` passes, as the new tests in `test_artisans.py` are comprehensive for the current Coder agent implementation.
    *   Ensuring all linters (`flake8`, `black`) and type checks (`mypy`) pass by running `make audit`.
    *   Updating `docs/roadmap/V1.md` to mark `feature/V1-coder-agent-basic` as complete.
*   All these changes are staged for commit on the `feature/V1-coder-agent-basic` branch.
*   This `AGENTS.md` file was also updated.

**Next Steps & Focus Areas for the *Next* Jules Iteration:**

Based on `docs/roadmap/V1.md`, the following are high-priority areas:

1.  **`feature/V1-e2e-testing-framework`**: This is a critical next step now that basic Planner, Coder, and Auditor agents are in place.
    *   This involves setting up basic infrastructure and writing initial E2E tests.
    *   The "Hello, World" application generation described in `docs/roadmap/V1.md` is the primary E2E test case for V1. This will involve the Orchestrator, Planner, Coder, and Auditor.
    *   Focus on integrating these components and verifying the end-to-end flow.

2.  **`feature/V1-initial-documentation`**: Drafting initial user guides for setting up the development environment and running the V1 application. This can proceed in parallel or after the E2E framework is established.

**General Guidance for Next Iteration:**

*   **Follow Test-Driven Development (TDD):** For any new Python code, write tests first.
    *   Look at existing tests in `gandalf_workshop/tests/` for examples.
    *   Ensure `Makefile` targets like `test` and `lint` (via `make audit`) are used and pass.
*   **Adhere to `CONTRIBUTING.md`:** This file provides guidelines for development, including branch naming and updating roadmap files.
*   **Branching Strategy:**
    *   Create specific `feature/V1-*` branches for each component as outlined in `docs/roadmap/V1.md`.
    *   Merge completed features into `develop/V1` (once this integration branch is established and used - check if it exists, otherwise, merging to main after feature completion is the current implied practice based on roadmap).
*   **Small, Atomic Commits:** Keep commits focused on a single logical change.
*   **Consult Documentation:** The `docs/` folder is your primary reference. Use `docs/roadmap/V1.md` for V1 tasks and `docs/VERSION_ROADMAP.md` for the overall vision.
*   **AGENTS.md:** Always check for and adhere to instructions in any `AGENTS.md` files relevant to the files you are modifying (including this one!).

Good luck with the next V1 features!
