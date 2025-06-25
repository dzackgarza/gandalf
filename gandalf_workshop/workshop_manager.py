"""
workshop_manager.py - The Office of the Workshop Manager (Orchestrator)

This module houses the WorkshopManager class, the central intelligence of the
Gandalf Workshop. The Manager oversees all operations, from commissioning new
Blueprints to approving final Products for delivery. It's akin to the master
artisan or foreman who directs the workflow, assigns tasks to specialized
artisans (AI agents/crews), and ensures quality standards are met throughout
the creation process.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any # Added Optional, Dict, Any

# from datetime import datetime, timezone # No longer used in V1

# Import the LLMProviderManager
from gandalf_workshop.llm_provider_manager import LLMProviderManager

# Import the mock artisan crew and data models
from gandalf_workshop.artisan_guildhall.artisans import (
    initialize_live_planner_agent,
    initialize_live_coder_agent,
    initialize_auditor_agent_v1,
    initialize_live_auditor_agent,
    invoke_oracle_llm_for_advice,
    initialize_help_example_extractor_agent, # Added Help Example Extractor
)
# Import the alternative prompt
from gandalf_workshop.artisan_guildhall.prompts import CODER_CHARTER_PROMPT_ALT_1
import subprocess # For running help and echo tests

# from gandalf_workshop.specs.data_models import PMReview, PMReviewDecision # Not used in V1 simple loop
from gandalf_workshop.specs.data_models import (
    PlanOutput,
    CodeOutput,
    AuditOutput,
    AuditStatus,
)
from gandalf_workshop.validators import validate_code_structure, run_flake8_validation # Import new validators

logger = logging.getLogger(__name__)


class WorkshopManager:
    # --- Parameters for Retry Limits and Strategy Controls ---
    MAX_TOTAL_ATTEMPTS = 50  # Overall limit to prevent true infinite loops in catastrophic scenarios
    MAX_ATTEMPTS_PER_STRATEGY = 3  # Number of retries with one strategy before switching
    MAX_STRATEGY_CYCLES = 2        # Number of times to cycle through all available strategies

    # Define strategies (can be an Enum later if preferred)
    STRATEGIES = [
        "DEFAULT",
        "INCREASE_TEMPERATURE",
        "ALTERNATIVE_PROMPT_1",
        "REPLAN_WITH_ERROR_CONTEXT",
        "ORACLE_ASSISTANCE",
    ]
    # --- End Parameters ---

    def __init__(self, preferred_llm_provider: Optional[str] = None):
        logger.info("Workshop Manager (V1) initializing...")
        self.llm_provider_manager = LLMProviderManager()
        self.llm_config: Optional[
            Dict[str, Any]
        ] = self.llm_provider_manager.get_llm_provider(
            preferred_provider=preferred_llm_provider
        )

        if not self.llm_config:
            logger.error(
                "Workshop Manager: CRITICAL - No operational LLM provider found. Cannot proceed with commissions."
            )
        else:
            logger.info(
                f"Workshop Manager: Successfully configured LLM provider: {self.llm_config.get('provider_name', 'Unknown')}"
            )

        # Initialize strategy-related state for each WorkshopManager instance
        self.current_strategy_index = 0
        self.attempts_this_strategy = 0
        self.total_strategy_cycles_completed = 0
        self.overall_attempt_count = 0

        logger.info("Workshop Manager (V1) initialized.")

    def _get_next_strategy(self) -> str:
        self.attempts_this_strategy = 0 # Reset counter for the new strategy
        self.current_strategy_index += 1
        if self.current_strategy_index >= len(self.STRATEGIES):
            self.current_strategy_index = 0
            self.total_strategy_cycles_completed += 1
            logger.info(
                f"Completed strategy cycle {self.total_strategy_cycles_completed}. "
                f"Resetting to first strategy: {self.STRATEGIES[self.current_strategy_index]}"
            )
        return self.STRATEGIES[self.current_strategy_index]

    def run_v1_commission(
        self, user_prompt: str, commission_id: str = "v1_commission"
    ) -> Path:
        print(f"DEBUG_WM: Entered run_v1_commission with commission_id: {commission_id}") # DEBUG
        logger.info(
            f"===== Starting V1 Workflow for Commission: {commission_id} ====="
        )
        logger.info(f"User Prompt: {user_prompt}")

        print(f"DEBUG_WM: Attempting to create output directory for {commission_id}") # DEBUG
        commission_base_output_dir = Path("outputs") / commission_id
        try:
            commission_base_output_dir.mkdir(parents=True, exist_ok=True)
            print(f"DEBUG_WM: Successfully ensured directory exists: {commission_base_output_dir}") # DEBUG
        except Exception as e_mkdir:
            print(f"DEBUG_WM: ERROR creating directory {commission_base_output_dir}: {e_mkdir}") # DEBUG
            logger.error(f"Failed to create base output directory {commission_base_output_dir}: {e_mkdir}", exc_info=True)
            raise # Re-raise the error to ensure it's not swallowed

        logger.info(
            f"Workshop Manager: Ensured base output directory exists: {commission_base_output_dir}"
        )

        if not self.llm_config:
            logger.error(
                f"Workshop Manager: Cannot run commission '{commission_id}'. No LLM provider configured."
            )
            raise ConnectionError(
                "LLM provider not available. Commission cannot be processed."
            )

        # Reset strategy controls for this specific commission run
        self.current_strategy_index = 0
        self.attempts_this_strategy = 0
        self.total_strategy_cycles_completed = 0
        self.overall_attempt_count = 0

        active_strategy = self.STRATEGIES[self.current_strategy_index]

        logger.info(
            f"Workshop Manager: Invoking Initial Live Planner Agent for '{commission_id}'."
        )
        plan_output = initialize_live_planner_agent(
            user_prompt, commission_id, llm_config=self.llm_config.copy() # Pass a copy
        )
        plan_tasks_str = str(plan_output.tasks)
        if len(plan_tasks_str) > 50:
            plan_tasks_str = plan_tasks_str[:47] + "..."
        logger.info(
            f"Workshop Manager: Initial Planner Agent returned plan: {plan_tasks_str}"
        )

        last_audit_failure_message = "No audit failures yet."
        code_output: Optional[CodeOutput] = None # Ensure code_output is defined for the final return

        while True: # Main retry loop
            self.overall_attempt_count += 1
            self.attempts_this_strategy += 1

            if self.overall_attempt_count > self.MAX_TOTAL_ATTEMPTS:
                logger.error(
                    f"Commission '{commission_id}' exceeded MAX_TOTAL_ATTEMPTS ({self.MAX_TOTAL_ATTEMPTS}). Aborting."
                )
                raise Exception(f"Max total attempts reached for '{commission_id}'.")

            logger.info(
                f"Workshop Manager: Overall Attempt {self.overall_attempt_count}/{self.MAX_TOTAL_ATTEMPTS}, "
                f"Strategy: {active_strategy} (Attempt {self.attempts_this_strategy}/{self.MAX_ATTEMPTS_PER_STRATEGY}, "
                f"Cycle {self.total_strategy_cycles_completed + 1}/{self.MAX_STRATEGY_CYCLES}) for '{commission_id}'."
            )

            current_llm_config_for_attempt = self.llm_config.copy()

            # --- Apply strategy-specific modifications ---
            if active_strategy == "INCREASE_TEMPERATURE":
                new_temp = 0.8 # Fixed higher temperature for this strategy
                logger.info(f"Strategy '{active_strategy}': Setting LLM temperature to {new_temp} for Coder and relevant Auditors/Planners.")
                current_llm_config_for_attempt['temperature'] = new_temp
            else:
                # For DEFAULT or other strategies, ensure temperature is not lingering from a previous strategy attempt
                # or set to a model's default if that's preferred. Popping it means provider default.
                current_llm_config_for_attempt.pop('temperature', None)


            if active_strategy == "REPLAN_WITH_ERROR_CONTEXT":
                if self.overall_attempt_count == 1 and self.attempts_this_strategy == 1:
                    # Avoid re-planning if this strategy is chosen first and it's the very first attempt overall.
                    # Or if it's the first attempt *for this strategy* in its current cycle.
                    logger.info(f"Strategy '{active_strategy}': First attempt with this strategy, using existing plan for '{commission_id}'.")
                else:
                    logger.info(f"Strategy '{active_strategy}': Re-invoking planner for '{commission_id}'.")
                    replan_prompt = f"Original request: {user_prompt}\nPrevious attempt failed. Last audit feedback: {last_audit_failure_message}\nPlease generate a revised plan."
                    # The planner will use current_llm_config_for_attempt (which might have its own temp setting for this strategy)
                    plan_output = initialize_live_planner_agent(
                        replan_prompt, commission_id, llm_config=current_llm_config_for_attempt
                    )
                    logger.info(f"Re-planner returned new plan: {plan_output.tasks}")
            # --- End strategy-specific modifications ---

            # Determine coder prompt charter based on strategy
            coder_prompt_charter_to_use: Optional[str] = None
            if active_strategy == "ALTERNATIVE_PROMPT_1":
                logger.info(f"Strategy '{active_strategy}': Using CODER_CHARTER_PROMPT_ALT_1.")
                coder_prompt_charter_to_use = CODER_CHARTER_PROMPT_ALT_1

            code_output = initialize_live_coder_agent(
                plan_input=plan_output, # Use current plan_output (might have been updated by REPLAN)
                commission_id=commission_id,
                output_target_dir_base=commission_base_output_dir,
                llm_config=current_llm_config_for_attempt,
                prompt_charter_override=coder_prompt_charter_to_use
            )
            logger.info(
                f"Workshop Manager: Coder Agent completed. Path: {code_output.code_path}, Msg: {code_output.message}"
            )

            attempt_successful = False
            if not code_output.code_path.is_file() or not code_output.code_path.exists():
                logger.error(
                    f"Coder Agent failed to create file at {code_output.code_path}. Msg: {code_output.message}."
                )
                last_audit_failure_message = f"Coder failed to produce a file. Message: {code_output.message}"
            else:
                syntax_audit_output = initialize_auditor_agent_v1(
                    code_input=code_output, commission_id=commission_id
                )
                logger.info(
                    f"Syntax Auditor: Status: {syntax_audit_output.status}, Msg: {syntax_audit_output.message}"
                )
                if syntax_audit_output.status == AuditStatus.SUCCESS:
                    try:
                        with open(code_output.code_path, "r", encoding="utf-8") as f:
                            generated_code_str = f.read()

                        live_audit_output = initialize_live_auditor_agent(
                            generated_code=generated_code_str,
                            plan_input=plan_output,
                            commission_id=commission_id,
                            llm_config=current_llm_config_for_attempt,
                        )
                        logger.info(
                            f"Live Auditor: Status: {live_audit_output.status}, Msg: {live_audit_output.message}"
                        )
                        if live_audit_output.status == AuditStatus.SUCCESS:
                            attempt_successful = True
                        else:
                            last_audit_failure_message = live_audit_output.message if live_audit_output.message else "Live audit failed without specific message."
                    except Exception as e:
                        logger.error(f"Failed to read/audit code file {code_output.code_path}: {e}", exc_info=True)
                        last_audit_failure_message = f"Error during live audit file read: {str(e)}"
                else:
                    last_audit_failure_message = syntax_audit_output.message if syntax_audit_output.message else "Syntax audit failed without specific message."

            if attempt_successful:
                logger.info(
                    f"Commission '{commission_id}' PASSED with strategy '{active_strategy}' on overall attempt {self.overall_attempt_count}."
                )
                break

            logger.warning(
                f"Attempt {self.attempts_this_strategy} for strategy '{active_strategy}' FAILED for '{commission_id}'. Last error: {last_audit_failure_message}"
            )

            if self.attempts_this_strategy >= self.MAX_ATTEMPTS_PER_STRATEGY:
                if self.total_strategy_cycles_completed >= self.MAX_STRATEGY_CYCLES and \
                   self.current_strategy_index == len(self.STRATEGIES) -1:
                     logger.warning(
                        f"Commission '{commission_id}' has completed {self.total_strategy_cycles_completed + 1} full strategy cycles "
                        f"and exhausted attempts for all strategies in the current cycle. "
                        f"The MAX_STRATEGY_CYCLES ({self.MAX_STRATEGY_CYCLES}) limit has been effectively reached or exceeded. "
                        f"Loop will continue (up to MAX_TOTAL_ATTEMPTS), cycling strategies again."
                    )

                previous_strategy = active_strategy
                active_strategy = self._get_next_strategy() # This also resets self.attempts_this_strategy
                logger.info(
                    f"Switching strategy for '{commission_id}' from '{previous_strategy}' to '{active_strategy}'."
                )

            logger.info(f"Retrying commission '{commission_id}' (next attempt with strategy '{active_strategy}')...")

        if not code_output: # Should not happen if loop runs at least once and coder produces output
             logger.error(f"Commission '{commission_id}' ended without valid code_output.")
             raise Exception(f"Workflow ended unexpectedly without code output for '{commission_id}'.")

        logger.info(
            f"===== V1 Workflow for Commission: {commission_id} Completed Successfully after {self.overall_attempt_count} attempt(s) ====="
        )
        return code_output.code_path

    # --- Methods from older, more complex workflow (commented out for V1 focus) ---
    # All legacy methods previously here have been removed.
