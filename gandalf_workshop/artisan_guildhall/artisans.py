"""
artisans.py - The Assembly Hall for Specialist Artisan Crews

This module provides functions to initialize and configure "Artisan Crews"
(specialized AI agent teams). It's like a workshop assembly hall where the
Workshop Manager briefs craftsmen (Planner, Coder, Inspector crews) before
they start a commission. Each function here would typically set up agents
(e.g., using CrewAI, AutoGen, LangGraph) with charters, tools, and context.
This module provides functions to initialize and configure "Artisan Crews"
(specialized AI agent teams). It's like a workshop assembly hall where the
Workshop Manager briefs craftsmen (Planner, Coder, Inspector crews) before
they start a commission. Each function here would typically set up agents
(e.g., using CrewAI, AutoGen, LangGraph) with charters, tools, and context.
"""

# from .prompts import (PLANNER_CHARTER_PROMPT, CODER_CHARTER_PROMPT,
#                       GENERAL_INSPECTOR_CHARTER_PROMPT)
# Import necessary AI framework components here, e.g.:
# from crewai import Agent, Task, Crew, Process

import yaml
import logging
from pathlib import Path
from datetime import datetime, timezone

# from .prompts import (PLANNER_CHARTER_PROMPT, CODER_CHARTER_PROMPT,
#                       GENERAL_INSPECTOR_CHARTER_PROMPT)
# Import necessary AI framework components here, e.g.:
# from crewai import Agent, Task, Crew, Process
from gandalf_workshop.specs.data_models import (
    PlanOutput,
    PMReview,
    PMReviewDecision,
    CodeOutput,  # Added for Auditor V1
    AuditOutput,  # Added for Auditor V1
    AuditStatus,  # Added for Auditor V1
)
import py_compile  # Added for Auditor V1
import tempfile # For safe auditing


# Metaphor: These functions are like the Workshop Manager's assistants who
# know how to quickly assemble Planners, Coders, or Inspectors, providing
# them with their official charters (prompts) and tools.
# Metaphor: These functions are like the Workshop Manager's assistants who
# know how to quickly assemble Planners, Coders, or Inspectors, providing
# them with their official charters (prompts) and tools.


def initialize_planning_crew():
    """
    Assembles and initializes a "Planning Crew" of AI agents.
    Metaphor: Gathers the Master Draftsmen and Architectural Scribes in the
    Design Studio, handing them their charter and tools to create a new
    Blueprint.

    This crew would be responsible for taking a user prompt and generating
    a detailed `blueprint.yaml` file.
    """
    # Placeholder for actual crew initialization (e.g., CrewAI setup)
    # Example (conceptual):
    # planner_agent = Agent(
    #   role='Lead Blueprint Architect',
    #   goal='Create a comprehensive and actionable blueprint from a user '
    #        'request.',
    #   backstory='A seasoned architect renowned for clarity and foresight '
    #             'in design.',
    #   instructions=PLANNER_CHARTER_PROMPT,
    #   verbose=True
    # )
    # planning_task = Task(
    #   description='Analyze the user request and generate a blueprint.yaml '
    #               'file.',
    #   agent=planner_agent
    # )
    # planning_crew = Crew(
    #   agents=[planner_agent],
    #   tasks=[planning_task],
    #   process=Process.sequential
    # )
    # return planning_crew
    print("Artisan Assembly: Planning Crew initialized (placeholder).")


def initialize_coding_crew():
    """
    Assembles and initializes a "Coding Crew" of AI agents.
    Metaphor: Summons the Master Builders and Code Smiths to the Main
    Workbench, providing them with the Blueprint and tools to construct the
    Product.

    This crew takes a `blueprint.yaml` and (optionally) an
    `inspection_report.json` to generate or revise the product code.
    """
    # Placeholder for actual crew initialization
    # Example (conceptual):
    # coder_agent = Agent(
    #   role='Lead Software Artisan',
    #   goal='Implement the product specifications from the blueprint and '
    #        'address any reported flaws.',
    #   backstory='A meticulous craftsman dedicated to producing high-quality, '
    #             'functional code.',
    #   instructions=CODER_CHARTER_PROMPT,
    #   verbose=True
    # )
    # # ... more agents for testing, specific component development etc.
    # coding_task = Task(
    #   description='Develop or revise the product based on the blueprint and '
    #               'inspection report.',
    #   agent=coder_agent
    # )
    # coding_crew = Crew(
    #   agents=[coder_agent], # Potentially more agents
    #   tasks=[coding_task],
    #   process=Process.sequential
    # )
    # return coding_crew
    print("Artisan Assembly: Coding Crew initialized (placeholder).")


