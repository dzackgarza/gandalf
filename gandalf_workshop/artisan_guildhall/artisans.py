"""
artisans.py - The Assembly Hall for Specialist Artisan Crews

This module provides functions to initialize and configure "Artisan Crews"
(specialized AI agent teams). It's like a workshop assembly hall where the
Workshop Manager briefs craftsmen (Planner, Coder, Inspector crews) before
they start a commission. Each function here would typically set up agents
(e.g., using CrewAI, AutoGen, LangGraph) with charters, tools, and context.
"""

import os # Import os
import yaml
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import google.generativeai as genai # Import genai

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
# Metaphor: These functions are like the Workshop Manager's assistants who
# know how to quickly assemble Planners, Coders, or Inspectors, providing
# them with their official charters (prompts) and tools.


def _get_gemini_api_key() -> str:
    """
    Retrieves the Gemini API key from the environment variable GEMINI_API_KEY.

    Raises:
        ValueError: If the GEMINI_API_KEY environment variable is not set.

    Returns:
        The Gemini API key.
    """
    # api_key = os.getenv("GEMINI_API_KEY")
    # if not api_key:
    #     raise ValueError(
    #         "GEMINI_API_KEY environment variable not set. "
    #         "Please set it before running the live agents."
    #     )
    # return api_key
    # api_key = os.getenv("GEMINI_API_KEY")
    # if not api_key:
    #     raise ValueError(
    #         "GEMINI_API_KEY environment variable not set. "
    #         "Please set it before running the live agents."
    #     )
    # return api_key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Please set it before running the live agents."
        )
    return api_key


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


def initialize_live_planner_agent(user_prompt: str, commission_id: str, llm_config: Optional[Dict[str, Any]] = None) -> PlanOutput:
    """
    Initializes and runs a live LLM-based Planner Agent using the configured LLM provider.

    Args:
        user_prompt: The initial request from the client.
        commission_id: A unique ID for this commission.

    Returns:
        A PlanOutput object.
    """
    logger = logging.getLogger(__name__)
    logger.info(
        f"Artisan Assembly: Live Planner Agent activated for commission '{commission_id}'."
    )
    logger.info(f"  User Prompt: {user_prompt[:100]}...")

    if not llm_config or not llm_config.get("client"):
        logger.error("  Live Planner: LLM configuration not provided or client missing.")
        return PlanOutput(tasks=["Error: LLM not configured for planner."], details=None)

    provider_name = llm_config["provider_name"]
    client = llm_config["client"]
    # Choose a model - for simplicity, using the first available model.
    # More sophisticated selection logic could be added here based on model capabilities.
    selected_model_name = llm_config["models"][0] if llm_config.get("models") else None

    if not selected_model_name:
        logger.error(f"  Live Planner: No models found in LLM configuration for provider {provider_name}.")
        return PlanOutput(tasks=[f"Error: No models available for {provider_name} in planner."], details=None)

    logger.info(f"  Live Planner: Using {provider_name} with model {selected_model_name}.")

    try:
        from .prompts import PLANNER_CHARTER_PROMPT

        # For Gemini, the prompt needs to be structured carefully.
        # We'll combine the charter prompt and user prompt.
        # System-level instructions are often part of the initial user message turn for some models.
        # Or passed via specific generation_config or system_instruction parameters if available.
        # For gemini-pro, we pass it as part of the history or as a single block.
        # Let's try a combined prompt approach.

        full_prompt = f"{PLANNER_CHARTER_PROMPT}\n\nUser Request:\n{user_prompt}"
        raw_plan = ""

        if provider_name == "gemini":
            # client is genai module itself, model is selected_model_name (string)
            model_instance = client.GenerativeModel(selected_model_name)
            response = model_instance.generate_content(full_prompt)
            raw_plan = response.text
        elif provider_name == "mistral":
            # client is MistralClient instance
            messages = [{"role": "user", "content": full_prompt}] # Use dict for messages
            # TODO: Select a suitable model from llm_config['models'] for mistral
            # For now, using the first one.
            chat_response = client.chat_completions.create(model=selected_model_name, messages=messages) # Corrected call
            raw_plan = chat_response.choices[0].message.content
        elif provider_name == "together_ai":
            # client is Together instance
            # TODO: Select a suitable model and adapt prompt format if needed
            # Using a simple completion for now, might need chat completion format.
            # The prompt format "[INST] {prompt} [/INST]" is common for instruction-tuned models.
            together_prompt = f"[INST] {full_prompt} [/INST]"
            response = client.completions.create(
                prompt=together_prompt,
                model=selected_model_name,
                max_tokens=1024, # Arbitrary limit
                stop=["[/INST]", "</s>"] # Common stop tokens
            )
            if response and response.choices:
                raw_plan = response.choices[0].text.strip()
            else:
                raise Exception("Together AI response was empty or malformed.")
        else:
            logger.error(f"  Live Planner: Provider {provider_name} not supported for LLM call.")
            return PlanOutput(tasks=[f"Error: Planner provider {provider_name} not supported."], details=None)

        logger.info(f"  Live Planner: Raw LLM response: {raw_plan[:200]}...")

        # Attempt to parse as YAML or JSON, otherwise treat as a single task
        # For simplicity in this iteration, we'll treat the entire response as a task list.
        # A more robust solution would involve more sophisticated parsing.
        if raw_plan:
            # Assuming the plan is a list of tasks, one per line, or a block of text.
            # We'll split by newline and filter out empty lines.
            tasks = [task.strip() for task in raw_plan.split('\n') if task.strip()]
            if not tasks: # If splitting by newline results in empty, use the whole raw_plan
                tasks = [raw_plan.strip()]
            plan = PlanOutput(tasks=tasks, details={"raw_response": raw_plan})
            logger.info(f"  Live Planner: Parsed tasks: {tasks}")
        else:
            logger.warning("  Live Planner: LLM returned an empty plan.")
            plan = PlanOutput(tasks=["Error: LLM returned empty plan."], details={"raw_response": raw_plan})

    except Exception as e: # General exception for Gemini API errors or other issues
        logger.error(f"  Live Planner: Exception caught: {type(e).__name__} - {str(e)}", exc_info=True)
        # Explicitly define plan within the except block using str(e)
        plan = PlanOutput(tasks=[f"Error during planning: {type(e).__name__} - {str(e)}"], details=None)
        return plan # Return immediately from except block

    # This line should ideally not be reached if an exception occurs and is handled above.
    # If plan was not defined in try (e.g. an early error before plan assignment),
    # and exception was NOT caught, then plan would be unbound here.
    # However, the UnboundLocalError for 'e' was the primary concern from the traceback.
    return plan # Assuming plan was successfully defined in the try block


