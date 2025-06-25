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

## Task: Implement Live LLM Agent Chain (For Jules)

Hello Jules,

Your next major task is to upgrade the Gandalf Workshop's V1 pipeline to use live LLM agents, replacing the current mock/placeholder implementations. This will involve a significant refactoring of the existing V1 workflow.

**Phase 1: Understanding and Initial Setup**

1.  **Read the Audit Report:** Begin by thoroughly reading the `AUDIT_V1.md` file in the repository. It details why the current V1 system does not use LLMs and should give you a clear picture of the components that need modification.
2.  **API Key Management:**
    *   You will need an OpenAI API key to complete this task. Assume the user will provide this to you when you request it, or that it can be set as an environment variable (e.g., `OPENAI_API_KEY`).
    *   Modify the code to securely access this API key (e.g., using `os.getenv("OPENAI_API_KEY")`). **Do not hardcode the API key.** Prompt the user for the key if it's not found in the environment.

**Phase 2: Implementing Live LLM Agents (Iterative Approach)**

Focus on replacing the mock V1 components one by one. We recommend using the `openai` library directly for initial simplicity, or `crewai` if you assess it to be straightforward for integrating the existing charter prompts.

1.  **Live Planner Agent:**
    *   Modify `gandalf_workshop/artisan_guildhall/artisans.py`:
        *   Update `initialize_planner_agent_v1` (or create a new `initialize_live_planner_agent`).
        *   This function should now instantiate an LLM client (e.g., `openai.OpenAI()`).
        *   It should use the `PLANNER_CHARTER_PROMPT` from `gandalf_workshop/artisan_guildhall/prompts.py` as the system message or main instruction for the LLM.
        *   The user's input prompt should be incorporated into the LLM call.
        *   The LLM's response, which should be a plan (ideally structured, perhaps YAML or JSON as hinted in `PLANNER_CHARTER_PROMPT`), needs to be parsed and returned as a `PlanOutput` object.
    *   Modify `gandalf_workshop/workshop_manager.py`:
        *   Ensure `run_v1_commission` calls your new live planner agent function.

2.  **Live Coder Agent:**
    *   Modify `gandalf_workshop/artisan_guildhall/artisans.py`:
        *   Create a new function `initialize_live_coder_agent`.
        *   This function should take the `PlanOutput` (from the live Planner) as input.
        *   It should instantiate an LLM client.
        *   It should use the `CODER_CHARTER_PROMPT` from `prompts.py`.
        *   The plan details should be formatted and passed to the LLM.
        *   The LLM's response should be the generated code.
        *   This code should be saved to a file (e.g., `generated_code.py` within the commission directory), and the path returned in a `CodeOutput` object.
    *   Modify `gandalf_workshop/workshop_manager.py`:
        *   Replace the inline mock Coder logic in `run_v1_commission` with a call to your new `initialize_live_coder_agent`.

3.  **Live Auditor Agent (Basic Syntax Check First, then LLM):**
    *   **Initial Step:** Modify `gandalf_workshop/workshop_manager.py` to call the existing `initialize_auditor_agent_v1` from `artisans.py` (which does a `py_compile` syntax check). This is better than the current inline mock auditor.
    *   **Future Enhancement (Optional for this task, but consider):** Create an `initialize_live_auditor_agent` in `artisans.py` that uses an LLM with `GENERAL_INSPECTOR_CHARTER_PROMPT` to perform a more semantic audit of the code from the live Coder Agent. For now, ensuring the syntax check auditor is called is sufficient.

**Phase 3: Testing and Refinement**

*   **Iterative Testing:** Test each agent as you make it live.
    *   Start with simple prompts (e.g., "create a python function that adds two numbers").
    *   Gradually increase complexity. Test the "Create a calculator app with a streamlit GUI" prompt.
*   **Error Handling:** Implement basic error handling for API calls (e.g., network issues, API errors).
*   **Output Parsing:** Be robust in parsing the outputs from LLMs. They might not always perfectly adhere to requested formats.
*   **Environment Variables:** Ensure your solution relies on `OPENAI_API_KEY` being set in the environment.

**General Guidelines:**

*   **Refer to Documentation:** The `docs/` directory, especially `technology_stack.md` and `communication_protocols.md`, contains the original design intent for using frameworks like CrewAI and AutoGen. While a direct implementation of that full stack might be too complex for one go, it provides good context. For this task, direct OpenAI API calls or a simple CrewAI setup for individual agents is acceptable.
*   **Adhere to Existing Data Models:** Use the `PlanOutput`, `CodeOutput`, `AuditOutput` data models defined in `gandalf_workshop/specs/data_models.py`.
*   **Keep Changes Focused:** Primarily modify `workshop_manager.py` and `artisans.py`. You may need to adjust `data_models.py` if the LLM outputs require different structuring that still fits the spirit of the existing models.
*   **Documentation:** Add comments to your new code explaining its logic. Update relevant docstrings.

Good luck, Jules! This is a challenging but important step in making Gandalf Workshop truly functional.
