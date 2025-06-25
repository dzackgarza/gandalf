"""
artisans.py - The Assembly Hall for Specialist Artisan Crews

This module provides functions to initialize and configure "Artisan Crews"
(specialized AI agent teams). It's like a workshop assembly hall where the
Workshop Manager briefs craftsmen (Planner, Coder, Inspector crews) before
they start a commission. Each function here would typically set up agents
(e.g., using CrewAI, AutoGen, LangGraph) with charters, tools, and context.
"""

import os
import yaml
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import google.generativeai as genai
import re # Ensure re is imported

from gandalf_workshop.specs.data_models import (
    PlanOutput,
    PMReview,
    PMReviewDecision,
    CodeOutput,
    AuditOutput,
    AuditStatus,
)
# Import the default and alternative charters
from .prompts import CODER_CHARTER_PROMPT, CODER_CHARTER_PROMPT_ALT_1, ORACLE_ASSISTANCE_PROMPT, HELP_EXAMPLE_EXTRACTOR_PROMPT

import py_compile
import json # For parsing JSON output from help extractor
import tempfile # For safe auditing

logger_artisans = logging.getLogger(__name__)

def _get_gemini_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Please set it before running the live agents."
        )
    return api_key

def initialize_planning_crew():
    logger_artisans.info("Artisan Assembly: Planning Crew initialized (placeholder).")

def initialize_coding_crew():
    logger_artisans.info("Artisan Assembly: Coding Crew initialized (placeholder).")

def initialize_inspection_crew():
    logger_artisans.info("Artisan Assembly: Inspection Crew initialized (placeholder).")

def initialize_planner_agent_v1(user_prompt: str, commission_id: str) -> PlanOutput:
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
        plan = PlanOutput(
            tasks=[f"Generate Python code for the following task: {user_prompt}"], details=None
        )
        logger_artisans.info(f"  V1 Planner: Generated plan for LLM Coder: {user_prompt[:50]}...")
    return plan

def initialize_live_planner_agent(user_prompt: str, commission_id: str, llm_config: Optional[Dict[str, Any]] = None) -> PlanOutput:
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
    selected_model_name = llm_config["models"][0] if llm_config.get("models") else None
    temperature = llm_config.get("temperature") # Define temperature

    if not selected_model_name:
        logger.error(f"  Live Planner: No models found in LLM configuration for provider {provider_name}.")
        return PlanOutput(tasks=[f"Error: No models available for {provider_name} in planner."], details=None)

    logger.info(f"  Live Planner: Using {provider_name} with model {selected_model_name}.")

    try:
        from .prompts import PLANNER_CHARTER_PROMPT # New prompt
        # Replace placeholder in the new PLANNER_CHARTER_PROMPT
        full_prompt = PLANNER_CHARTER_PROMPT.replace("{user_request_placeholder}", user_prompt)
        raw_plan = ""

        # ... (LLM call logic remains the same for Gemini, Mistral, TogetherAI) ...
        # Current LLM call logic:
        if provider_name == "gemini":
            model_instance = client.GenerativeModel(selected_model_name)
            gen_config_args = {}
            if temperature is not None:
                gen_config_args["temperature"] = temperature
            response = model_instance.generate_content(full_prompt, generation_config=genai.types.GenerationConfig(**gen_config_args) if gen_config_args else None)
            raw_plan = response.text
        elif provider_name == "mistral":
            messages = [{"role": "user", "content": full_prompt}]
            mistral_params = {"model": selected_model_name, "messages": messages}
            if temperature is not None:
                mistral_params["temperature"] = temperature
            chat_response = client.chat.complete(**mistral_params)
            raw_plan = chat_response.choices[0].message.content
        elif provider_name == "together_ai":
            together_params = {
                "prompt": full_prompt,
                "model": selected_model_name,
                "max_tokens": 1024,
                "stop": ["</s>"]
            }
            if temperature is not None:
                together_params["temperature"] = temperature
            response = client.completions.create(**together_params)
            if response and response.choices:
                raw_plan = response.choices[0].text.strip()
            else:
                raise Exception("Together AI response was empty or malformed.")
        else:
            logger.error(f"  Live Planner: Provider {provider_name} not supported for LLM call.")
            return PlanOutput(tasks=[f"Error: Planner provider {provider_name} not supported."], details=None)


        logger.info(f"  Live Planner: Raw LLM response: {raw_plan[:200]}...")
        if raw_plan:
            # Parsing logic: split by newline, remove empty lines, strip whitespace.
            # This aligns with the new PLANNER_CHARTER_PROMPT's output format.
            tasks = [task.strip() for task in raw_plan.split('\n') if task.strip() and not task.startswith("User Request:")]
            # Filter out potential re-echoing of the "Your Task List:" header if the LLM includes it
            tasks = [task for task in tasks if task.lower() != "your task list:"]

            if not tasks: # If splitting by newline yields nothing, maybe the LLM returned one line.
                tasks = [raw_plan.strip()]
            plan = PlanOutput(tasks=tasks, details={"raw_response": raw_plan})
            logger.info(f"  Live Planner: Parsed tasks: {tasks}")
        else:
            logger.warning("  Live Planner: LLM returned an empty plan.")
            plan = PlanOutput(tasks=["Error: LLM returned empty plan."], details={"raw_response": raw_plan})
    except Exception as e:
        logger.error(f"  Live Planner: Exception caught: {type(e).__name__} - {str(e)}", exc_info=True)
        plan = PlanOutput(tasks=[f"Error during planning: {type(e).__name__} - {str(e)}"], details=None)
        return plan
    return plan

