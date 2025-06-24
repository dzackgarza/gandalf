# First Commission Walkthrough: "The GUI Calculator"

This document walks through the Gandalf Workshop's process for its first hypothetical commission: "Build a GUI calculator application." It demonstrates how the Workshop Manager, Specialist Artisans, Blueprints, Commission Expectations, Products, and the automated Audit Pipeline interact to deliver a high-quality, verified result, aligning with the "Proof-of-Work" Constitution.

**Commission Brief (Client Request):** "We need a simple graphical calculator application for desktop users. It should perform basic arithmetic operations: addition, subtraction, multiplication, and division. It needs a clear display and standard number buttons (0-9) and operator buttons. Users should be able to chain operations (e.g., 1 + 2 + 3) and see intermediate results."

## The Commission Journey

1.  **Commission Acceptance & Planning (Blueprint & Expectations):**
    *   The **Workshop Manager** receives the "Build a GUI calculator app" Commission.
    *   A unique `commission_id` is assigned: `gui_calc_001`.
    *   The Manager assigns the task of creating planning artifacts to a **Planner Artisan** (specializing as a "Software Architect").
    *   The Planner Artisan studies the brief and drafts two key documents:
        1.  `blueprints/gui_calc_001/blueprint.yaml`:
            *   `commission_title: "GUI Calculator Application"`
            *   `commission_type: "software_mvp"`
            *   `project_summary: "A desktop GUI calculator for basic arithmetic with chained operations."`
            *   `product_specifications`:
                *   `type: "software"`
                *   `target_platform: "Desktop (Windows/macOS/Linux)"`
                *   `primary_language_framework: "Python/Tkinter"` (or another suitable GUI framework)
                *   `modules`:
                    *   `module_name: "ui_module"` (handling display, buttons, user interaction)
                    *   `module_name: "logic_module"` (handling calculations, state management)
                *   `components` within `ui_module`: `display_field`, `number_buttons_0_9`, `operator_buttons_plus_minus_etc`, `equals_button`, `clear_button`.
                *   `components` within `logic_module`: `perform_operation`, `append_digit`, `set_operator`, `calculate_result`, `clear_state`, `handle_error_state` (e.g., division by zero).
                *   `unit_tests_required`: `test_addition`, `test_subtraction`, `test_multiplication`, `test_division`, `test_division_by_zero_error`, `test_clear_state`, `test_append_digit_to_current_number`, `test_set_operator_updates_state`, `test_chaining_operations_intermediate_result`.
            *   `quality_criteria`: "All unit tests pass with >=80% coverage," "All BDD scenarios pass," "Code is linted and type-checked successfully."
        2.  `gandalf_workshop/tests/features/gui_calc_001.feature` (Commission Expectations):
            ```gherkin
            Feature: GUI Calculator Basic Operations
              As a user
              I want to perform basic arithmetic operations
              So that I can get correct calculation results.

              Scenario: Adding two numbers
                Given the calculator is clear
                When I press "1"
                And I press "+"
                And I press "2"
                And I press "="
                Then the display should show "3"

              Scenario: Chaining multiple additions
                Given the calculator is clear
                When I press "1"
                And I press "+"
                And I press "2"
                And I press "+"
                And I press "3"
                And I press "="
                Then the display should show "6"

              Scenario: Division by zero
                Given the calculator is clear
                When I press "5"
                And I press "/"
                And I press "0"
                And I press "="
                Then the display should show "Error"
            ```
            *(More scenarios for subtraction, multiplication, clear button, etc., would be included)*