def initialize_inspection_crew():
    """
    Assembles and initializes an "Inspection Crew" of AI agents.
    Metaphor: Calls upon the Guild of Quality Assessors and Scrutineers
    to the Quality Control Lab, tasking them with examining a Product
    against its Blueprint.

    This crew takes a product and its `blueprint.yaml` to produce an
    `inspection_report.json`. It might include various specialized
    inspectors.
    """
    # Placeholder for actual crew initialization
    # Example (conceptual):
    # lead_inspector_agent = Agent(
    #   role='Chief Quality Inspector',
    #   goal='Conduct a thorough inspection of the product against its '
    #        'blueprint and generate a detailed inspection report.',
    #   backstory='An uncompromising guardian of quality with an eagle eye '
    #             'for detail.',
    #   instructions=GENERAL_INSPECTOR_CHARTER_PROMPT,  # May be specialized
    #   verbose=True
    # )
    # # Could add more specialized inspector agents here (e.g., security,
    # # compliance)
    # inspection_task = Task(
    #   description='Inspect the submitted product against the blueprint and '
    #               'document all findings.',
    #   agent=lead_inspector_agent
    # )
    # inspection_crew = Crew(
    #   agents=[lead_inspector_agent],  # Potentially more specialized
    #                                   # inspectors
    #   tasks=[inspection_task],
    #   process=Process.sequential
    # )
    # return inspection_crew
    print("Artisan Assembly: Inspection Crew initialized (placeholder).")


# V1 Basic Agents - these are simple functions for now, not full "crews"
# They will be integrated into the V1 WorkshopManager orchestrator loop.
# PlanOutput, CodeOutput, AuditOutput, AuditStatus are imported at the top.


def initialize_planner_agent_v1(user_prompt: str, commission_id: str) -> PlanOutput:
    """
    Initializes and runs a basic V1 Planner Agent.
    For V1, this is a simple function that returns a predefined plan
    based on the user prompt. It does not involve a full LLM crew.

    Args:
        user_prompt: The initial request from the client.
        commission_id: A unique ID for this commission.

    Returns:
        A PlanOutput object.
    """
    print(
        f"Artisan Assembly: V1 Basic Planner Agent activated for commission "
        f"'{commission_id}'."
    )
    print(f"  User Prompt: {user_prompt[:100]}...")  # Log a snippet of the prompt

    if "hello world" in user_prompt.lower():
        plan = PlanOutput(
            tasks=["Create a Python file that prints 'Hello, World!'"], details=None
        )
        print("  V1 Planner: Generated 'Hello, World!' plan.")
    else:
        plan = PlanOutput(
            tasks=[f"Task 1: Implement feature based on: {user_prompt}"], details=None
        )
        print(f"  V1 Planner: Generated generic plan for: {user_prompt[:50]}...")

    return plan