def initialize_live_auditor_agent(
    generated_code: str, plan_input: PlanOutput, commission_id: str, llm_config: Optional[Dict[str, Any]] = None
) -> AuditOutput:
    logger = logging.getLogger(__name__)
    logger.info(f"Artisan Assembly: Live Auditor Agent activated for commission '{commission_id}'.")
    if not llm_config or not llm_config.get("client"):
        logger.error("  Live Auditor: LLM configuration not provided or client missing.")
        return AuditOutput(status=AuditStatus.FAILURE, message="Auditor Error: LLM not configured.")

    provider_name = llm_config["provider_name"]
    client = llm_config["client"]
    selected_model_name = llm_config["models"][0] if llm_config.get("models") else None

    if not selected_model_name:
        logger.error(f"  Live Auditor: No models found for provider {provider_name}.")
        return AuditOutput(status=AuditStatus.FAILURE, message=f"Auditor Error: No models for {provider_name}.")

    logger.info(f"  Live Auditor: Using {provider_name} with model {selected_model_name}.")

    try:
        from .prompts import GENERAL_INSPECTOR_CHARTER_PROMPT
        formatted_plan = "\n".join(f"- {task}" for task in plan_input.tasks)
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
            messages = [{"role": "user", "content": audit_request_prompt}]
            chat_response = client.chat.complete(model=selected_model_name, messages=messages)
            llm_response_text = chat_response.choices[0].message.content
        elif provider_name == "together_ai":
            together_prompt = f"[INST] {audit_request_prompt} [/INST]"
            response = client.completions.create(
                prompt=together_prompt, model=selected_model_name, max_tokens=1024, stop=["[/INST]", "</s>"]
            )
            if response and response.choices:
                llm_response_text = response.choices[0].text.strip()
            else:
                raise Exception("Together AI response was empty or malformed.")
        else:
            logger.error(f"  Live Auditor: Provider {provider_name} not supported.")
            return AuditOutput(status=AuditStatus.FAILURE, message=f"Auditor Error: Provider {provider_name} not supported.")

        logger.info(f"  Live Auditor: Raw LLM response (first 300): {llm_response_text[:300]}...")
        audit_status = AuditStatus.FAILURE
        audit_message = "Live Auditor: Could not determine audit outcome from LLM response."

        if llm_response_text:
            lines = llm_response_text.strip().split('\n')
            result_line = ""
            for line in reversed(lines):
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
                audit_message = f"Live Auditor: LLM response did not contain clear PASS/FAIL. Response: {llm_response_text}"
                logger.warning(f"  Live Auditor: Could not parse AUDIT_RESULT line. Full response: {llm_response_text}")
        else:
            audit_message = "Live Auditor: LLM returned an empty response."
            logger.warning(audit_message)
        return AuditOutput(status=audit_status, message=audit_message, report_path=None)
    except Exception as e:
        logger.error(f"  Live Auditor: Exception: {type(e).__name__} - {str(e)}", exc_info=True)
        return AuditOutput(status=AuditStatus.FAILURE, message=f"Live Auditor Error: {type(e).__name__} - {str(e)}", report_path=None)

