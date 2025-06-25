# Jules Instructions

**Project:** Gandalf Workshop

**Meta-Instructions for Future Jules Iterations:**
*   **At the end of your assigned task, you MUST perform these steps:**
    1.  **Overwrite this file (`JULES_INSTRUCTIONS.md`)**: Do not create a new timestamped or uniquely named file. Always update this specific file.
    2.  **Summarize Your Accomplishments**: Briefly describe the task you just completed and the key changes you made or committed.
    3.  **Provide Clear Next Steps**: Based on the project's roadmap and your understanding of the current state, outline the most logical next task(s) for the subsequent Jules iteration.
    4.  **Include General Reminders**:
        *   Emphasize adherence to `CONTRIBUTING.md`.
        *   Point to the relevant roadmap document (e.g., `docs/roadmap/V1.md`, `docs/roadmap/V2.md`) for task identification.
        *   Remind to check alignment with the overall project vision (see `docs/VERSION_ROADMAP.md` and other strategic documents).
        *   Stress the importance of checking for and following instructions in any `AGENTS.md` files.
*   **Your goal is to ensure a smooth handover to the next Jules, providing all necessary context and direction.**

---

**Your Current State & Context (as of last update):**
*   You (the current Jules iteration) just successfully completed the task: `feature/V1-e2e-testing-framework: Set up the basic infrastructure and write initial E2E tests that cover the core application workflow.`
*   This involved:
    *   Creating a BDD feature file (`gandalf_workshop/tests/features/main_workflow_e2e.feature`) to define an E2E test for the main CLI workflow (`main.py`).
    *   Implementing the corresponding step definitions (`gandalf_workshop/tests/step_definitions/test_main_workflow_e2e_steps.py`) using `pytest-bdd` and `subprocess` to run and assert the CLI's output.
    *   Debugging an issue where `main.py` was not correctly calling the V1 `WorkshopManager` interface. This was fixed by updating `main.py` to instantiate `WorkshopManager` without arguments and to call its `run_v1_commission` method.
    *   Ensuring all tests (including the new E2E tests) pass via `pytest`.
    *   Ensuring the project's full audit script (`auditing/run_full_audit.sh`) passes.
*   All changes will be committed to the `feature/V1-e2e-testing-framework` branch.
*   The repository now has a basic E2E test that validates the primary CLI entry point and its interaction with the `WorkshopManager`.

**Next Steps & Focus Areas for the *Next* Jules Iteration:**

The V1 roadmap (`docs/roadmap/V1.md`) should continue to guide development. With the basic E2E test for the main workflow in place, the next steps should focus on building out the core agentic functionalities:

1.  **Establish `develop/V1` Branch (if not already done):**
    *   If it doesn't exist, create a `develop/V1` integration branch from the current `main` or an appropriate base. This branch will be where `feature/V1-*` branches are merged. (This was also a next step from the previous Jules, so verify its status).

2.  **Continue V1 Feature Implementation (Prioritize Core Workflow components):**
    *   **`feature/V1-orchestrator-loop`**: This remains fundamental. The `WorkshopManager`'s `run_v1_commission` method currently has a mock/linear execution. It needs to be developed into a more robust loop if the V1 design requires iterative processing or more complex state management between Planner, Coder, and Auditor.
        *   Refer to `gandalf_workshop/workshop_manager.py`.
        *   The current implementation in `run_v1_commission` is sequential. Review `docs/roadmap/V1.md` and `docs/1_strategic_overview/technology_stack.md` to confirm if a more complex loop (e.g., with retries or conditional paths based on agent output) is intended for V1 or if the current sequential call is sufficient.
    *   **`feature/V1-communication-protocol`**: Define and implement/refine the data structures for how agents (Planner, Coder, Auditor) pass information.
        *   Review `gandalf_workshop/specs/data_models.py`. The existing `PlanOutput`, `CodeOutput`, `AuditOutput` are good starts. Ensure they meet the needs of the V1 agents.
        *   Check `docs/2_operational_framework/communication_protocols.md` for guidance.
    *   **`feature/V1-planner-agent-basic`**: Enhance the `initialize_planner_agent_v1` function in `gandalf_workshop/artisan_guildhall/artisans.py`.
        *   Currently, it returns a very simple plan. It should be able to take a user prompt and produce a slightly more structured plan (e.g., a list of tasks that the Coder agent can understand).
        *   The `Planner` might need to interact with LLMs via `CrewAI` or `Langchain` as suggested in the tech stack, even for a basic V1 version.
    *   **`feature/V1-coder-agent-basic`**: Implement the Coder agent functionality.
        *   The `run_v1_commission` in `WorkshopManager` currently has mock coder logic. Replace this with a call to a `initialize_coder_agent_v1` (or similar) that takes the `PlanOutput` and generates actual code files.
        *   This agent will likely be a key area of development.
    *   **`feature/V1-auditor-agent-basic`**: Implement the Auditor agent functionality.
        *   Similar to the Coder, replace the mock auditor logic in `WorkshopManager` with a call to an Auditor agent that takes `CodeOutput` and performs a basic audit (e.g., linting, simple static analysis if planned for V1).

**General Guidance for Next Iteration:**

*   **Follow Test-Driven Development (TDD):** For any new Python code (orchestrator logic, agent functionality), write tests first.
    *   The new E2E test can serve as a high-level validation. Unit tests for individual agent functions and orchestrator logic are crucial.
    *   Look at existing tests in `gandalf_workshop/tests/` for examples.
    *   Ensure `Makefile` targets like `test` or `lint` (or the full `auditing/run_full_audit.sh`) are used and pass.
*   **Adhere to `CONTRIBUTING.md`:** This file should provide guidelines for development.
*   **Branching Strategy:**
    *   Create specific `feature/V1-*` branches for each component as outlined in `docs/roadmap/V1.md`.
    *   Merge completed features into `develop/V1`.
*   **Small, Atomic Commits:** Keep commits focused on a single logical change.
*   **Consult Documentation:** The `docs/` folder is crucial. Use it as a reference for architecture, agent roles, and the V1 plan (`docs/roadmap/V1.md`). Check the overall vision in `docs/VERSION_ROADMAP.md`.
*   **AGENTS.md:** Always check for and adhere to instructions in any `AGENTS.md` files relevant to the files you are modifying.

**If Ambiguity Arises:**
*   Refer to the detailed V1 roadmap (`docs/roadmap/V1.md`).
*   If the roadmap is unclear or a design decision is needed, use `request_user_input`.

Good luck with the continued V1 implementation!
