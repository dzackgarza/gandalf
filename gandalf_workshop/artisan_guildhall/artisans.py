"""
artisans.py - The Assembly Hall for Specialist Artisan Crews

This module provides functions to initialize and configure "Artisan Crews"
(specialized AI agent teams). It's like a workshop assembly hall where the
Workshop Manager briefs craftsmen (Planner, Coder, Inspector crews) before
they start a commission. Each function here would typically set up agents
(e.g., using CrewAI, AutoGen, LangGraph) with charters, tools, and context.
"""

import yaml
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from gandalf_workshop.specs.data_models import (
    PlanOutput,
    PMReview,
    PMReviewDecision,
    CodeOutput,
    AuditOutput,
    AuditStatus,
)
from .prompts import CODER_CHARTER_PROMPT # Import CODER_CHARTER_PROMPT

import py_compile
import tempfile # For safe auditing

# Placeholder for prompts if they were to be used by these V1 agents
# from .prompts import (PLANNER_CHARTER_PROMPT, CODER_CHARTER_PROMPT,
#                       GENERAL_INSPECTOR_CHARTER_PROMPT)

logger_artisans = logging.getLogger(__name__) # Using a module-level logger

# Metaphor: These functions are like the Workshop Manager's assistants who
# know how to quickly assemble Planners, Coders, or Inspectors, providing
# them with their official charters (prompts) and tools.

def initialize_planning_crew():
    """Placeholder for a more complex planning crew."""
    logger_artisans.info("Artisan Assembly: Planning Crew initialized (placeholder).")

def initialize_coding_crew():
    """Placeholder for a more complex coding crew."""
    logger_artisans.info("Artisan Assembly: Coding Crew initialized (placeholder).")

def initialize_inspection_crew():
    """Placeholder for a more complex inspection crew."""
    logger_artisans.info("Artisan Assembly: Inspection Crew initialized (placeholder).")


# V1 Basic Agents

def initialize_planner_agent_v1(user_prompt: str, commission_id: str) -> PlanOutput:
    """
    Initializes and runs a basic V1 Planner Agent.
    For V1, this is a simple function that returns a predefined plan.
    """
    logger_artisans.info(
        f"Artisan Assembly: V1 Basic Planner Agent activated for commission '{commission_id}'. "
        f"User Prompt (snippet): {user_prompt[:100]}..."
    )

    if "hello world" in user_prompt.lower():
        plan = PlanOutput(
            tasks=["Create a Python file that prints 'Hello, World!'"], details=None
        )
        logger_artisans.info("  V1 Planner: Generated 'Hello, World!' plan.")
    else:
        # For LLM Coder, make the task more explicit for the LLM
        plan = PlanOutput(
            tasks=[f"Generate Python code for the following task: {user_prompt}"], details=None
        )
        logger_artisans.info(f"  V1 Planner: Generated plan for LLM Coder: {user_prompt[:50]}...")
    return plan