def initialize_live_coder_agent(
    plan_input: PlanOutput,
    commission_id: str,
    output_target_dir_base: Path,
    llm_config: Optional[Dict[str, Any]] = None,
    prompt_charter_override: Optional[str] = None # New argument
) -> CodeOutput:
    logger = logging.getLogger(__name__)
    logger.info(f"Artisan Assembly: Live Coder Agent activated for commission '{commission_id}'.")

    # Create the timestamped directory
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    # output_target_dir_base is outputs/<unique_id>
    # final_output_dir will be outputs/<unique_id>/<timestamp>
    final_output_dir = output_target_dir_base / timestamp_str
    final_output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"  Live Coder: Output directory set to {final_output_dir}")

    if not llm_config or not llm_config.get("client"):
        logger.error("  Live Coder: LLM configuration not provided or client missing.")
        # Return CodeOutput with the base directory path if LLM is not configured,
        # as a file won't be created.
        return CodeOutput(code_path=final_output_dir, message="Coder Error: LLM not configured for coder.")

    provider_name = llm_config["provider_name"]
    client = llm_config["client"]
    selected_model_name = llm_config["models"][0] if llm_config.get("models") else None

    if not selected_model_name:
        logger.error(f"  Live Coder: No models found for provider {provider_name}.")
        return CodeOutput(code_path=final_output_dir, message=f"Coder Error: No models for {provider_name}.")

    logger.info(f"  Live Coder: Using {provider_name} with model {selected_model_name}.")

    max_retries = 3
    for attempt in range(max_retries):
        logger.info(f"  Live Coder: Attempt {attempt + 1} of {max_retries} to generate and validate code.")
        try:
            from .prompts import CODER_CHARTER_PROMPT
            formatted_plan = "\n".join(f"- {task}" for task in plan_input.tasks)
            # Added instruction to avoid markdown for TogetherAI specifically, good general practice
            full_prompt = (
                f"{CODER_CHARTER_PROMPT}\n\nUser Request (Plan):\n{formatted_plan}\n\n"
                "Please provide only the Python code as a direct response. "
                "Do not include any markdown formatting like ```python ... ``` or ``` ... ```. "
                "Your entire response should be parseable as a single Python file."
            )

            generated_code_full_response = ""
            if provider_name == "gemini":
                model_instance = client.GenerativeModel(selected_model_name)
                # Add safety settings to reduce refusals for code generation
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
                response = model_instance.generate_content(full_prompt, safety_settings=safety_settings)
                generated_code_full_response = response.text
            elif provider_name == "mistral":
                messages = [{"role": "user", "content": full_prompt}]
                chat_response = client.chat.complete(model=selected_model_name, messages=messages)
                generated_code_full_response = chat_response.choices[0].message.content
            elif provider_name == "together_ai":
                # TogetherAI prompt structure is specific
                together_prompt_structured = f"[INST] {full_prompt} [/INST]"
                response = client.completions.create(
                    prompt=together_prompt_structured, model=selected_model_name, max_tokens=3072, # Increased max_tokens
                    stop=["[/INST]", "</s>", "```"] # Stop sequences
                )
                if response and response.choices:
                    generated_code_full_response = response.choices[0].text.strip()
                else:
                    raise Exception("Together AI response was empty or malformed.")
            else:
                logger.error(f"  Live Coder: Provider {provider_name} not supported.")
                # On unsupported provider, return error with final_output_dir
                return CodeOutput(code_path=final_output_dir, message=f"Coder Error: Provider {provider_name} not supported.")

            logger.info(f"  Live Coder: Raw LLM response (first 300 chars): {generated_code_full_response[:300]}...")
            if not generated_code_full_response.strip():
                logger.warning("  Live Coder: LLM returned empty or whitespace-only response.")
                if attempt < max_retries - 1:
                    logger.info("  Live Coder: Retrying...")
                    continue
                return CodeOutput(code_path=final_output_dir, message="Coder Error: LLM returned empty code after retries.")

            # Code extraction logic (simplified due to stronger prompt against markdown)
            # First, try to remove common markdown code fences if they still appear.
            cleaned_response = generated_code_full_response
            # Regex to find ```python ... ``` or ``` ... ```
            # It captures the content within the fences.
            # re.DOTALL allows . to match newlines.
            python_block_match = re.search(r"```(?:python\s*)?\n?(.*?)\n?```", generated_code_full_response, re.DOTALL)
            if python_block_match:
                logger.info("  Live Coder: Found markdown code block, extracting content.")
                cleaned_response = python_block_match.group(1)
            else:
                # If no blocks, assume the whole response might be code, but check for common refusal phrases.
                # This check is now more critical as we discourage markdown.
                refusal_patterns = [
                    r"I cannot fulfill this request",
                    r"I am unable to create code",
                    r"I'm not able to generate code",
                    r"As a large language model",
                    r"My purpose is to assist with a wide range of tasks",
                    r"However, I cannot directly execute code"
                ]
                if any(re.search(pattern, cleaned_response, re.IGNORECASE) for pattern in refusal_patterns):
                    logger.warning(f"  Live Coder: LLM response appears to be a refusal or explanation, not code: {cleaned_response[:200]}")
                    if attempt < max_retries - 1:
                        logger.info("  Live Coder: Retrying due to detected refusal/explanation...")
                        continue
                    return CodeOutput(code_path=final_output_dir, message="Coder Error: LLM responded with explanation/refusal instead of code.")
                logger.info("  Live Coder: No markdown code block found. Assuming entire response is code.")

            generated_code_final = cleaned_response.strip()

            if not generated_code_final:
                logger.warning("  Live Coder: After parsing/cleaning, no code was extracted.")
                if attempt < max_retries - 1:
                    logger.info("  Live Coder: Retrying...")
                    continue
                return CodeOutput(code_path=final_output_dir, message="Coder Error: No usable code extracted after retries.")

            # Basic validation: try to compile the code.
            try:
                compile(generated_code_final, '<string>', 'exec')
                logger.info("  Live Coder: Code syntax validation (compile check) successful.")
            except SyntaxError as se:
                logger.warning(f"  Live Coder: Generated code failed syntax validation: {se}")
                if attempt < max_retries - 1:
                    logger.info("  Live Coder: Retrying due to syntax error...")
                    continue
                # Save the erroneous code for debugging before returning error
                error_file_name = "generated_code_syntax_error.py"
                error_file_path = final_output_dir / error_file_name
                with open(error_file_path, "w", encoding="utf-8") as f:
                    f.write(f"# Original LLM Response (Syntax Error on Attempt {attempt + 1}):\n# {generated_code_full_response}\n\n# Extracted/Cleaned Code (Syntax Error on Attempt {attempt + 1}):\n{generated_code_final}")
                logger.error(f"  Live Coder: Wrote syntactically incorrect code to {error_file_path}")
                return CodeOutput(code_path=error_file_path, message=f"Coder Error: Generated code has syntax errors after {max_retries} attempts. Last error: {se}")

            # If validation passes
            file_name = "generated_code.py"
            file_path = final_output_dir / file_name
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(generated_code_final)
            logger.info(f"  Live Coder: Successfully wrote validated code to {file_path}")
            return CodeOutput(code_path=file_path, message="Successfully generated code.")

        except Exception as e:
            logger.error(f"  Live Coder: Exception during attempt {attempt + 1}: {type(e).__name__} - {str(e)}", exc_info=True)
            if attempt < max_retries - 1:
                logger.info("  Live Coder: Retrying due to exception...")
                continue
            # After last retry, return error with final_output_dir
            # Potentially save the last raw response for debugging
            error_response_file = final_output_dir / "llm_error_response.txt"
            try:
                with open(error_response_file, "w", encoding="utf-8") as f:
                    f.write(f"Error on attempt {attempt + 1}: {type(e).__name__} - {str(e)}\n\n")
                    f.write("Raw LLM response (if available):\n")
                    f.write(generated_code_full_response if 'generated_code_full_response' in locals() else "N/A")
                logger.info(f"  Live Coder: Saved error response to {error_response_file}")
            except Exception as ex_save:
                logger.error(f"  Live Coder: Could not save error response file: {ex_save}")

            return CodeOutput(code_path=final_output_dir, message=f"Coder Error: Exception after {max_retries} attempts - {type(e).__name__}: {str(e)}")

    # Should not be reached if loop logic is correct, but as a fallback:
    logger.error("  Live Coder: Exited retry loop unexpectedly.")
    return CodeOutput(code_path=final_output_dir, message=f"Coder Error: Unexpected exit from generation loop after {max_retries} attempts.")


