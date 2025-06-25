"""
workshop_manager.py - The Office of the Workshop Manager (Orchestrator)

This module houses the WorkshopManager class, the central intelligence of the
Gandalf Workshop. The Manager oversees all operations, from commissioning new
Blueprints to approving final Products for delivery. It's akin to the master
artisan or foreman who directs the workflow, assigns tasks to specialized
artisans (AI agents/crews), and ensures quality standards are met throughout
the creation process.
"""

# import json # No longer used in V1
# import yaml # No longer used in V1
from pathlib import Path

# from typing import Optional, Dict # No longer used in V1
# from datetime import datetime, timezone # No longer used in V1

# Import the mock artisan crew and data models
from gandalf_workshop.artisan_guildhall.artisans import initialize_planner_agent_v1

# from gandalf_workshop.specs.data_models import PMReview, PMReviewDecision # Not used in V1 simple loop
from gandalf_workshop.specs.data_models import (
    PlanOutput,
    CodeOutput,
    AuditOutput,
    AuditStatus,
)

# Placeholder for actual agent imports or direct function calls for V1
# from gandalf_workshop.artisan_guildhall.artisans import (
#     initialize_coder_agent_v1,
#     initialize_auditor_agent_v1
# )


class WorkshopManager:
    """
    The Workshop Manager directs the V1 workflow of the Gandalf workshop,
    sequentially invoking Planner, Coder, and Auditor agents.
    """

    def __init__(self):
        """
        Initializes the Workshop Manager for V1.
        """
        # For V1, initialization is simple.
        # Future versions might load configurations or connect to agent frameworks.
        print("Workshop Manager (V1) initialized.")

    def run_v1_commission(
        self, user_prompt: str, commission_id: str = "v1_commission"
    ) -> Path:
        """
        Orchestrates the V1 commission workflow: Planner -> Coder -> Auditor.
        Args:
            user_prompt: The initial request from the client.
            commission_id: A unique ID for this commission.
        Returns:
            Path to the final generated product if successful, otherwise raises an exception.
        """
        print(f"\n===== Starting V1 Workflow for Commission: {commission_id} =====")
        print(f"User Prompt: {user_prompt}")

        # 1. Call Planner Agent
        print(f"Workshop Manager: Invoking Planner Agent for '{commission_id}'.")
        plan_output = initialize_planner_agent_v1(user_prompt, commission_id)
        # Ensure the print statement below adheres to line length
        plan_tasks_str = str(plan_output.tasks)
        if len(plan_tasks_str) > 50:  # Arbitrary short length for log
            plan_tasks_str = plan_tasks_str[:47] + "..."
        print(f"Workshop Manager: Planner Agent returned plan: {plan_tasks_str}")

        # 2. Call Coder Agent
        # This will be replaced by actual agent call in later steps
        # coder_agent = initialize_coder_agent_v1() # Conceptual
        # code_output = coder_agent.generate_code(plan_output, commission_id)
        print(f"Workshop Manager: Invoking Coder Agent for '{commission_id}'.")
        # Mock Coder Output for now
        # Let's assume it creates a file in a temporary commission-specific directory
        commission_work_dir = Path("gandalf_workshop/commission_work") / commission_id
        commission_work_dir.mkdir(parents=True, exist_ok=True)

        if plan_output.tasks == ["Create a Python file that prints 'Hello, World!'"]:
            output_file = commission_work_dir / "hello.py"
            with open(output_file, "w") as f:
                f.write("print('Hello, World!')\n")
            code_output = CodeOutput(
                code_path=output_file, message="Python 'Hello, World!' generated."
            )
            print(
                f"Workshop Manager: Coder Agent generated code at: {code_output.code_path}"
            )
        else:
            # Generic placeholder file for other prompts
            output_file = commission_work_dir / "output.txt"
            with open(output_file, "w") as f:
                f.write(
                    f"Content for: {user_prompt}\nBased on plan: {plan_output.tasks}"
                )
            code_output = CodeOutput(
                code_path=output_file, message=f"Generated content for {user_prompt}."
            )
            print(
                f"Workshop Manager: Coder Agent generated code at: {code_output.code_path}"
            )
            # raise NotImplementedError(f"V1 Coder cannot handle plan: {plan_output.tasks}")

        # 3. Call Auditor Agent
        # This will be replaced by actual agent call in later steps
        # auditor_agent = initialize_auditor_agent_v1() # Conceptual
        # audit_output = auditor_agent.audit_code(code_output, commission_id)
        print(f"Workshop Manager: Invoking Auditor Agent for '{commission_id}'.")
        # Mock Auditor Output for now
        if code_output.code_path.name == "hello.py":
            audit_output = AuditOutput(
                status=AuditStatus.SUCCESS,
                message="Audit passed for 'Hello, World!'.",
                report_path=None,
            )
            print(
                f"Workshop Manager: Auditor Agent reported: {audit_output.status} - {audit_output.message}"
            )
        else:
            audit_output = AuditOutput(
                status=AuditStatus.SUCCESS,
                message="Audit passed for generic content.",
                report_path=None,
            )
            print(
                f"Workshop Manager: Auditor Agent reported: {audit_output.status} - {audit_output.message}"
            )
            # audit_output = AuditOutput(status=AuditStatus.FAILURE, message="Audit failed for unknown code.", report_path=None)
            # print(f"Workshop Manager: Auditor Agent reported: {audit_output.status} - {audit_output.message}")

        if audit_output.status == AuditStatus.FAILURE:
            print(
                f"Workshop Manager: Commission '{commission_id}' failed audit. Reason: {audit_output.message}"
            )
            # In a real V1, we might raise an exception or return a specific indicator of failure.
            # For now, we'll let it proceed but the message indicates failure.
            # Consider raising an exception for clearer failure handling:
            raise Exception(
                f"Audit failed for commission '{commission_id}': {audit_output.message}"
            )

        print(
            f"===== V1 Workflow for Commission: {commission_id} Completed Successfully ====="
        )
        return code_output.code_path

    # --- Methods from older, more complex workflow (commented out for V1 focus) ---
    #
    # def _get_blueprint_version(self, blueprint_path: Path) -> str:
    #     """Helper to read version from blueprint YAML."""
    #     try:
    #         with open(blueprint_path, "r") as f:
    #             content = yaml.safe_load(f)
    #         if (
    #             "revisions" in content
    #             and isinstance(content["revisions"], list)
    #             and content["revisions"]
    #         ):
    #             return content["revisions"][-1].get("version", "unknown")
    #         return content.get("version", "unknown")
    #     except Exception:  # pylint: disable=broad-except
    #         return "unknown"
    #
    # def commission_new_blueprint(self, user_prompt: str, commission_id: str) -> Path:
    #     """
    #     Assigns a new Commission to a Planner Artisan to create a Blueprint.
    #     Metaphor: "Manager gives client's request to the Head Draftsman."
    #     Args:
    #         user_prompt: The initial request from the client.
    #         commission_id: A unique ID for this new commission.
    #     Returns:
    #         Path to the generated blueprint.yaml file in the /blueprints
    #         directory.
    #     """
    #     print(
    #         (
    #             f"Workshop Manager: Commissioning new blueprint for "
    #             f"'{commission_id}' based on prompt: '{user_prompt[:50]}...'"
    #         )
    #     )
    #     blueprint_dir = Path("gandalf_workshop/blueprints") / commission_id
    #     blueprint_dir.mkdir(parents=True, exist_ok=True)
    #     blueprint_path = blueprint_dir / "blueprint.yaml"
    #     initial_version = "1.0"
    #     with open(blueprint_path, "w") as f:
    #         yaml.dump(
    #             {
    #                 "commission_id": commission_id,
    #                 "commission_title": f"Commission for {commission_id}",
    #                 "commission_type": "software_mvp",
    #                 "project_summary": user_prompt,
    #                 "key_objectives": ["Objective 1 based on prompt."],
    #                 "product_specifications": {
    #                     "type": "software",
    #                     "description": "Details to be filled by Planner.",
    #                 },
    #                 "quality_criteria": ["Criterion 1"],
    #                 "revisions": [
    #                     {
    #                         "version": initial_version,
    #                         "date": datetime.now(timezone.utc).isoformat(),
    #                         "notes": "Initial blueprint creation.",
    #                     }
    #                 ],
    #             },
    #             f,
    #             sort_keys=False,
    #         )
    #     print(
    #         (
    #             f"Workshop Manager: Placeholder blueprint generated at "
    #             f"{blueprint_path} (Version: {initial_version})"
    #         )
    #     )
    #     return blueprint_path
    #
    # def initiate_strategic_review(
    #     self, commission_id: str, blueprint_path: Path
    # ) -> Path:
    #     """
    #     Assigns a Blueprint to the PM Agent for strategic review.
    #     """
    #     print(
    #         (
    #             f"Workshop Manager: Initiating strategic review for blueprint "
    #             f"'{blueprint_path.name}' of commission '{commission_id}'."
    #         )
    #     )
    #     blueprint_version = self._get_blueprint_version(blueprint_path)
    #     pm_review_path = initialize_pm_review_crew(
    #         blueprint_path=blueprint_path,
    #         commission_id=commission_id,
    #         blueprint_version=blueprint_version,
    #     )
    #     print(
    #         (
    #             f"Workshop Manager: Strategic review completed. Report at {pm_review_path}"
    #         )
    #     )
    #     return pm_review_path
    #
    # def request_blueprint_strategic_revision(
    #     self,
    #     commission_id: str,
    #     original_blueprint_path: Path,
    #     pm_review: PMReview,
    # ) -> Path:
    #     """
    #     Simulates sending a Blueprint back to Planner for PM-feedback-based revision.
    #     """
    #     rationale_summary = pm_review.rationale[:50]
    #     log_message = (
    #         f"Workshop Manager: Requesting strategic blueprint revision for "
    #         f"'{commission_id}' based on PM feedback: {rationale_summary}..."
    #     )
    #     print(log_message)
    #     try:
    #         with open(original_blueprint_path, "r") as f:
    #             blueprint_content = yaml.safe_load(f)
    #     except Exception as e:
    #         print(
    #             f"Error reading original blueprint {original_blueprint_path}: {e}. "
    #             "Cannot revise."
    #         )
    #         raise
    #     current_revisions = blueprint_content.get("revisions", [])
    #     if not current_revisions or not isinstance(current_revisions, list):
    #         last_version_str = "1.0"
    #     else:
    #         last_version_str = current_revisions[-1].get("version", "1.0")
    #     try:
    #         major, minor = map(int, last_version_str.split("."))
    #         new_version_str = f"{major}.{minor + 1}"
    #     except ValueError:
    #         new_version_str = f"{last_version_str}_pm_rev"
    #     new_revision_note = (
    #         f"Revised based on PM Review. Feedback: {pm_review.rationale[:100]}..."
    #     )
    #     if pm_review.suggested_focus_areas_for_revision:
    #         new_revision_note += (
    #             f" Focus: {', '.join(pm_review.suggested_focus_areas_for_revision)}"
    #         )
    #     new_revision_entry = {
    #         "version": new_version_str,
    #         "date": datetime.now(timezone.utc).isoformat(),
    #         "notes": new_revision_note,
    #     }
    #     current_revisions.append(new_revision_entry)
    #     blueprint_content["revisions"] = current_revisions
    #     if (
    #         "complex" in blueprint_content.get("project_summary", "")
    #         and "simplify" in pm_review.rationale.lower()
    #     ):
    #         blueprint_content["project_summary"] = (
    #             "Revised project summary: now simple and MVP focused."
    #         )
    #     revised_blueprint_filename = f"{original_blueprint_path.stem}_rev{new_version_str.replace('.', '_')}.yaml"
    #     revised_blueprint_path = (
    #         original_blueprint_path.parent / revised_blueprint_filename
    #     )
    #     with open(revised_blueprint_path, "w") as f:
    #         yaml.dump(blueprint_content, f, sort_keys=False)
    #     print(
    #         (
    #             f"Workshop Manager: Placeholder revised blueprint "
    #             f"(Version {new_version_str}) generated at {revised_blueprint_path}"
    #         )
    #     )
    #     return revised_blueprint_path
    #
    # def _execute_pm_review_cycle(
    #     self, commission_id: str, current_blueprint_path: Path
    # ) -> Optional[Path]:
    #     """
    #     Manages the iterative PM review cycle for a blueprint.
    #     """
    #     for i in range(self.max_pm_review_cycles):
    #         cycle_msg = (
    #             f"PM Review Cycle {i+1}/{self.max_pm_review_cycles} "
    #             f"for {commission_id}"
    #         )
    #         print(cycle_msg)
    #         pm_review_report_path = self.initiate_strategic_review(
    #             commission_id=commission_id, blueprint_path=current_blueprint_path
    #         )
    #         with open(pm_review_report_path, "r") as f:
    #             pm_review_data = json.load(f)
    #         pm_review = PMReview(**pm_review_data)
    #         if pm_review.decision == PMReviewDecision.APPROVED:
    #             print(
    #                 (
    #                     f"Workshop Manager: Blueprint {current_blueprint_path.name} "
    #                     f"APPROVED by PM."
    #                 )
    #             )
    #             return current_blueprint_path
    #         elif pm_review.decision == PMReviewDecision.REVISION_REQUESTED:
    #             print(
    #                 (
    #                     f"Workshop Manager: Blueprint {current_blueprint_path.name} "
    #                     f"REVISION REQUESTED by PM."
    #                 )
    #             )
    #             if i < self.max_pm_review_cycles - 1:
    #                 current_blueprint_path = self.request_blueprint_strategic_revision(
    #                     commission_id=commission_id,
    #                     original_blueprint_path=current_blueprint_path,
    #                     pm_review=pm_review,
    #                 )
    #             else:
    #                 print(
    #                     (
    #                         f"Workshop Manager: Max PM review cycles reached for "
    #                         f"{commission_id}. Blueprint not approved."
    #                     )
    #                 )
    #                 return None
    #         else:
    #             print(
    #                 (
    #                     f"Workshop Manager: Unknown PM review decision: "
    #                     f"{pm_review.decision}. Halting."
    #                 )
    #             )
    #             return None
    #     return None
    #
    # def execute_full_commission_workflow(
    #     self, user_prompt: str, commission_id: str
    # ) -> bool:
    #     """
    #     Orchestrates the full commission workflow from blueprinting to (mocked) delivery.
    #     """
    #     print(f"\n===== Starting Full Workflow for Commission: {commission_id} =====")
    #     initial_blueprint_path = self.commission_new_blueprint(
    #         user_prompt=user_prompt, commission_id=commission_id
    #     )
    #     approved_blueprint_path = self._execute_pm_review_cycle(
    #         commission_id, initial_blueprint_path
    #     )
    #     if not approved_blueprint_path:
    #         print(
    #             (
    #                 f"Workshop Manager: Commission '{commission_id}' halted due to "
    #                 f"failed PM review process."
    #             )
    #         )
    #         return False
    #     print(
    #         (
    #             f"Workshop Manager: PM review approved. Proceeding with blueprint: "
    #             f"{approved_blueprint_path.name}"
    #         )
    #     )
    #     product_path_v1 = self.request_product_generation_or_revision(
    #         commission_id=commission_id, blueprint_path=approved_blueprint_path
    #     )
    #     inspection_report_v1_path = self.initiate_quality_inspection(
    #         commission_id=commission_id,
    #         product_to_inspect_path=product_path_v1,
    #         blueprint_path=approved_blueprint_path,
    #     )
    #     print(f"Workshop Manager: Assuming QA passed for {commission_id} (mock).")
    #     self.finalize_commission_and_deliver(
    #         commission_id=commission_id,
    #         final_product_path=product_path_v1,
    #         final_inspection_report_path=inspection_report_v1_path,
    #     )
    #     print(
    #         (
    #             f"===== Full Workflow for Commission: {commission_id} "
    #             "Completed Successfully ====="
    #         )
    #     )
    #     return True
    #
    # def request_product_generation_or_revision(
    #     self,
    #     commission_id: str,
    #     blueprint_path: Path,
    #     current_product_path: Optional[Path] = None,
    #     previous_inspection_report_path: Optional[Path] = None,
    # ) -> Path:
    #     """
    #     Assigns a Coder Artisan to build or revise a Product.
    #     """
    #     print(
    #         (
    #             f"Workshop Manager: Requesting product generation/revision for "
    #             f"'{commission_id}'."
    #         )
    #     )
    #     product_dir = (
    #         Path("gandalf_workshop/commissions_in_progress")
    #         / commission_id
    #         / "product_v_scaffold"
    #     )
    #     product_dir.mkdir(parents=True, exist_ok=True)
    #     product_file_path = product_dir / "product_content.txt"
    #     with open(product_file_path, "w") as f:
    #         f.write(f"Placeholder product for {commission_id}\n")
    #         if current_product_path:
    #             f.write(f"Based on revision of {current_product_path.name}\n")
    #     print(
    #         (
    #             f"Workshop Manager: Placeholder product generated at "
    #             f"{product_file_path}"
    #         )
    #     )
    #     return product_file_path
    #
    # def initiate_quality_inspection(
    #     self, commission_id: str, product_to_inspect_path: Path, blueprint_path: Path
    # ) -> Path:
    #     """
    #     Assigns an Inspector Artisan to conduct Quality Inspection.
    #     """
    #     print(
    #         (
    #             f"Workshop Manager: Initiating quality inspection for product "
    #             f"'{product_to_inspect_path.name}' of commission "
    #             f"'{commission_id}'."
    #         )
    #     )
    #     report_dir = Path("gandalf_workshop/quality_control_lab") / commission_id
    #     report_dir.mkdir(parents=True, exist_ok=True)
    #     report_name = f"{product_to_inspect_path.parent.name}_inspection_report.json"
    #     report_path = report_dir / report_name
    #     with open(report_path, "w") as f:
    #         json.dump(
    #             {
    #                 "commission_id": commission_id,
    #                 "product_version_inspected": product_to_inspect_path.parent.name,
    #                 "status": "placeholder_inspection_report",
    #                 "summary": "Scaffold report - no actual inspection performed.",
    #             },
    #             f,
    #             indent=2,
    #         )
    #     print(
    #         (
    #             f"Workshop Manager: Placeholder inspection report generated at "
    #             f"{report_path}"
    #         )
    #     )
    #     return report_path
    #
    # def finalize_commission_and_deliver(
    #     self,
    #     commission_id: str,
    #     final_product_path: Path,
    #     final_inspection_report_path: Path,
    # ) -> None:
    #     """
    #     Packages final Product and Inspection Report for delivery.
    #     """
    #     print(f"Workshop Manager: Finalizing commission '{commission_id}'.")
    #     completed_dir = Path("gandalf_workshop/completed_commissions") / commission_id
    #     completed_dir.mkdir(parents=True, exist_ok=True)
    #     if final_product_path.is_file():
    #         dest_product_name = f"final_product_{final_product_path.name}"
    #         with open(completed_dir / dest_product_name, "w") as f:
    #             f.write(
    #                 f"Simulated copy of {final_product_path.name} for "
    #                 f"commission {commission_id}\n"
    #             )
    #     else:
    #         dest_info_name = f"final_product_info_for_{final_product_path.name}.txt"
    #         with open(completed_dir / dest_info_name, "w") as f:
    #             f.write(
    #                 f"Simulated copy of product directory {final_product_path} "
    #                 f"for commission {commission_id}\n"
    #             )
    #     dest_report_name = (
    #         f"final_inspection_report_{final_inspection_report_path.name}"
    #     )
    #     with open(completed_dir / dest_report_name, "w") as f:
    #         f.write(
    #             f"Simulated copy of {final_inspection_report_path.name} "
    #             f"for commission {commission_id}\n"
    #         )
    #     print(
    #         (
    #             f"Workshop Manager: Commission '{commission_id}' finalized and "
    #             f"artifacts 'moved' to {completed_dir}."
    #         )
    #     )
    #
    # def request_blueprint_revision(
    #     self,
    #     commission_id: str,
    #     original_blueprint_path: Path,
    #     failure_history: Dict[str, any],
    # ) -> Path:
    #     """
    #     Sends Blueprint to Planner for revision due to fundamental design issues.
    #     """
    #     print(
    #         (
    #             f"Workshop Manager: Requesting blueprint revision for "
    #             f"'{commission_id}'."
    #         )
    #     )
    #     revised_blueprint_name = f"{original_blueprint_path.stem}_revised.yaml"
    #     revised_blueprint_path = original_blueprint_path.parent / revised_blueprint_name
    #     with open(revised_blueprint_path, "w") as f:
    #         f.write(f"# Revised Blueprint for {commission_id}\n")
    #         f.write(f"commission_id: {commission_id}\n")
    #         f.write("status: placeholder_revised_blueprint\n")
    #         f.write(f"based_on_failures: {str(failure_history)}\n")
    #     print(
    #         (
    #             f"Workshop Manager: Placeholder revised blueprint generated at "
    #             f"{revised_blueprint_path}"
    #         )
    #     )
    #     return revised_blueprint_path