def initialize_pm_review_crew(blueprint_path, commission_id, blueprint_version="1.0"):
    """
    Simulates the PM Review Crew analyzing a blueprint.
    Metaphor: The Chief Strategist pores over the Blueprint, comparing it
    against the original Commission's grand vision.

    For this mock implementation, it makes a simple decision.
    In a real system, this would involve an LLM agent using PM_CHARTER_PROMPT.

    Args:
        blueprint_path (pathlib.Path): Path to the blueprint.yaml file.
        commission_id (str): The ID of the commission.
        blueprint_version (str): The version of the blueprint being reviewed.

    Returns:
        pathlib.Path: Path to the generated PM_Review.json file.
    """
    # Imports moved to top of file

    print(
        f"Artisan Assembly: PM Review Crew activated for blueprint: "
        f"{blueprint_path}"
    )

    # Mock decision logic:
    # Read blueprint summary. If "simple" or "mvp", approve. Else, request revision.
    try:
        with open(blueprint_path, "r") as f:
            blueprint_content = yaml.safe_load(f)
        summary = blueprint_content.get("project_summary", "").lower()
        if "complex" in summary:
            decision = PMReviewDecision.REVISION_REQUESTED
            rationale = (
                "Mock PM Review: Blueprint needs revision. "
                "Summary indicates complexity. Please simplify."  # Added "Please simplify"
            )
            suggested_focus_areas = [
                "project_summary",
                "product_specifications.modules",
            ]
        elif "simple" in summary or "mvp" in summary:  # Only if not complex
            decision = PMReviewDecision.APPROVED
            rationale = (
                "Mock PM Review: Blueprint approved. "
                "Summary indicates a simple or MVP scope."
            )
            suggested_focus_areas = None
        else:  # Default if neither complex, simple, nor mvp explicitly mentioned
            decision = PMReviewDecision.REVISION_REQUESTED
            rationale = (
                "Mock PM Review: Blueprint needs revision. Scope clarity needed "
                "(neither explicitly simple/mvp nor complex)."
            )
            suggested_focus_areas = ["project_summary"]
    except Exception as e:  # pylint: disable=broad-except
        logger = logging.getLogger(__name__)
        logger.error(
            f"Mock PM Review: Error reading blueprint {blueprint_path}. "
            f"Defaulting to REVISION_REQUESTED.",
            exc_info=True,
        )
        decision = PMReviewDecision.REVISION_REQUESTED
        rationale = (
            f"Mock PM Review: Error reading blueprint. Defaulting to "
            f"REVISION_REQUESTED. Error: {e} (See logs for details)"
        )
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

    # Define reviews directory
    reviews_dir = Path("gandalf_workshop/reviews") / commission_id
    reviews_dir.mkdir(parents=True, exist_ok=True)

    # Create a unique filename for the review
    timestamp_str = review_data.review_timestamp.strftime("%Y%m%d_%H%M%S_%f")
    review_file_path = reviews_dir / f"pm_review_{timestamp_str}.json"

    with open(review_file_path, "w") as f:
        f.write(review_data.model_dump_json(indent=2))

    print(f"Artisan Assembly: PM Review Crew generated report: {review_file_path}")
    return review_file_path


# The __main__ block below was moved to a test in:
# gandalf_workshop/tests/test_artisans.py
# to allow pytest to include its logic in coverage reports.


