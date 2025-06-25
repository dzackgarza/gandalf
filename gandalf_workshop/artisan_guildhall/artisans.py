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
from .prompts import CODER_CHARTER_PROMPT

import py_compile
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

    if not selected_model_name:
        logger.error(f"  Live Planner: No models found in LLM configuration for provider {provider_name}.")
        return PlanOutput(tasks=[f"Error: No models available for {provider_name} in planner."], details=None)

    logger.info(f"  Live Planner: Using {provider_name} with model {selected_model_name}.")

    try:
        from .prompts import PLANNER_CHARTER_PROMPT
        full_prompt = f"{PLANNER_CHARTER_PROMPT}\n\nUser Request:\n{user_prompt}"
        raw_plan = ""

        if provider_name == "gemini":
            model_instance = client.GenerativeModel(selected_model_name)
            response = model_instance.generate_content(full_prompt)
            raw_plan = response.text
        elif provider_name == "mistral":
            messages = [{"role": "user", "content": full_prompt}]
            chat_response = client.chat.complete(model=selected_model_name, messages=messages)
            raw_plan = chat_response.choices[0].message.content
        elif provider_name == "together_ai":
            together_prompt = f"[INST] {full_prompt} [/INST]"
            response = client.completions.create(
                prompt=together_prompt, model=selected_model_name, max_tokens=1024, stop=["[/INST]", "</s>"]
            )
            if response and response.choices:
                raw_plan = response.choices[0].text.strip()
            else:
                raise Exception("Together AI response was empty or malformed.")
        else:
            logger.error(f"  Live Planner: Provider {provider_name} not supported for LLM call.")
            return PlanOutput(tasks=[f"Error: Planner provider {provider_name} not supported."], details=None)

        logger.info(f"  Live Planner: Raw LLM response: {raw_plan[:200]}...")
        if raw_plan:
            tasks = [task.strip() for task in raw_plan.split('\n') if task.strip()]
            if not tasks: tasks = [raw_plan.strip()]
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
    plan_input: PlanOutput, commission_id: str, output_target_dir: Path, llm_config: Optional[Dict[str, Any]] = None
) -> CodeOutput:
    logger = logging.getLogger(__name__)
    logger.info(f"Artisan Assembly: Live Coder Agent activated for commission '{commission_id}'.")
    output_target_dir.mkdir(parents=True, exist_ok=True)

    if not llm_config or not llm_config.get("client"):
        logger.error("  Live Coder: LLM configuration not provided or client missing.")
        return CodeOutput(code_path=output_target_dir, message="Coder Error: LLM not configured for coder.")

    provider_name = llm_config["provider_name"]
    client = llm_config["client"]
    selected_model_name = llm_config["models"][0] if llm_config.get("models") else None

    if not selected_model_name:
        logger.error(f"  Live Coder: No models found for provider {provider_name}.")
        return CodeOutput(code_path=output_target_dir, message=f"Coder Error: No models for {provider_name}.")

    logger.info(f"  Live Coder: Using {provider_name} with model {selected_model_name}.")

    try:
        from .prompts import CODER_CHARTER_PROMPT
        formatted_plan = "\n".join(f"- {task}" for task in plan_input.tasks)
        full_prompt = f"{CODER_CHARTER_PROMPT}\n\nUser Request (Plan):\n{formatted_plan}\n\nPlease provide only the Python code as a direct response. Do not include any markdown formatting like ```python ... ```."

        generated_code_full_response = ""
        if provider_name == "gemini":
            model_instance = client.GenerativeModel(selected_model_name)
            response = model_instance.generate_content(full_prompt)
            generated_code_full_response = response.text
        elif provider_name == "mistral":
            messages = [{"role": "user", "content": full_prompt}]
            chat_response = client.chat.complete(model=selected_model_name, messages=messages)
            generated_code_full_response = chat_response.choices[0].message.content
        elif provider_name == "together_ai":
            together_prompt = f"[INST] {full_prompt} [/INST]"
            response = client.completions.create(
                prompt=together_prompt, model=selected_model_name, max_tokens=2048, stop=["[/INST]", "</s>", "```"]
            )
            if response and response.choices:
                generated_code_full_response = response.choices[0].text.strip()
            else:
                raise Exception("Together AI response was empty or malformed.")
        else:
            logger.error(f"  Live Coder: Provider {provider_name} not supported.")
            return CodeOutput(code_path=output_target_dir, message=f"Coder Error: Provider {provider_name} not supported.")

        logger.info(f"  Live Coder: Raw LLM response (first 200): {generated_code_full_response[:200]}...")
        if not generated_code_full_response:
            logger.warning("  Live Coder: LLM returned empty response.")
            return CodeOutput(code_path=output_target_dir, message="Coder Error: LLM returned empty code.")

        python_blocks = re.findall(r"```python\s*\n?(.*?)\n```", generated_code_full_response, re.DOTALL)
        generic_blocks = re.findall(r"```\s*\n?(.*?)\n```", generated_code_full_response, re.DOTALL)
        selected_code_content = ""

        if python_blocks:
            logger.info(f"  Live Coder: Found {len(python_blocks)} Python-specific blocks.")
            if len(python_blocks) == 1:
                selected_code_content = python_blocks[0]
                logger.info("  Live Coder: Single Python block selected.")
            else:
                main_candidates = [b for b in python_blocks if 'if __name__ == "__main__":' in b]
                if main_candidates:
                    selected_code_content = main_candidates[0]
                    logger.info("  Live Coder: Selected Python block with '__main__' check.")
                else:
                    non_test_candidates = [b for b in python_blocks if not ("unittest" in b or "pytest" in b or "test_" in b or "Test" in b)]
                    if non_test_candidates:
                        selected_code_content = non_test_candidates[0]
                        logger.info("  Live Coder: Selected first non-test Python block.")
                    else:
                        selected_code_content = python_blocks[0]
                        logger.warning("  Live Coder: Multiple Python blocks, all seem like tests. Selected first one.")
        elif generic_blocks:
            logger.info(f"  Live Coder: No Python-specific blocks. Found {len(generic_blocks)} generic blocks.")
            selected_code_content = generic_blocks[0]
            logger.info("  Live Coder: Selected first generic block.")
        else:
            logger.warning("  Live Coder: No markdown code blocks found. Checking if entire response is code or natural language.")
            # If no blocks, check if the response *looks* like it might be just code, or if it's likely natural language.
            # A simple heuristic: if it contains "```" anywhere, it's malformed for this fallback.
            # Or if it contains common introductory phrases.
            if "```" in generated_code_full_response or \
               generated_code_full_response.lower().strip().startswith("here's") or \
               generated_code_full_response.lower().strip().startswith("sure,") or \
               generated_code_full_response.lower().strip().startswith("certainly,") or \
               generated_code_full_response.lower().strip().startswith("okay,") or \
               ("python" in generated_code_full_response.lower() and len(generated_code_full_response) < 100 and '\n' not in generated_code_full_response): # Short line with "python"
                logger.warning("  Live Coder: Fallback 'no blocks' determined to be natural language or malformed. Clearing code.")
                selected_code_content = ""
            else:
                logger.warning("  Live Coder: Fallback 'no blocks' - assuming entire response is code (still risky).")
                selected_code_content = generated_code_full_response

        generated_code_final = selected_code_content.strip()

        if not generated_code_final:
            logger.warning("  Live Coder: After parsing, no code was extracted.")
            return CodeOutput(code_path=output_target_dir, message="Coder Error: No usable code extracted.")

        file_name = "generated_code.py"
        file_path = output_target_dir / file_name
        with open(file_path, "w", encoding="utf-8") as f: f.write(generated_code_final)
        logger.info(f"  Live Coder: Successfully wrote code to {file_path}")
        return CodeOutput(code_path=file_path, message="Successfully generated code.")
    except Exception as e:
        logger.error(f"  Live Coder: Exception: {e}", exc_info=True)
        return CodeOutput(code_path=output_target_dir, message=f"Coder Error: Exception - {e}")

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