def initialize_pm_review_crew(blueprint_path, commission_id, blueprint_version="1.0"):
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
            f"Mock PM Review: Error reading blueprint {blueprint_path}. Defaulting to REVISION_REQUESTED.", exc_info=True
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
    logger_artisans.info(
        f"Artisan Assembly: V1 Basic Auditor Agent activated for commission '{commission_id}'. Auditing: {code_input.code_path}"
    )
    if not code_input.code_path or not code_input.code_path.exists() or not code_input.code_path.is_file():
        err_msg = f"Audit Error: Code path '{code_input.code_path}' is invalid or file not found."
        logger_artisans.error(err_msg)
        return AuditOutput(status=AuditStatus.FAILURE, message=err_msg)

    try:
        with open(code_input.code_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        if not source_code.strip():
            logger_artisans.warning(f"  V1 Auditor: Code file {code_input.code_path} is empty.")
            return AuditOutput(status=AuditStatus.FAILURE, message=f"Code file {code_input.code_path.name} is empty.")
        compile(source_code, str(code_input.code_path), 'exec')
        logger_artisans.info(f"  V1 Auditor: Syntax check PASSED for {code_input.code_path}.")
        return AuditOutput(status=AuditStatus.SUCCESS, message="Syntax OK.")
    except FileNotFoundError:
        logger_artisans.error(f"  Audit Error: Code file not found at {code_input.code_path} during read.")
        return AuditOutput(status=AuditStatus.FAILURE, message=f"Code file for audit not found: {code_input.code_path}")
    except SyntaxError as e:
        logger_artisans.warning(f"  V1 Auditor: Syntax check FAILED for {code_input.code_path}. Error: {e}")
        return AuditOutput(status=AuditStatus.FAILURE, message=f"Syntax error in {code_input.code_path.name}: {e.msg} (line {e.lineno})")
    except Exception as e:
        logger_artisans.error(f"  V1 Auditor: Unexpected error for {code_input.code_path}. Error: {e}", exc_info=True)
        return AuditOutput(status=AuditStatus.FAILURE, message=f"Unexpected error auditing {code_input.code_path.name}: {str(e)}")

def initialize_coder_agent_v1(
    plan_input: PlanOutput, commission_id: str, output_target_dir: Path, llm_config: Optional[Dict[str, Any]] = None
) -> CodeOutput:
    logger_artisans.info(f"Artisan Assembly: V1 Coder Agent activated for commission '{commission_id}'.")
    output_target_dir.mkdir(parents=True, exist_ok=True)

    if not plan_input.tasks:
        logger_artisans.error("  Coder Error: No tasks in plan.")
        return CodeOutput(code_path=output_target_dir, message="Coder Error: No tasks in plan.")

    task_description = plan_input.tasks[0]
    file_content_full_response: str = ""
    message: str = ""
    file_name = "app.py"

    if llm_config and llm_config.get("client"):
        provider_name = llm_config['provider_name']
        client = llm_config['client']
        models = llm_config.get('models', [])
        selected_model_name = models[0] if models else None

        if not selected_model_name:
            logger_artisans.error(f"  V1 Coder: No model for {provider_name}.")
            return CodeOutput(code_path=output_target_dir, message=f"Coder Error: No model for {provider_name}.")

        logger_artisans.info(f"  V1 Coder: Using {provider_name} with model {selected_model_name}.")
        full_prompt = (
            f"{CODER_CHARTER_PROMPT}\n\n"
            f"Blueprint Task: '{task_description}'.\n"
            "Output only Python code. No markdown, no explanation."
        )
        try:
            if provider_name == 'gemini':
                model_instance = client.GenerativeModel(selected_model_name)
                response = model_instance.generate_content(full_prompt)
                file_content_full_response = response.text
            elif provider_name == 'mistral':
                messages = [{"role": "user", "content": full_prompt}]
                chat_response = client.chat.complete(model=selected_model_name, messages=messages)
                file_content_full_response = chat_response.choices[0].message.content
            elif provider_name == 'together_ai':
                response = client.completions.create(
                    prompt=f"[INST] {full_prompt} [/INST]", model=selected_model_name, max_tokens=2048, stop=["```"]
                )
                if response and response.choices: file_content_full_response = response.choices[0].text.strip()
                else: raise Exception("Together AI response empty/malformed.")

            logger_artisans.info(f"  V1 Coder (LLM): Raw response (first 200): {file_content_full_response[:200]}")

            python_blocks = re.findall(r"```python\s*\n?(.*?)\n```", file_content_full_response, re.DOTALL)
            generic_blocks = re.findall(r"```\s*\n?(.*?)\n```", file_content_full_response, re.DOTALL)
            selected_code_content = ""

            if python_blocks:
                logger_artisans.info(f"  V1 Coder (LLM): Found {len(python_blocks)} Python-specific blocks.")
                if len(python_blocks) == 1: selected_code_content = python_blocks[0]
                else:
                    main_candidates = [b for b in python_blocks if 'if __name__ == "__main__":' in b]
                    if main_candidates: selected_code_content = main_candidates[0]
                    else:
                        non_test_candidates = [b for b in python_blocks if not ("unittest" in b or "pytest" in b or "test_" in b or "Test" in b)]
                        if non_test_candidates: selected_code_content = non_test_candidates[0]
                        else: selected_code_content = python_blocks[0]
            elif generic_blocks:
                logger_artisans.info(f"  V1 Coder (LLM): No Python-specific. Found {len(generic_blocks)} generic. Selecting first.")
                selected_code_content = generic_blocks[0]
            else:
                logger_artisans.warning("  V1 Coder (LLM): No markdown blocks found. Checking if entire response is code or natural language.")
                if "```" in file_content_full_response or \
                   file_content_full_response.lower().strip().startswith("here's") or \
                   file_content_full_response.lower().strip().startswith("sure,") or \
                   file_content_full_response.lower().strip().startswith("certainly,") or \
                   file_content_full_response.lower().strip().startswith("okay,") or \
                   ("python" in file_content_full_response.lower() and len(file_content_full_response) < 100 and '\n' not in file_content_full_response):
                    logger_artisans.warning("  V1 Coder (LLM): Fallback 'no blocks' determined to be natural language or malformed. Clearing code.")
                    selected_code_content = ""
                else:
                    logger_artisans.warning("  V1 Coder (LLM): Fallback 'no blocks' - assuming entire response is code (still risky).")
                    selected_code_content = file_content_full_response

            file_content_final = selected_code_content.strip()

            if not file_content_final:
                logger_artisans.error("  V1 Coder (LLM): No usable code extracted after cleanup.")
                raise Exception("LLM returned empty or unparseable content after cleanup.")

            message = f"LLM ({provider_name}/{selected_model_name}) generated code."
            logger_artisans.info(f"  V1 Coder (LLM): Processed code using {provider_name}/{selected_model_name}.")
            file_content = file_content_final

        except Exception as e:
            logger_artisans.error(f"  Coder Agent: LLM call/parsing failed. Error: {e}", exc_info=True)
            file_name = "app_llm_failed.py"
            file_content = f"# LLM generation failed: {task_description}\n# Error: {e}\nprint('Error: LLM failed.')\n"
            message = f"LLM generation failed. Error: {e}"
    else:
        logger_artisans.warning("  Coder Agent: No LLM config. Using placeholder.")
        if "Create a Python file that prints 'Hello, World!'" in task_description:
            file_name = "main.py"
            file_content = 'print("Hello, World!")\n'
            message = "Created 'Hello, World!' (placeholder)."
        else:
            file_name = "task_output.txt"
            file_content = f"Task (no LLM):\n{task_description}\n"
            message = "Created generic task output (placeholder)."

    file_path = output_target_dir / file_name
    try:
        with open(file_path, "w", encoding="utf-8") as f: f.write(file_content)
        logger_artisans.info(f"  V1 Coder: Successfully wrote to {file_path}")
        return CodeOutput(code_path=file_path, message=message)
    except IOError as e:
        logger_artisans.error(f"  Coder Error: Could not write to {file_path}. Error: {e}", exc_info=True)
        return CodeOutput(code_path=output_target_dir, message=f"Coder Error: Write failed - {e}")


def invoke_oracle_llm_for_advice(
    user_request: str,
    current_plan_str: str,
    failed_code_str: str,
    audit_feedback_str: str,
    llm_config: Optional[Dict[str, Any]]
) -> str:
    logger = logging.getLogger(__name__)
    logger.info("Artisan Assembly: Oracle LLM for Advice activated.")

    if not llm_config or not llm_config.get("client"):
        logger.error("  Oracle LLM: LLM configuration not provided or client missing.")
        return "Oracle Error: LLM not configured."

    provider_name = llm_config.get("provider_name", "Unknown")
    client = llm_config["client"]
    selected_model_name = llm_config.get("oracle_model_name") or (llm_config["models"][0] if llm_config.get("models") else None)

    if not selected_model_name:
        logger.error(f"  Oracle LLM: No models found or specified for provider {provider_name}.")
        return f"Oracle Error: No models available/specified for {provider_name}."

    temperature = llm_config.get("temperature")

    logger.info(f"  Oracle LLM: Using {provider_name} with model {selected_model_name}" + (f" and temperature {temperature}" if temperature is not None else ""))

    try:
        # Ensure ORACLE_ASSISTANCE_PROMPT is imported if not already at top level
        from .prompts import ORACLE_ASSISTANCE_PROMPT

        prompt = ORACLE_ASSISTANCE_PROMPT.format(
            user_request=user_request,
            current_plan=current_plan_str,
            failed_code=failed_code_str,
            audit_feedback=audit_feedback_str
        )

        advice_text = ""

        if provider_name == "gemini":
            model_instance = client.GenerativeModel(selected_model_name)
            gen_config_args = {}
            if temperature is not None:
                gen_config_args["temperature"] = temperature
            response = model_instance.generate_content(prompt, generation_config=genai.types.GenerationConfig(**gen_config_args) if gen_config_args else None)
            advice_text = response.text
        elif provider_name == "mistral":
            messages = [{"role": "user", "content": prompt}]
            mistral_params = {"model": selected_model_name, "messages": messages}
            if temperature is not None:
                mistral_params["temperature"] = temperature
            chat_response = client.chat.complete(**mistral_params)
            advice_text = chat_response.choices[0].message.content
        elif provider_name == "together_ai":
            together_params = {
                "prompt": f"[INST] {prompt} [/INST]",
                "model": selected_model_name,
                "max_tokens": 1024,
            }
            if temperature is not None:
                together_params["temperature"] = temperature
            response = client.completions.create(**together_params)
            if response and response.choices:
                advice_text = response.choices[0].text.strip()
            else:
                raise Exception("Together AI (Oracle) response was empty or malformed.")
        else:
            logger.error(f"  Oracle LLM: Provider {provider_name} not supported.")
            return f"Oracle Error: Provider {provider_name} not supported."

        logger.info(f"  Oracle LLM: Raw advice response: {advice_text[:300]}...")
        return advice_text.strip()

    except Exception as e:
        logger.error(f"  Oracle LLM: Exception caught: {type(e).__name__} - {str(e)}", exc_info=True)
        return f"Oracle Error during advice generation: {type(e).__name__} - {str(e)}"

print("DEBUG: artisans.py - invoke_oracle_llm_for_advice IS DEFINED") # Debug print


def initialize_help_example_extractor_agent(
    help_text: str,
    llm_config: Optional[Dict[str, Any]]
) -> Dict[str, Optional[str]]:
    logger = logging.getLogger(__name__)
    logger.info("Artisan Assembly: Help Example Extractor Agent activated.")

    default_error_response = {
        "command": None,
        "stdin_input": None,
        "notes": "Help example extraction failed or no example found."
    }

    if not llm_config or not llm_config.get("client"):
        logger.error("  Help Extractor: LLM configuration not provided or client missing.")
        default_error_response["notes"] = "Help Extractor Error: LLM not configured."
        return default_error_response

    provider_name = llm_config.get("provider_name", "Unknown")
    client = llm_config["client"]
    selected_model_name = llm_config.get("help_extractor_model_name") or \
                          (llm_config["models"][0] if llm_config.get("models") else None)

    if not selected_model_name:
        logger.error(f"  Help Extractor: No models found/specified for provider {provider_name}.")
        default_error_response["notes"] = f"Help Extractor Error: No models for {provider_name}."
        return default_error_response

    temperature = llm_config.get("temperature", 0.3)

    logger.info(f"  Help Extractor: Using {provider_name} with model {selected_model_name} and temperature {temperature}")

    try:
        # Ensure HELP_EXAMPLE_EXTRACTOR_PROMPT is imported (already done at module level)
        prompt = HELP_EXAMPLE_EXTRACTOR_PROMPT.format(help_text_placeholder=help_text)
        raw_llm_response = ""

        if provider_name == "gemini":
            model_instance = client.GenerativeModel(selected_model_name)
            response = model_instance.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=temperature))
            raw_llm_response = response.text
        elif provider_name == "mistral":
            messages = [{"role": "user", "content": prompt}]
            chat_response = client.chat.complete(model=selected_model_name, messages=messages, temperature=temperature)
            raw_llm_response = chat_response.choices[0].message.content
        elif provider_name == "together_ai":
            response = client.completions.create(
                prompt=f"[INST] {prompt} [/INST]", model=selected_model_name, max_tokens=512, temperature=temperature
            )
            if response and response.choices:
                raw_llm_response = response.choices[0].text.strip()
            else:
                raise Exception("Together AI (Help Extractor) response was empty or malformed.")
        else:
            logger.error(f"  Help Extractor: Provider {provider_name} not supported.")
            default_error_response["notes"] = f"Help Extractor Error: Provider {provider_name} not supported."
            return default_error_response

        logger.info(f"  Help Extractor: Raw LLM response: {raw_llm_response[:300]}...")

        json_match = re.search(r"```json\s*\n?(.*?)\n?```", raw_llm_response, re.DOTALL)
        json_str_to_parse = json_match.group(1) if json_match else raw_llm_response

        extracted_data = json.loads(json_str_to_parse)
        return {
            "command": extracted_data.get("command"),
            "stdin_input": extracted_data.get("stdin_input"),
            "notes": extracted_data.get("notes")
        }

    except json.JSONDecodeError as je:
        logger.error(f"  Help Extractor: Failed to parse JSON response: {je}. Raw response: {raw_llm_response}", exc_info=True)
        default_error_response["notes"] = f"Help Extractor Error: Could not parse JSON from LLM. {je}"
        return default_error_response
    except Exception as e:
        logger.error(f"  Help Extractor: Exception caught: {type(e).__name__} - {str(e)}", exc_info=True)
        default_error_response["notes"] = f"Help Extractor Error: {type(e).__name__} - {str(e)}"
        return default_error_response

print("DEBUG: artisans.py - initialize_help_example_extractor_agent IS DEFINED") # Debug print