def initialize_live_auditor_agent(
    generated_code: str,
    plan_input: PlanOutput,
    commission_id: str,
    llm_config: Optional[Dict[str, Any]] = None, # Added llm_config
) -> AuditOutput:
    """
    Initializes and runs a live LLM-based Auditor Agent using the configured LLM provider.
    This agent performs a semantic audit of the code against the plan.

    Args:
        generated_code: The string content of the code to be audited.
        plan_input: A PlanOutput object containing the tasks the code should implement.
        commission_id: A unique ID for this commission (for context/logging).
        llm_config: Configuration for the LLM provider.

    Returns:
        An AuditOutput object.
    """
    logger = logging.getLogger(__name__)
    logger.info(
        f"Artisan Assembly: Live Auditor Agent activated for commission '{commission_id}'."
    )
    logger.info(f"  Auditing code snippet (first 200 chars): {generated_code[:200]}...")
    logger.info(f"  Against plan tasks: {plan_input.tasks}")

    if not llm_config or not llm_config.get("client"):
        logger.error("  Live Auditor: LLM configuration not provided or client missing.")
        return AuditOutput(status=AuditStatus.FAILURE, message="Auditor Error: LLM not configured.")

    provider_name = llm_config["provider_name"]
    client = llm_config["client"]
    selected_model_name = llm_config["models"][0] if llm_config.get("models") else None

    if not selected_model_name:
        logger.error(f"  Live Auditor: No models found in LLM configuration for provider {provider_name}.")
        return AuditOutput(status=AuditStatus.FAILURE, message=f"Auditor Error: No models available for {provider_name}.")

    logger.info(f"  Live Auditor: Using {provider_name} with model {selected_model_name}.")

    try:
        from .prompts import GENERAL_INSPECTOR_CHARTER_PROMPT

        formatted_plan = "\n".join(
            f"- {task}" for task in plan_input.tasks
        )

        # Simplified prompt for PASS/FAIL and summary
        audit_request_prompt = f"""{GENERAL_INSPECTOR_CHARTER_PROMPT}

Your task is to review the following Python code based on the provided plan.

**Plan:**
{formatted_plan}

**Code to Review:**
```python
{generated_code}
```

**Instructions:**
1.  Determine if the code successfully and correctly implements all aspects of the plan.
2.  Identify any bugs, deviations from the plan, or critical issues.
3.  Provide a concise summary of your findings.
4.  Conclude your response with a single line containing ONLY "AUDIT_RESULT: PASS" if the code meets the plan's requirements and is functionally sound, or "AUDIT_RESULT: FAIL" if there are significant issues or deviations.

Example Response Format:
The code generally implements the feature for adding two numbers. However, it lacks error handling for non-numeric inputs as implicitly required by a robust function.
AUDIT_RESULT: FAIL
"""
        llm_response_text = ""

        if provider_name == "gemini":
            model_instance = client.GenerativeModel(selected_model_name)
            response = model_instance.generate_content(audit_request_prompt)
            llm_response_text = response.text
        elif provider_name == "mistral":
            messages = [{"role": "user", "content": audit_request_prompt}] # Use dict for messages
            chat_response = client.chat_completions.create(model=selected_model_name, messages=messages) # Corrected call
            llm_response_text = chat_response.choices[0].message.content
        elif provider_name == "together_ai":
            together_prompt = f"[INST] {audit_request_prompt} [/INST]"
            response = client.completions.create(
                prompt=together_prompt,
                model=selected_model_name,
                max_tokens=1024,
                stop=["[/INST]", "</s>"]
            )
            if response and response.choices:
                llm_response_text = response.choices[0].text.strip()
            else:
                raise Exception("Together AI response was empty or malformed.")
        else:
            logger.error(f"  Live Auditor: Provider {provider_name} not supported for LLM call.")
            return AuditOutput(status=AuditStatus.FAILURE, message=f"Auditor Error: Provider {provider_name} not supported.")

        logger.info(f"  Live Auditor: Raw LLM response: {llm_response_text[:300]}...")

        # Parse the response
        audit_status = AuditStatus.FAILURE # Default to failure
        audit_message = "Live Auditor: Could not determine audit outcome from LLM response."

        if llm_response_text:
            lines = llm_response_text.strip().split('\n')
            result_line = ""
            for line in reversed(lines): # Check from the end for the result line
                if line.startswith("AUDIT_RESULT:"):
                    result_line = line.strip()
                    break

            if "AUDIT_RESULT: PASS" in result_line:
                audit_status = AuditStatus.SUCCESS
                audit_message = llm_response_text.replace(result_line, "").strip()
                logger.info("  Live Auditor: Parsed result - PASS")
            elif "AUDIT_RESULT: FAIL" in result_line:
                audit_status = AuditStatus.FAILURE
                audit_message = llm_response_text.replace(result_line, "").strip()
                logger.info("  Live Auditor: Parsed result - FAIL")
            else:
                # If specific line not found, use the whole text but still mark as failure
                # as the format wasn't followed.
                audit_message = f"Live Auditor: LLM response did not contain clear PASS/FAIL line. Response: {llm_response_text}"
                logger.warning(f"  Live Auditor: Could not parse specific AUDIT_RESULT line. Full response: {llm_response_text}")
        else:
            audit_message = "Live Auditor: LLM returned an empty response."
            logger.warning(audit_message)


        return AuditOutput(
            status=audit_status,
            message=audit_message,
            report_path=None # No separate report file for now
        )

    except Exception as e:
        logger.error(f"  Live Auditor: Exception caught: {type(e).__name__} - {str(e)}", exc_info=True)
        return AuditOutput(
            status=AuditStatus.FAILURE,
            message=f"Live Auditor Error: Exception - {type(e).__name__} - {str(e)}",
            report_path=None
        )