def initialize_auditor_agent_v1(
    code_input: CodeOutput, commission_id: str
) -> AuditOutput:
    """
    Initializes and runs a basic V1 Auditor Agent.
    For V1, this is a simple function that performs a syntax check on the
    provided Python code file.

    Args:
        code_input: A CodeOutput object containing the path to the code.
        commission_id: A unique ID for this commission.

    Returns:
        An AuditOutput object.
    """
    logger = logging.getLogger(__name__)
    logger.info(
        f"Artisan Assembly: V1 Basic Auditor Agent activated for commission "
        f"'{commission_id}'."
    )
    logger.info(f"  Auditing code at: {code_input.code_path}")

    if not code_input.code_path.exists() or not code_input.code_path.is_file():
        logger.error(f"  Audit Error: Code file not found at {code_input.code_path}")
        return AuditOutput(
            status=AuditStatus.FAILURE,
            message=f"Code file not found: {code_input.code_path}",
            report_path=None,
        )

    # Use built-in compile() for a pure syntax check without file I/O for .pyc
    try:
        with open(code_input.code_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        compile(source_code, str(code_input.code_path), 'exec')
        logger.info("  V1 Auditor: Syntax check PASSED.")
        return AuditOutput(
            status=AuditStatus.SUCCESS, message="Syntax OK.", report_path=None
        )
    except FileNotFoundError: # Handle if the source file itself is missing during read
        logger.error(f"  Audit Error: Code file not found at {code_input.code_path} during read for compile.")
        return AuditOutput(
            status=AuditStatus.FAILURE,
            message=f"Code file (to be audited) not found during read: {code_input.code_path}",
            report_path=None,
        )
    except SyntaxError as e:
        logger.warning(f"  V1 Auditor: Syntax check FAILED. Error: {e}")
        return AuditOutput(
            status=AuditStatus.FAILURE,
            message=f"Syntax error: {e.msg} (line {e.lineno})", # More specific error
            report_path=None,
        )
    except Exception as e:  # pylint: disable=broad-except # Catch any other exceptions
        logger.error(
            f"  V1 Auditor: Unexpected error during audit. Error: {e}", exc_info=True
        )
        return AuditOutput(
            status=AuditStatus.FAILURE,
            message=f"Unexpected error during audit: {str(e)}",
            report_path=None,
        )


def initialize_coder_agent_v1(
    plan_input: PlanOutput,
    commission_id: str,  # Retained for logging/context if needed inside agent
    output_target_dir: Path,
) -> CodeOutput:
    """
    Initializes and runs a basic V1 Coder Agent.
    For V1, this is a simple function that creates a file based on the plan
    directly within the provided output_target_dir.

    Args:
        plan_input: A PlanOutput object containing the tasks.
        commission_id: A unique ID for this commission (for context/logging).
        output_target_dir: The specific directory where the generated code file
                           should be saved. This directory will be created if
                           it doesn't exist.

    Returns:
        A CodeOutput object.
    """
    logger = logging.getLogger(__name__)
    logger.info(
        f"Artisan Assembly: V1 Basic Coder Agent activated for commission "
        f"'{commission_id}'."
    )
    logger.info(f"  Plan tasks: {plan_input.tasks}")
    logger.info(f"  Output target directory: {output_target_dir}")

    # Ensure the output directory for the commission exists
    output_target_dir.mkdir(parents=True, exist_ok=True)

    # For V1, we assume the first task is the primary one.
    # And for "Hello, World", we specifically look for that task.
    if not plan_input.tasks:
        logger.error("  Coder Error: No tasks found in the plan.")
        return CodeOutput(
            code_path=output_target_dir,  # Return dir path on error
            message="Coder Error: No tasks found in plan.",
        )

    first_task = plan_input.tasks[0]
    file_path: Path | None = None  # Use | for union type for Python 3.10+
    file_content: str = ""
    message: str = ""

    if "Create a Python file that prints 'Hello, World!'" in first_task:
        file_name = "main.py" # Standardized to main.py for "Hello, World!"
        file_content = 'print("Hello, World!")\n'
        file_path = output_target_dir / file_name
        message = f"Successfully created {file_name} for 'Hello, World!' task."
        logger.info(f"  V1 Coder: Preparing to create '{file_name}' for Hello World.")
    else:
        # Generic task handling: create a text file with task description
        file_name = "task_output.txt"
        file_content = f"Task from plan:\n{first_task}\n"
        file_path = output_target_dir / file_name
        message = f"Successfully created {file_name} for generic task."
        logger.info(
            f"  V1 Coder: Preparing to create '{file_name}' for generic task: {first_task[:50]}..."
        )

    if file_path:
        try:
            with open(file_path, "w") as f:
                f.write(file_content)
            logger.info(f"  V1 Coder: Successfully wrote to {file_path}")
            return CodeOutput(code_path=file_path, message=message)
        except IOError as e:
            logger.error(
                f"  Coder Error: Could not write to file {file_path}. Error: {e}"
            )
            return CodeOutput(
                code_path=output_target_dir,  # Return dir path on error
                message=f"Coder Error: Could not write to file {file_path}. Error: {e}",
            )
    else:  # Should not happen if logic is correct, but as a safeguard
        logger.error("  Coder Error: File path was not set.")
        return CodeOutput(
            code_path=output_target_dir,
            message="Coder Error: Internal error, file path not set.",
        )
