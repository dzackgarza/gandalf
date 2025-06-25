# Audit Report: LLM Usage in Gandalf Workshop V1 Pipeline

**Date:** 2024-07-17
**Auditor:** Jules (AI Assistant)
**Subject:** Investigation into why the V1 pipeline of the Gandalf Workshop (`main.py`) does not use live LLM agents or produce functional code for complex prompts (e.g., "Create a calculator app with a streamlit GUI").

## 1. Executive Summary

The Gandalf Workshop's V1 pipeline, when invoked via `main.py`, does **not** utilize live Large Language Model (LLM) agents for its core tasks of planning, code generation, or auditing. The observed behavior of producing placeholder output instead of functional code is by design in this V1 iteration. The system relies on hardcoded logic and mock components that simulate an agentic workflow without actual AI-driven task execution. While the project includes LLM libraries and detailed prompts for future use, these are not active in the V1 workflow.

## 2. Methodology

The audit involved:
*   Executing `main.py` with the prompt: "Create a calculator app with a streamlit GUI".
*   Analyzing the script's output and generated files.
*   Reviewing the source code of relevant Python modules:
    *   `main.py`
    *   `gandalf_workshop/workshop_manager.py`
    *   `gandalf_workshop/artisan_guildhall/artisans.py`
    *   `gandalf_workshop/artisan_guildhall/prompts.py`
*   Checking project dependencies (`requirements.txt`).
*   Searching the codebase for LLM-related keywords and configurations.

## 3. Key Findings

### 3.1. V1 Workflow Uses Mock/Placeholder Logic
The primary reason for the lack of LLM usage and functional code output is that the V1 workflow implemented in `WorkshopManager.run_v1_commission` is a mock or placeholder:

*   **Planner Agent (`initialize_planner_agent_v1`):**
    *   This function is called but uses hardcoded conditional logic based on keywords in the user prompt (e.g., "hello world").
    *   For other prompts, like the calculator app request, it generates a generic, non-LLM-derived plan string (e.g., "Task 1: Implement feature based on: [user_prompt]").
*   **Coder Agent (Mocked within `WorkshopManager`):**
    *   `WorkshopManager.run_v1_commission` contains inlined mock logic for the Coder step, explicitly bypassing any potential external Coder agent function.
    *   This mock logic writes a placeholder `output.txt` file for any plan not matching the hardcoded "Hello, World!" scenario. This directly explains the generic output observed for the calculator prompt.
*   **Auditor Agent (Mocked within `WorkshopManager`):**
    *   Similar to the Coder, the Auditor step is also an inlined mock within `WorkshopManager`.
    *   It reports a generic `AuditStatus.SUCCESS` for the placeholder content, which is misleading as no actual validation against the user's request occurs.

### 3.2. LLM Prompts and Frameworks Are Intended but Not Used in V1
*   **Detailed Prompts Exist:** The file `gandalf_workshop/artisan_guildhall/prompts.py` contains comprehensive "charter prompts" (e.g., `PLANNER_CHARTER_PROMPT`, `CODER_CHARTER_PROMPT`) suitable for guiding LLM agents.
*   **Prompts Bypassed:** These detailed prompts are **not** used by the active V1 agent functions or the mock logic in `WorkshopManager`.
*   **LLM Framework Placeholders:** `artisans.py` includes commented-out code and import statements (e.g., for `crewai`) indicating a design for future integration with LLM agent frameworks. This is not implemented in the V1 workflow.

### 3.3. LLM Libraries Installed but Dormant
*   The project's `requirements.txt` correctly lists and installs LLM interaction libraries such as `openai`, `crewai`, and `langchain`.
*   However, these libraries are not invoked by the V1 workflow for planning, coding, or auditing tasks.

## 4. Conclusion

The Gandalf Workshop's V1 pipeline is currently a scaffold that simulates an agentic workflow without actual LLM-driven capabilities. The system is architected with a clear intent for future LLM integration, as evidenced by the presence of detailed prompts, placeholder LLM framework code, and necessary libraries. However, the V1 execution path deliberately uses hardcoded logic and mock components, resulting in placeholder outputs for non-trivial user requests.

To enable LLM-driven code generation, the `WorkshopManager` and `artisans.py` modules would need to be updated to:
1.  Initialize and use actual LLM clients (e.g., OpenAI).
2.  Pass the defined charter prompts from `prompts.py` to these LLM clients/agents.
3.  Process the LLM responses to generate plans, code, and audit reports.
4.  Potentially implement the more sophisticated agent crew structures hinted at in `artisans.py` using frameworks like CrewAI.