def initialize_pm_review_crew(blueprint_path: Path, commission_id: str, blueprint_version: str ="1.0") -> Path:
    """
    Simulates the PM Review Crew analyzing a blueprint.
    """
    logger_artisans.info(
        f"Artisan Assembly: PM Review Crew activated for blueprint: {blueprint_path}"
    )
    try:
        with open(blueprint_path, "r", encoding="utf-8") as f:
            blueprint_content = yaml.safe_load(f)
        summary = blueprint_content.get("project_summary", "").lower()
        if "complex" in summary:
            decision = PMReviewDecision.REVISION_REQUESTED
            rationale = "Mock PM Review: Blueprint needs revision. Summary indicates complexity. Please simplify."
            suggested_focus_areas = ["project_summary", "product_specifications.modules"]
        elif "simple" in summary or "mvp" in summary:
            decision = PMReviewDecision.APPROVED
            rationale = "Mock PM Review: Blueprint approved. Summary indicates a simple or MVP scope."
            suggested_focus_areas = None
        else:
            decision = PMReviewDecision.REVISION_REQUESTED
            rationale = "Mock PM Review: Blueprint needs revision. Scope clarity needed."
            suggested_focus_areas = ["project_summary"]
    except Exception as e:
        logger_artisans.error(
            f"Mock PM Review: Error reading blueprint {blueprint_path}. Defaulting to REVISION_REQUESTED.",
            exc_info=True
        )
        decision = PMReviewDecision.REVISION_REQUESTED
        rationale = f"Mock PM Review: Error reading blueprint. Error: {e}"
        suggested_focus_areas = ["project_summary"]

    review_data = PMReview(
        commission_id=commission_id,
        blueprint_path=str(blueprint_path.resolve()),
        blueprint_version_reviewed=blueprint_version,
        review_timestamp=datetime.now(timezone.utc),
        pm_agent_id="Mock_PM_Agent_v0.1",
        decision=decision,
        rationale=rationale,
        suggested_focus_areas_for_revision=suggested_focus_areas,
    )
    reviews_dir = Path("gandalf_workshop/reviews") / commission_id
    reviews_dir.mkdir(parents=True, exist_ok=True)
    timestamp_str = review_data.review_timestamp.strftime("%Y%m%d_%H%M%S_%f")
    review_file_path = reviews_dir / f"pm_review_{timestamp_str}.json"
    with open(review_file_path, "w", encoding="utf-8") as f:
        f.write(review_data.model_dump_json(indent=2))
    logger_artisans.info(f"Artisan Assembly: PM Review Crew generated report: {review_file_path}")
    return review_file_path


