# Running the Gandalf Workshop V1 Application

This guide explains how to run the Version 1 (V1) of the Gandalf Workshop application. V1 focuses on a basic sequential workflow involving a Planner, Coder, and Auditor agent.

## Prerequisites

*   You must have completed the [Setting Up Development Environment](./setting_up_development_environment.md) guide.
*   Ensure your virtual environment is activated. If not, navigate to the project root and run:
    *   macOS/Linux: `source .venv/bin/activate`
    *   Windows: `.venv\Scripts\activate`

## Running the V1 Application via CLI

The primary way to interact with the Gandalf Workshop (including V1) is through its command-line interface (CLI), typically via `main.py` in the project root.

1.  **Navigate to the Project Root:**
    Open your terminal and ensure you are in the `gandalf-workshop` directory.

2.  **Execute `main.py` with a Prompt:**
    The V1 application is triggered by providing a user prompt. The basic command structure is:

    ```bash
    python main.py --prompt "Your detailed request for the workshop"
    ```

    **Example:**
    To ask the workshop to create a simple "Hello, World!" script, you might run:

    ```bash
    python main.py --prompt "Create a Python file that prints 'Hello, World!'"
    ```

    You can also specify a custom `commission_id`:
    ```bash
    python main.py --prompt "Create a Python file that prints 'Hello, World!'" --commission_id "my_first_commission"
    ```
    If no `commission_id` is provided, a default one will be used or generated.

## Expected V1 Workflow and Output

When you run the command, the `WorkshopManager` will orchestrate the V1 workflow:

1.  **Commission Reception:** You should see output indicating that your commission request has been received and an ID assigned.
    ```
    Received new commission request with prompt: "Create a Python file that prints 'Hello, World!'"
    Assigning Commission ID: commission_xxxxxxxx_xxxxxx
    ```

2.  **Agent Invocation Sequence (V1 Mocked/Basic Agents):**
    The `WorkshopManager` will log its interactions as it calls the V1 agents in sequence:
    *   **Planner Agent:** Takes your prompt and (in V1) produces a basic plan.
        ```
        ===== Starting V1 Workflow for Commission: commission_xxxxxxxx_xxxxxx =====
        User Prompt: Create a Python file that prints 'Hello, World!'
        Workshop Manager: Invoking Planner Agent for 'commission_xxxxxxxx_xxxxxx'.
        Workshop Manager: Planner Agent returned plan: ['Create a Python file that prints \'Hello, World!\'']
        ```
    *   **Coder Agent:** Takes the plan and (in V1) generates a placeholder/mock code file.
        ```
        Workshop Manager: Invoking Coder Agent for 'commission_xxxxxxxx_xxxxxx'.
        Workshop Manager: Coder Agent generated code at: gandalf_workshop/commission_work/commission_xxxxxxxx_xxxxxx/hello.py
        ```
    *   **Auditor Agent:** Takes the code and (in V1) performs a basic audit, likely always succeeding for mock outputs.
        ```
        Workshop Manager: Invoking Auditor Agent for 'commission_xxxxxxxx_xxxxxx'.
        Workshop Manager: Auditor Agent reported: SUCCESS - Audit passed for 'Hello, World!'.
        ```

3.  **Output Location:**
    *   Successfully generated files will be placed in a subdirectory within `gandalf_workshop/commission_work/` named after the `commission_id`. For the example above, it would be something like `gandalf_workshop/commission_work/commission_xxxxxxxx_xxxxxx/hello.py`.
    *   The CLI output will confirm the path to the generated file.

4.  **Completion Message:**
    A message indicating the successful completion of the V1 workflow.
    ```
    ===== V1 Workflow for Commission: commission_xxxxxxxx_xxxxxx Completed Successfully =====
    Commission 'commission_xxxxxxxx_xxxxxx' processed successfully. Output at: gandalf_workshop/commission_work/commission_xxxxxxxx_xxxxxx/hello.py
    ```

## Example V1 Scenario: "Hello, World!"

*   **Input Command:**
    ```bash
    python main.py --prompt "Create a Python file that prints 'Hello, World!'" --commission_id "test_hello_v1"
    ```

*   **Expected Output (Conceptual - details may vary slightly):**
    ```
    Received new commission request with prompt: "Create a Python file that prints 'Hello, World!'"
    Assigning Commission ID: test_hello_v1
    INFO:gandalf_workshop.main:Starting commission 'test_hello_v1'
    INFO:gandalf_workshop.main:Workshop Manager (V1) initialized.

    ===== Starting V1 Workflow for Commission: test_hello_v1 =====
    User Prompt: Create a Python file that prints 'Hello, World!'
    Workshop Manager: Invoking Planner Agent for 'test_hello_v1'.
    Workshop Manager: Planner Agent returned plan: ['Create a Python file that prints \'Hello, World!\'']
    Workshop Manager: Invoking Coder Agent for 'test_hello_v1'.
    Workshop Manager: Coder Agent generated code at: gandalf_workshop/commission_work/test_hello_v1/hello.py
    Workshop Manager: Invoking Auditor Agent for 'test_hello_v1'.
    Workshop Manager: Auditor Agent reported: SUCCESS - Audit passed for 'Hello, World!'.
    ===== V1 Workflow for Commission: test_hello_v1 Completed Successfully =====
    INFO:gandalf_workshop.main:Commission 'test_hello_v1' processed successfully. Output at: gandalf_workshop/commission_work/test_hello_v1/hello.py
    ```

*   **Generated File (`gandalf_workshop/commission_work/test_hello_v1/hello.py`):**
    ```python
    print('Hello, World!')
    ```

## Troubleshooting (V1 Specific)

*   **`FileNotFoundError: main.py`**: Ensure you are running the command from the root directory of the `gandalf-workshop` project.
*   **Module Not Found Errors**: Make sure your virtual environment is activated and you have installed all dependencies from `requirements.txt` and `requirements-dev.txt`.
*   **V1 Agent Behavior**: Keep in mind that the V1 agents (Planner, Coder, Auditor) are very basic and likely use mock logic. The output will be simple and may not reflect complex reasoning or actual code generation beyond predefined scenarios like "Hello, World!". The primary purpose of running V1 is to test the orchestration loop of the `WorkshopManager`.
*   **Audit Failures**: If the `WorkshopManager` is configured to raise an exception on audit failure (as it does by default), an audit failure will terminate the process and show an error message. For V1, this is less likely unless a specific test scenario for audit failure is triggered by the prompt/plan.

For more advanced troubleshooting or issues with agent behavior beyond V1, consult the main project documentation or seek help from the development team.
