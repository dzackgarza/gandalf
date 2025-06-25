from pytest_bdd import scenarios, given, when, then, parsers
import subprocess
from pathlib import Path

SCENARIO_FILE = "../commission_expectations.feature"
scenarios(SCENARIO_FILE)

APP_SCRIPT = "app.py"


@given("the greeter CLI application is available")
def cli_available():
    # Assumes APP_SCRIPT is relative to the features directory's parent (coding_outputs)
    # when tests are run by pytest from project root and files are copied to gandalf_workshop/
    # For audit, run_commission.py copies app.py to gandalf_workshop/app.py
    # and features/steps to gandalf_workshop/tests/step_definitions
    # and features files to gandalf_workshop/tests/features
    # So, from gandalf_workshop/tests/step_definitions/app_steps.py,
    # app.py is at ../../app.py (relative to gandalf_workshop itself)
    # This path needs to be relative to the location of app_steps.py during audit
    # which is gandalf_workshop/tests/step_definitions/app_steps.py
    # The app itself is at gandalf_workshop/app.py
    # So from app_steps.py, app_file is Path(__file__).parent.parent.parent / APP_SCRIPT
    app_file = Path(__file__).parent.parent.parent / APP_SCRIPT
    assert app_file.exists(), (
        "Application script " + str(app_file) + " not found for BDD step."
    )


@when(parsers.parse('I run the application with the name "{name}"'))  # Escaped {name}
def run_with_name(name, tmp_path):
    app_file = Path(__file__).parent.parent.parent / APP_SCRIPT
    command = ["python", str(app_file), "--name", name]
    process = subprocess.run(command, capture_output=True, text=True, check=False)
    tmp_path.process_result = process


@when("I run the application without providing a name")
def run_without_name(tmp_path):
    app_file = Path(__file__).parent.parent.parent / APP_SCRIPT
    command = ["python", str(app_file)]
    process = subprocess.run(command, capture_output=True, text=True, check=False)
    tmp_path.process_result = process


@then(
    parsers.parse('the output should be "{expected_output}"')
)  # Escaped {expected_output}
def verify_output(expected_output, tmp_path):
    raw_stderr = tmp_path.process_result.stderr
    assert (
        tmp_path.process_result.returncode == 0
    ), f"CLI app exited with code {tmp_path.process_result.returncode}, stderr: {raw_stderr}"
    assert tmp_path.process_result.stdout.strip() == expected_output