def initialize_live_coder_agent(
    plan_input: PlanOutput,
    commission_id: str,
    output_target_dir: Path,
    llm_config: Optional[Dict[str, Any]] = None, # Added llm_config
) -> CodeOutput:
    """
    Initializes and runs a live LLM-based Coder Agent using the configured LLM provider.

    Args:
        plan_input: A PlanOutput object containing the tasks.
        commission_id: A unique ID for this commission (for context/logging).
        output_target_dir: The specific directory where the generated code file
                           should be saved.

    Returns:
        A CodeOutput object.
    """
    logger = logging.getLogger(__name__)
    logger.info(
        f"Artisan Assembly: Live Coder Agent activated for commission '{commission_id}'."
    )
    logger.info(f"  Plan tasks: {plan_input.tasks}")
    logger.info(f"  Output target directory: {output_target_dir}")

    output_target_dir.mkdir(parents=True, exist_ok=True)

    if not llm_config or not llm_config.get("client"):
        logger.error("  Live Coder: LLM configuration not provided or client missing.")
        # Return CodeOutput with the directory path and an error message
        return CodeOutput(code_path=output_target_dir, message="Coder Error: LLM not configured for coder.")

    provider_name = llm_config["provider_name"]
    client = llm_config["client"]
    selected_model_name = llm_config["models"][0] if llm_config.get("models") else None

    if not selected_model_name:
        logger.error(f"  Live Coder: No models found in LLM configuration for provider {provider_name}.")
        return CodeOutput(code_path=output_target_dir, message=f"Coder Error: No models available for {provider_name} in coder.")

    logger.info(f"  Live Coder: Using {provider_name} with model {selected_model_name}.")

    try:
        from .prompts import CODER_CHARTER_PROMPT

        formatted_plan = "\n".join(
            f"- {task}" for task in plan_input.tasks
        )
        full_prompt = f"{CODER_CHARTER_PROMPT}\n\nUser Request (Plan):\n{formatted_plan}\n\nPlease provide only the Python code as a direct response. Do not include any markdown formatting like ```python ... ```."

        generated_code = ""

        if provider_name == "gemini":
            model_instance = client.GenerativeModel(selected_model_name)
            response = model_instance.generate_content(full_prompt)
            generated_code = response.text
        elif provider_name == "mistral":
            messages = [{"role": "user", "content": full_prompt}] # Use dict for messages
            chat_response = client.chat_completions.create(model=selected_model_name, messages=messages) # Corrected call
            generated_code = chat_response.choices[0].message.content
        elif provider_name == "together_ai":
            together_prompt = f"[INST] {full_prompt} [/INST]"
            response = client.completions.create(
                prompt=together_prompt,
                model=selected_model_name,
                max_tokens=2048, # Increased max_tokens for code
                stop=["[/INST]", "</s>", "```"] # Added ``` as a stop token
            )
            if response and response.choices:
                generated_code = response.choices[0].text.strip()
            else:
                raise Exception("Together AI response was empty or malformed.")
        else:
            logger.error(f"  Live Coder: Provider {provider_name} not supported for LLM call.")
            return CodeOutput(code_path=output_target_dir, message=f"Coder Error: Provider {provider_name} not supported.")

        logger.info(f"  Live Coder: Raw LLM response: {generated_code[:200]}...")

        if not generated_code:
            logger.warning("  Live Coder: LLM returned empty code.")
            return CodeOutput(
                code_path=output_target_dir, # Return dir path on error
                message="Coder Error: LLM returned empty code."
            )

        # Clean up common markdown code block fences if present
        if generated_code.strip().startswith("```python"):
            generated_code = generated_code.split("```python\n", 1)[1]
            if generated_code.strip().endswith("```"):
                 generated_code = generated_code.rsplit("\n```", 1)[0]
        elif generated_code.strip().startswith("```"):
            generated_code = generated_code.split("```\n", 1)[1]
            if generated_code.strip().endswith("```"):
                generated_code = generated_code.rsplit("\n```", 1)[0]


        file_name = "generated_code.py"
        file_path = output_target_dir / file_name

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(generated_code)

        logger.info(f"  Live Coder: Successfully wrote code to {file_path}")
        return CodeOutput(code_path=file_path, message=f"Successfully generated code to {file_path}")

    except Exception as e: # General exception for Gemini API errors or other issues
        # Specific Gemini error types can be caught here if known, e.g., google.api_core.exceptions.
        # This also catches ValueError for API key issues and IOError for file issues.
        logger.error(f"  Live Coder: Gemini API error or other exception: {e}", exc_info=True)
        return CodeOutput(code_path=output_target_dir, message=f"Coder Error: Gemini API or other error - {e}")


def initialize_pm_review_crew(blueprint_path, commission_id, blueprint_version="1.0"):
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
