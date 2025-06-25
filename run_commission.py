import argparse
import os
import sys
import time # Added for sleep in retry loops
from pathlib import Path
from dotenv import load_dotenv

import shutil # For file copying in prepare_for_audit

# Add gandalf_workshop to Python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Load environment variables from .env file FIRST
load_dotenv() # Ensures API keys are loaded before any other imports that might need them

try:
    from gandalf_workshop.crews_hardcoded import PlannerCrew, CoderCrew, create_commission_id
    from gandalf_workshop.llm_manager import SmartLLMProviderManager
    # Import specific Langchain chat model classes if SmartLLMProviderManager doesn't return an instance
    # For now, assuming SmartLLMProviderManager.get_current_llm_instance() returns a usable LLM object
except ImportError as e:
    print(f"Error during initial imports: {e}")
    sys.exit(f"Could not resolve imports. Original error: {e}. Exiting.")


MAX_RETRIES = 5 # Max retries for LLM calls if they fail and manager cycles provider/model

def main():
    parser = argparse.ArgumentParser(description="Run a commission for the Gandalf project.")
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="The high-level prompt for the commission."
    )
    parser.add_argument(
        "--commission-id",
        type=str,
        default=None,
        help="Optional: A specific ID for the commission. If not provided, one will be generated from the prompt."
    )
    args = parser.parse_args()

    print(f"Received prompt: \"{args.prompt}\"")

    # --- Initialize SmartLLMProviderManager ---
    print("\nInitializing Smart LLM Provider Manager...")
    llm_manager = SmartLLMProviderManager()
    if not llm_manager.current_provider_name:
        print("ERROR: No LLM provider could be initialized by SmartLLMProviderManager. Check API keys and .env setup.")
        print("Manager Status:")
        try:
            # Assuming get_status_report is robust enough to be called even if current_provider_name is None
            status_report = llm_manager.get_status_report()
            import json
            print(json.dumps(status_report, indent=2))
        except Exception as report_e:
            print(f"Could not get status report: {report_e}")
        sys.exit("LLM Provider Initialization Failed.")

    print(f"SmartLLMProviderManager initialized. Initial provider: {llm_manager.current_provider_name}")
    # Accessing provider state safely
    if llm_manager.current_provider_name and llm_manager.current_provider_name in llm_manager.providers:
        current_model_for_provider = llm_manager.providers[llm_manager.current_provider_name].get_current_model()
        print(f"Initial model for provider {llm_manager.current_provider_name}: {current_model_for_provider}")
    else:
        # This case should have been caught by RuntimeError in SmartLLMProviderManager.__init__
        # but as a defensive measure:
        print("ERROR: llm_manager.current_provider_name is not set or invalid after initialization!")
        sys.exit("LLM Provider state error after initialization.")


    # --- Direct LLM Diagnostic Call ---
    print("\n--- Performing Direct LLM Diagnostic Call ---")
    test_llm_instance = None
    try:
        print("Attempting to get LLM instance for diagnostic call...")
        test_llm_instance = llm_manager.get_current_llm_instance() # This might raise RuntimeError if no instance can be made

        # get_current_llm_instance should raise error if it can't provide one.
        # So, if we are here, test_llm_instance should be valid.
        # However, adding an explicit check for robustness:
        if not test_llm_instance:
            print("❌ FATAL: SmartLLMProviderManager.get_current_llm_instance() returned None unexpectedly.")
            sys.exit("FATAL: Could not obtain LLM instance for diagnostic.")

        # Ensure current_provider_name is valid before trying to access its state for printing
        current_provider_for_diag = llm_manager.current_provider_name
        current_model_for_diag = "N/A"
        if current_provider_for_diag and current_provider_for_diag in llm_manager.providers:
            current_model_for_diag = llm_manager.providers[current_provider_for_diag].get_current_model()

        print(f"Attempting direct invoke with: {current_provider_for_diag} - {current_model_for_diag}")

        response = test_llm_instance.invoke("Hello! This is a diagnostic test.")
        print(f"✅ Direct LLM invoke successful. Response (type: {type(response)}):")
        if hasattr(response, 'content'):
            print(response.content[:200] + "..." if len(response.content) > 200 else response.content)
        else:
            print(str(response)[:200] + "..." if len(str(response)) > 200 else str(response))
        llm_manager.record_success()

    except RuntimeError as e: # Catch RuntimeErrors from llm_manager
        print(f"❌ FATAL: Could not obtain LLM for diagnostic call due to RuntimeError: {e}")
        sys.exit(f"FATAL: LLM acquisition failed: {e}")
    except Exception as direct_e: # Catch other errors like API errors from .invoke()
        print(f"❌ FATAL: Direct diagnostic LLM call failed: {type(direct_e).__name__}: {direct_e}")
        import traceback
        traceback.print_exc()
        if llm_manager.current_provider_name:
            llm_manager.handle_llm_failure(str(direct_e))
        sys.exit("FATAL: Direct diagnostic LLM call failed. Aborting.")
    print("--- Direct LLM Diagnostic Call Complete ---")


    # --- Commission ID ---
    if args.commission_id:
        commission_id = args.commission_id
    else:
        commission_id = create_commission_id(args.prompt)
    print(f"Commission ID: {commission_id}")

    # --- Workspace Setup ---
    workspace_root = Path("workspace") / commission_id
    workspace_root.mkdir(parents=True, exist_ok=True)
    print(f"Workspace for this commission: {workspace_root.resolve()}")

    # --- Stage 1: Run Planner Crew ---
    print("\nStarting Planner Crew...")
    blueprint_file_path, feature_file_path = None, None # Initialize
    for attempt in range(MAX_RETRIES):
        try:
            selected_llm_instance = llm_manager.get_current_llm_instance()
            if not selected_llm_instance:
                 print(f"Attempt {attempt + 1}/{MAX_RETRIES}: Failed to get LLM instance from manager. Retrying if possible...")
                 # Manager might have switched provider, or waiting for cooldown.
                 # A short delay might be useful if it's a cooldown scenario.
                 time.sleep(5) # Wait 5 seconds before retrying to get an instance
                 continue

            planner = PlannerCrew(
                commission_prompt=args.prompt,
                commission_id=commission_id,
                llm_instance=selected_llm_instance
            )
            blueprint_file_path, feature_file_path = planner.run()
            llm_manager.record_success()
            print(f"Planner Crew finished successfully on attempt {attempt + 1}.")
            print(f"  Blueprint generated: {blueprint_file_path}")
            print(f"  Feature file generated: {feature_file_path}")
            break # Success
        except Exception as e:
            print(f"ERROR: Planner Crew failed on attempt {attempt + 1}/{MAX_RETRIES}: {e}")
            import traceback
            traceback.print_exc()
            failure_report = llm_manager.handle_llm_failure(str(e))
            print(f"LLM Manager failure report: {failure_report}")

            if attempt + 1 >= MAX_RETRIES:
                print("Max retries reached for Planner Crew.")
                break # Exit loop, will be caught by 'else'

            if not failure_report.get("switch_occurred"):
                print("No provider/model switch occurred, but retrying...")
                time.sleep(10) # Longer sleep if no switch, could be transient issue
            # If a switch did occur, loop continues to retry with new config immediately

    else: # Loop finished without break (all retries failed)
        print("Planner Crew failed after all retries.") # Added print for clarity
        sys.exit("Planner Crew execution failed after all retries.")


    # --- Stage 2: Run Coder Crew ---
    print("\nStarting Coder Crew...")
    app_py, test_py, bdd_steps_py, req_txt = None, None, None, None # Initialize
    for attempt in range(MAX_RETRIES):
        try:
            selected_llm_instance = llm_manager.get_current_llm_instance()
            if not selected_llm_instance:
                 print(f"Attempt {attempt + 1}/{MAX_RETRIES}: Failed to get LLM instance for Coder. Retrying...")
                 time.sleep(5)
                 continue

            coder = CoderCrew(
                commission_id=commission_id,
                blueprint_path=blueprint_file_path,
                feature_file_path=feature_file_path,
                llm_instance=selected_llm_instance
            )
            app_py, test_py, bdd_steps_py, req_txt = coder.run()
            llm_manager.record_success()
            print(f"Coder Crew finished successfully on attempt {attempt + 1}.")
            print(f"  Application code: {app_py}")
            print(f"  Unit tests: {test_py}")
            print(f"  BDD step definitions: {bdd_steps_py}")
            if req_txt:
                print(f"  Requirements.txt: {req_txt}")
            print(f"\nAll generated artifacts for commission '{commission_id}' are in: {workspace_root.resolve()}")
            break # Success
        except Exception as e:
            print(f"ERROR: Coder Crew failed on attempt {attempt + 1}/{MAX_RETRIES}: {e}")
            import traceback
            traceback.print_exc()
            failure_report = llm_manager.handle_llm_failure(str(e))
            print(f"LLM Manager failure report: {failure_report}")

            if attempt + 1 >= MAX_RETRIES:
                print("Max retries reached for Coder Crew.")
                break # Exit loop, will be caught by 'else'

            if not failure_report.get("switch_occurred"):
                print("No provider/model switch occurred, but retrying Coder...")
                time.sleep(10)
            # If a switch did occur, loop continues to retry with new config immediately

    else: # Loop finished without break (all retries failed)
        print("Coder Crew failed after all retries.") # Added print for clarity
        sys.exit("Coder Crew execution failed after all retries.")

    print("\nCommission generation pipeline completed successfully!")

    # --- Stage 3: Prepare for Audit ---
    print("\nPreparing generated files for audit...")
    # Define paths for audit (expected by run_full_audit.sh)
    # These paths should match what run_full_audit.sh expects.
    # gandalf_workshop/app.py, gandalf_workshop/tests/test_app.py etc.
    # For simplicity, we will name the app 'app.py' for audit purposes.
    audit_app_name = "app"
    audit_base_dir = Path("gandalf_workshop")
    audit_tests_dir = audit_base_dir / "tests"
    audit_features_dir = audit_tests_dir / "features"
    audit_steps_dir = audit_tests_dir / "step_definitions"

    # Create necessary directories for audit
    audit_base_dir.mkdir(exist_ok=True)
    audit_tests_dir.mkdir(exist_ok=True)
    audit_features_dir.mkdir(exist_ok=True)
    audit_steps_dir.mkdir(exist_ok=True)

    # Create __init__.py files
    (audit_base_dir / "__init__.py").touch(exist_ok=True)
    (audit_tests_dir / "__init__.py").touch(exist_ok=True)
    (audit_steps_dir / "__init__.py").touch(exist_ok=True)

    # Generated file paths from CoderCrew
    # app_py, test_py, bdd_steps_py are Path objects
    # feature_file_path is also a Path object (from Planner, used by Coder)
    # The CoderCrew already copies the feature file to its coding_outputs/features/ directory.
    # We need to get that path. The Coder.run() returns the source paths.
    # Let's assume coder.feature_file_path_in_coding_outputs can give us this.
    # Or, more simply, reconstruct it based on feature_file_path.name

    # Source paths (from workspace)
    source_app_py = app_py
    source_test_py = test_py
    source_bdd_steps_py = bdd_steps_py
    # The feature file used by CoderCrew for BDD step generation is located at:
    # workspace/commission_id/coding_outputs/features/commission_expectations.feature
    source_bdd_feature_file = workspace_root / "coding_outputs" / "features" / feature_file_path.name

    # Destination paths (for audit script)
    dest_app_py = audit_base_dir / f"{audit_app_name}.py"
    dest_test_py = audit_tests_dir / f"test_{audit_app_name}.py"
    dest_bdd_steps_py = audit_steps_dir / f"{audit_app_name}_steps.py" # or just app_steps.py
    dest_bdd_feature_file = audit_features_dir / feature_file_path.name

    files_to_copy = [
        (source_app_py, dest_app_py),
        (source_test_py, dest_test_py),
        (source_bdd_steps_py, dest_bdd_steps_py),
        (source_bdd_feature_file, dest_bdd_feature_file),
    ]

    import shutil
    for src, dest in files_to_copy:
        if src.exists():
            shutil.copy(src, dest)
            print(f"Copied {src} to {dest} for audit.")
        else:
            print(f"Warning: Source file {src} not found for audit preparation.")

    # Create a simple main.py that imports and runs the app, for audit script compatibility
    main_py_content = f"""\
# Auto-generated main.py for audit purposes
# It attempts to import and run the main function from the generated app.

def run():
    try:
        # Assuming the generated app is in gandalf_workshop.app
        # and has a main() function or similar entry point.
        from gandalf_workshop import {audit_app_name}
        if hasattr({audit_app_name}, 'main'):
            print(f"Executing {audit_app_name}.main() from main.py...")
            {audit_app_name}.main()
        elif hasattr({audit_app_name}, 'run'):
            print(f"Executing {audit_app_name}.run() from main.py...")
            {audit_app_name}.run()
        else:
            print(f"No main() or run() function found in gandalf_workshop.{audit_app_name}")
    except ImportError:
        print(f"Could not import gandalf_workshop.{audit_app_name} in main.py")
    except Exception as e:
        print(f"Error running app from main.py: {{e}}")

if __name__ == "__main__":
    print("main.py executed for audit.")
    run()
"""
    with open("main.py", "w") as f:
        f.write(main_py_content)
    print("Created/updated main.py for audit.")

    print("Preparation for audit complete. Files copied to gandalf_workshop/ and ./main.py")
    print("Next step is to run: make audit")

if __name__ == "__main__":
    main()