2.  **First Product Iteration (Implementation & Test Creation):**
    *   The **Workshop Manager** reviews `blueprint.yaml` and `gui_calc_001.feature`. Satisfied, the Manager assigns them to a **Coder Artisan** (a "Python/Tkinter Specialist").
    *   The Coder Artisan takes both documents and begins crafting:
        *   The application code in `gandalf_workshop/gui_calculator/` (e.g., `main_app.py`, `ui.py`, `logic.py`).
        *   The unit tests in `gandalf_workshop/tests/unit/` (e.g., `test_logic.py`).
        *   The BDD step definitions in `gandalf_workshop/tests/step_definitions/test_gui_calculator_steps.py`.
            *   Example step definition for `test_gui_calculator_steps.py`:
            ```python
            from pytest_bdd import scenarios, given, when, then, parsers
            # Assume a CalculatorApp class is imported from the product code
            # from gandalf_workshop.gui_calculator.main_app import CalculatorApp # Or similar

            scenarios('../features/gui_calc_001.feature')

            @given("the calculator is clear", target_fixture="calculator")
            def calculator_clear():
                app = CalculatorApp() # Or however the app is instantiated
                app.press_clear_button()
                return app

            @when(parsers.parse('I press "{button_text}"'))
            def press_button(calculator, button_text):
                calculator.press_button(button_text) # Method in app to simulate button press

            @then(parsers.parse('the display should show "{expected_text}"'))
            def display_shows(calculator, expected_text):
                assert calculator.get_display_text() == expected_text
            ```
    *   The Coder aims to make all unit tests and BDD tests pass. Let's say after initial development:
        *   Unit tests: 90% pass (one edge case for chaining missed).
        *   BDD tests: "Adding two numbers" passes, "Chaining multiple additions" fails (due to the same logic error), "Division by zero" passes.

3.  **First Automated Audit:**
    *   The Coder believes the work is ready. The **Workshop Manager** (or an automated trigger, e.g., a commit hook) initiates the `auditing/run_full_audit.sh` script.
    *   The audit pipeline executes:
        *   **Linter/Formatter (black, flake8):** Passes.
        *   **Type Safety (mypy):** Passes.
        *   **Unit Test Coverage (pytest --cov):** Fails. `pytest` reports 1 unit test failure. Coverage is 75% (below 80% threshold).
        *   **BDD Tests (pytest --bdd):** Fails. `pytest --bdd` reports 1 scenario failure ("Chaining multiple additions").
    *   The `LATEST_AUDIT_RECEIPT.md` is generated, showing failures in Unit Test Coverage and BDD Tests.
    *   **Outcome:** The "Proof-of-Work" is NOT met. The commit is rejected (if in a CI/CD context) or the Manager is alerted.

4.  **Revision Cycle 1 (Addressing Audit Failures):**
    *   The **Coder Artisan** reviews the `LATEST_AUDIT_RECEIPT.md` and the detailed logs from `pytest`.
    *   The Coder:
        *   Fixes the logic error affecting chained operations. This makes the failing unit test pass.
        *   Writes an additional unit test for the specific chaining scenario that was initially missed, bringing coverage to 82%.
        *   Reruns BDD tests locally; the "Chaining multiple additions" scenario now passes.
    *   The Coder is now confident all automated checks will pass.

5.  **Second Automated Audit & Approval:**
    *   The **Workshop Manager** (or CI system) re-runs `auditing/run_full_audit.sh`.
    *   The audit pipeline executes:
        *   **Linter/Formatter:** Passes.
        *   **Type Safety:** Passes.
        *   **Unit Test Coverage:** Passes. All unit tests pass. Coverage is 82%.
        *   **BDD Tests:** Passes. All scenarios in `gui_calc_001.feature` pass.
    *   The `LATEST_AUDIT_RECEIPT.md` shows all stages passing.
    *   **Outcome:** "Proof-of-Work" IS met.

6.  **Commission Completion & Archival:**
    *   The **Workshop Manager** reviews the successful `LATEST_AUDIT_RECEIPT.md`.
    *   The Manager declares the Commission complete.
    *   The codebase (application, unit tests, BDD step definitions), along with the `blueprint.yaml`, `gui_calc_001.feature`, and the final `LATEST_AUDIT_RECEIPT.md`, are versioned and archived (e.g., committed to the main branch and tagged).
    *   The "GUI Calculator" Product is now considered verified and ready for "delivery".

This walkthrough illustrates the new iterative nature of the Gandalf Workshop under the "Proof-of-Work" Constitution. The Planner Artisan sets both the technical design (Blueprint) and the behavioral expectations (`.feature` file). The Coder Artisan implements the application and writes both unit tests (for internal component verification) and BDD step definitions (for external behavioral verification). The automated `run_full_audit.sh` script acts as the ultimate gatekeeper, ensuring all forms of "proof" are present and correct before a commission is considered complete.