def initialize_auditor_agent_v1(code_input: CodeOutput, commission_id: str) -> AuditOutput:
    """
    Initializes and runs a basic V1 Auditor Agent (syntax check).
    """
    logger_artisans.info(
        f"Artisan Assembly: V1 Basic Auditor Agent activated for commission '{commission_id}'. "
        f"Auditing: {code_input.code_path}"
    )
    if not code_input.code_path or not code_input.code_path.exists() or not code_input.code_path.is_file():
        err_msg = f"Audit Error: Code path '{code_input.code_path}' is invalid or file not found."
        logger_artisans.error(err_msg)
        return AuditOutput(status=AuditStatus.FAILURE, message=err_msg)

    try:
        with open(code_input.code_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        compile(source_code, str(code_input.code_path), 'exec')
        logger_artisans.info(f"  V1 Auditor: Syntax check PASSED for {code_input.code_path}.")
        return AuditOutput(status=AuditStatus.SUCCESS, message="Syntax OK.")
    except FileNotFoundError:
        logger_artisans.error(f"  Audit Error: Code file not found at {code_input.code_path} during read.")
        return AuditOutput(status=AuditStatus.FAILURE, message=f"Code file for audit not found during read: {code_input.code_path}")
    except SyntaxError as e:
        logger_artisans.warning(f"  V1 Auditor: Syntax check FAILED for {code_input.code_path}. Error: {e}")
        return AuditOutput(status=AuditStatus.FAILURE, message=f"Syntax error in {code_input.code_path.name}: {e.msg} (line {e.lineno})")
    except Exception as e:
        logger_artisans.error(f"  V1 Auditor: Unexpected error during audit of {code_input.code_path}. Error: {e}", exc_info=True)
        return AuditOutput(status=AuditStatus.FAILURE, message=f"Unexpected error during audit of {code_input.code_path.name}: {str(e)}")


def initialize_coder_agent_v1(
    plan_input: PlanOutput,
    commission_id: str,
    output_target_dir: Path,
    llm_config: Optional[Dict[str, Any]] = None,
) -> CodeOutput:
    """
    Initializes and runs a V1 Coder Agent.
    If llm_config is provided, it attempts to use the LLM for code generation.
    Otherwise, it falls back to placeholder logic.
    """
    logger_artisans.info(
        f"Artisan Assembly: V1 Coder Agent activated for commission '{commission_id}'."
    )

    output_target_dir.mkdir(parents=True, exist_ok=True)

    if not plan_input.tasks:
        logger_artisans.error("  Coder Error: No tasks found in the plan.")
        return CodeOutput(code_path=output_target_dir, message="Coder Error: No tasks found in plan.")

    task_description = plan_input.tasks[0] # Assuming the first task is the primary one.
    file_content: str = ""
    message: str = ""
    file_name = "app.py" # Default to app.py for LLM generated or complex tasks

    if llm_config and llm_config.get("client"):
        logger_artisans.info(f"  Coder Agent: Using LLM provider: {llm_config['provider_name']} for task: {task_description}")

        provider_name = llm_config['provider_name']
        client = llm_config['client']
        models = llm_config.get('models', [])
        selected_model_name = None

        # Select a suitable model
        if models:
            if provider_name == 'gemini':
                # Prefer modern, known-good models, then fall back more generally
                preferred_gemini_models = ['models/gemini-1.5-flash-latest', 'models/gemini-1.5-pro-latest', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro']
                selected_model_name = next((m for m in preferred_gemini_models if m in models), None)
                if not selected_model_name: # Fallback if preferred are not found
                    selected_model_name = next((m for m in models if 'flash' in m or 'pro' in m), None) # Broader search for flash/pro
                if not selected_model_name: # Last resort, pick first from the filtered list from LLMProviderManager
                     selected_model_name = models[0] if models else None
            elif provider_name == 'mistral':
                # Prefer more capable or recent models
                preferred_mistral_models = ['mistral-large-latest', 'codestral-latest', 'open-mixtral-8x22b', 'open-mixtral-8x7b']
                selected_model_name = next((m for m in preferred_mistral_models if m in models), None)
                if not selected_model_name: # Fallback
                    selected_model_name = next((m for m in models if 'large' in m or 'codestral' in m or 'mixtral' in m or 'small' in m), models[0] if models else None)
            elif provider_name == 'together_ai':
                 # For Together, model objects might be different, need to find names.
                 # This part might need adjustment based on actual model object structure from llm_provider_manager
                potential_models = [m for m in models if isinstance(m, str) and ('llama' in m or 'mixtral' in m or 'codellama' in m or 'deepseek' in m)]
                if potential_models:
                    selected_model_name = potential_models[0]
                elif models: # Fallback if no preferred keywords found
                    selected_model_name = models[0] if isinstance(models[0], str) else getattr(models[0], 'name', 'unknown_together_model')


            if not selected_model_name and models: # Fallback if no specific model found
                 selected_model_name = models[0] if isinstance(models[0], str) else getattr(models[0], 'name', 'unknown_model')


        if not selected_model_name:
            logger_artisans.error(f"  Coder Agent: No suitable model found for {provider_name}.")
            return CodeOutput(code_path=output_target_dir, message=f"Coder Error: No model found for {provider_name}.")

        logger_artisans.info(f"  Coder Agent: Selected model: {selected_model_name}")

        # Construct prompt using CODER_CHARTER_PROMPT and the task
        # For V1, we'll keep it simple: the charter acts as a system prompt, task is user prompt.
        # This assumes a chat-like interaction model for the LLM.

        # Simplified prompt for now, focusing on the task.
        # CODER_CHARTER_PROMPT is quite generic. We need to be specific about Python code.
        full_prompt = (
            f"{CODER_CHARTER_PROMPT}\n\n"
            f"Blueprint Task: Generate Python code for the following task: '{task_description}'.\n"
            "Ensure the output is only the Python code, without any explanatory text, "
            "markdown formatting, or ```python ... ``` blocks. Just the raw code."
        )

        try:
            if provider_name == 'gemini':
                model_instance = client.GenerativeModel(selected_model_name)
                response = model_instance.generate_content(full_prompt)
                file_content = response.text
            elif provider_name == 'mistral':
                from mistralai.models.chat_completion import ChatMessage
                messages = [ChatMessage(role="user", content=full_prompt)]
                chat_response = client.chat(model=selected_model_name, messages=messages)
                file_content = chat_response.choices[0].message.content
            elif provider_name == 'together_ai':
                # Together AI client might have a different chat completion method
                # Assuming client.chat.completions.create or similar for now
                # This is a common pattern but might need adjustment for 'together' library
                # For now, let's assume a simple completion endpoint if chat is not direct
                # The 'together' library's `client.completions.create` is for standard text completion.
                # For chat models, it's often `client.chat.completions.create`.
                # The `together` library's `Models.list()` returns model details that might include `type: 'chat'`.
                # We'll try a generic approach; if it fails, this part needs specific debugging.
                # The `llm_provider_manager` returns the `Together` client instance.
                # Let's try client.chat.completions.create if the model type suggests chat.
                # This part is speculative without running and testing the Together client structure directly.
                # Based on common patterns:
                # Check if model is chat type (this info might not be directly in llm_config['models'])
                # For simplicity, we'll assume it supports a completion-like interface.
                # This is a simplification and might need specific adapter logic for TogetherAI.
                # The `together run` command shows model names like `togethercomputer/llama-2-7b-chat`
                # The API expects a prompt string for completion models.
                # The client.models.list() returns ModelObject instances.
                # We'll try to use a generic completions endpoint if available, or simplify.
                # Forcing a simpler completion for now.
                # The `client.completions.create` is the most likely method.
                response = client.completions.create(
                    prompt=f"[INST] {full_prompt} [/INST]", # Common instruction format for some models
                    model=selected_model_name,
                    max_tokens=2048, # Arbitrary limit
                    stop=["```"] # Try to stop before markdown
                )
                if response and response.choices:
                    file_content = response.choices[0].text.strip()
                else:
                    raise Exception("Together AI response was empty or malformed.")

            # Clean up potential markdown code blocks if LLM doesn't respect the instruction
            if file_content.strip().startswith("```python"):
                file_content = file_content.split("```python\n", 1)[-1]
                if file_content.strip().endswith("```"):
                    file_content = file_content.rsplit("\n```", 1)[0]
            elif file_content.strip().startswith("```"):
                 file_content = file_content.split("```\n", 1)[-1]
                 if file_content.strip().endswith("```"):
                    file_content = file_content.rsplit("\n```", 1)[0]

            file_content = file_content.strip()

            if not file_content:
                raise Exception("LLM returned empty content.")

            message = f"LLM ({provider_name}/{selected_model_name}) generated code for task: {task_description[:50]}..."
            logger_artisans.info(f"  V1 Coder (LLM): Successfully generated code using {provider_name}/{selected_model_name}.")

        except Exception as e:
            logger_artisans.error(f"  Coder Agent: LLM call failed for {provider_name}. Error: {e}", exc_info=True)
            # Fallback to placeholder .py file if LLM fails
            file_name = "app_llm_failed.py" # Ensure .py extension
            file_content = (
                f"# LLM generation failed for task: {task_description}\n"
                f"# Error: {str(e)}\n"
                f"# Fallback content below (if any was planned)\n"
                f"print('Error: LLM code generation failed. See comments in this file.')\n"
            )
            message = f"LLM generation failed, created placeholder Python file. Error: {e}"
    else:
        logger_artisans.warning("  Coder Agent: No LLM configuration provided. Using placeholder logic.")
        if "Create a Python file that prints 'Hello, World!'" in task_description:
            file_name = "main.py" # Still main.py for this specific placeholder
            file_content = 'print("Hello, World!")\n'
            message = f"Successfully created {file_name} for 'Hello, World!' task (placeholder)."
            logger_artisans.info(f"  V1 Coder (placeholder): Creating '{file_name}' for Hello World.")
        else:
            file_name = "task_output.txt"
            file_content = f"Task from plan (no LLM):\n{task_description}\n"
            message = f"Successfully created {file_name} for generic task (placeholder)."
            logger_artisans.info(
                f"  V1 Coder (placeholder): Creating '{file_name}' for generic task: {task_description[:50]}..."
            )

    file_path = output_target_dir / file_name
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)
        logger_artisans.info(f"  V1 Coder: Successfully wrote to {file_path}")
        return CodeOutput(code_path=file_path, message=message)
    except IOError as e:
        logger_artisans.error(f"  Coder Error: Could not write to file {file_path}. Error: {e}", exc_info=True)
        return CodeOutput(code_path=output_target_dir, message=f"Coder Error: Could not write to file {file_path}. Error: {e}")