# if __name__ == "__main__":
# # Example of how the manager might be used (for testing purposes)
# # This now demonstrates the full workflow including PM review.
# manager = WorkshopManager(
#     max_pm_review_cycles=2
# )  # Test with 2 cycles for PM review
#
# # Test Case 1: Prompt to be rejected by PM, then revised and approved.
# test_commission_id_1 = "test_commission_pm_cycle_001"
# test_prompt_1 = (
#     "Create a very complex AI-driven platform for advanced quantum "
#     "particle simulation."
# )  # Mock PM rejects "complex"
# print(
#     (
#         f"\n--- Test Case 1: '{test_commission_id_1}' "
#         "(expect PM revision then approval) ---"
#     )
# )
# success_1 = manager.execute_full_commission_workflow(
#     user_prompt=test_prompt_1, commission_id=test_commission_id_1
# )
# print(f"Test Case 1 completed. Success: {success_1}")
# if success_1:
#     # Check if a revised blueprint was created
#     expected_bp_name_part = "_rev1_1.yaml"
#     bp_list = list(
#         (Path("gandalf_workshop/blueprints") / test_commission_id_1).glob("*.yaml")
#     )
#     found_revised = any(
#         expected_bp_name_part in bp.name
#         for bp in bp_list
#         if bp.name != "blueprint.yaml"
#     )
#     print(
#         (
#             f"Revised blueprint for Test Case 1 found: {found_revised} "
#             "(expected True if PM revision occurred)"
#         )
#     )
#
# # Test Case 2: Prompt that should be approved by PM on first try.
# test_commission_id_2 = "test_commission_pm_direct_approval_002"
# test_prompt_2 = "Create a simple command-line calculator MVP."
# print(
#     (
#         f"\n--- Test Case 2: '{test_commission_id_2}' "
#         "(expect direct PM approval) ---"
#     )
# )
# success_2 = manager.execute_full_commission_workflow(
#     user_prompt=test_prompt_2, commission_id=test_commission_id_2
# )
# print(f"Test Case 2 completed. Success: {success_2}")
#
# # Test Case 3: Prompt that might fail PM review cycles.
# manager_strict_pm = WorkshopManager(max_pm_review_cycles=1)
# test_commission_id_3 = "test_commission_pm_strict_fail_003"
# test_prompt_3 = (
#     "Develop a highly intricate enterprise system with many legacy " "integrations."
# )
# print(
#     (
#         f"\n--- Test Case 3: '{test_commission_id_3}' "
#         "(PM review with strict cycles) ---"
#     )
# )
# # Mock strategic revision makes summary "simple", so it passes on 2nd attempt.
# # With max_pm_review_cycles=1, it means 1 attempt. If rejected, it stops.
# manager_one_shot_pm = WorkshopManager(max_pm_review_cycles=1)
# print("Testing with manager_one_shot_pm (max_pm_review_cycles=1)")
# success_3 = manager_one_shot_pm.execute_full_commission_workflow(
#     user_prompt=test_prompt_3,  # This will be "complex"
#     commission_id=test_commission_id_3,
# )
# print(
#     (
#         f"Test Case 3 completed. Success: {success_3} "
#         "(expected False if initially complex and max_cycles=1)"
#     )
# )
#
# # Example of old-style blueprint revision (technical, not strategic)
# print("\n--- Test original blueprint revision method (technical) ---")
# if success_2:
#     bp_path_tech_rev = (
#         Path("gandalf_workshop/blueprints")
#         / test_commission_id_2
#         / "blueprint.yaml"
#     )
#     if bp_path_tech_rev.exists():
#         failure_data = {"reason": "Technical flaw found by QA", "attempts": 1}
#         print("Calling legacy request_blueprint_revision (not PM flow)")
#         try:
#             manager.request_blueprint_revision(
#                 commission_id=test_commission_id_2,
#                 original_blueprint_path=bp_path_tech_rev,
#                 failure_history=failure_data,
#             )
#             print(
#                 (
#                     "Legacy request_blueprint_revision called successfully for "
#                     f"{test_commission_id_2}."
#                 )
#             )
#         except Exception as e:
#             print(f"Error calling legacy request_blueprint_revision: {e}")
#     else:
#         print(
#             (
#                 f"Skipping legacy request_blueprint_revision test, blueprint "
#                 f"not found: {bp_path_tech_rev}"
#             )
#         )
#
# print("\nAll Workshop Manager __main__ tests completed.")
