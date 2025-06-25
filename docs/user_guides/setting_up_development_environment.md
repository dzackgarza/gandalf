# Setting Up Your Development Environment for Gandalf Workshop

This guide will walk you through the steps to set up your local development environment for the Gandalf Workshop project.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Python**: Version 3.9 or higher. You can download Python from [python.org](https://www.python.org/downloads/).
*   **pip**: Python's package installer. This usually comes with Python. If not, follow the [official installation guide](https://pip.pypa.io/en/stable/installation/).
*   **Git**: For cloning the repository. Download from [git-scm.com](https://git-scm.com/downloads).
*   **`venv` module**: For creating virtual environments. This is part of the Python standard library and should be available if Python is installed correctly.

## Setup Steps

1.  **Clone the Repository:**
    Open your terminal or command prompt and navigate to the directory where you want to store the project. Then, clone the repository using Git:

    ```bash
    git clone https://github.com/your-username/gandalf-workshop.git
    cd gandalf-workshop
    ```
    *(Note: Replace `https://github.com/your-username/gandalf-workshop.git` with the actual repository URL if it's different.)*

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies and avoid conflicts with other Python projects.

    *   Navigate into the cloned project directory (`gandalf-workshop`).
    *   Create a virtual environment (e.g., named `.venv`):

        ```bash
        python -m venv .venv
        ```

    *   Activate the virtual environment:
        *   On **macOS and Linux**:
            ```bash
            source .venv/bin/activate
            ```
        *   On **Windows**:
            ```bash
            .venv\Scripts\activate
            ```
        After activation, your command prompt should be prefixed with `(.venv)`.

3.  **Install Dependencies:**
    With the virtual environment activated, install the required Python packages. The project uses two files for dependencies:
    *   `requirements.txt`: For core application dependencies.
    *   `requirements-dev.txt`: For development and testing tools (like `pytest`, linters, etc.).

    Install them using pip:
    ```bash
    pip install -r requirements.txt -r requirements-dev.txt
    ```

4.  **Verify Setup (Optional but Recommended):**
    You can perform a quick check to ensure everything is set up correctly by running linters and tests. The project should have a `Makefile` with common commands.

    *   **Run Linters:**
        ```bash
        make lint
        ```
        This command will typically run tools like `flake8` and `black` to check code style and formatting. Address any issues reported.

    *   **Run Tests:**
        ```bash
        make test
        ```
        This command will execute the project's test suite using `pytest`. All tests should pass if the environment is set up correctly and the current codebase is stable.

## Next Steps

Once your development environment is ready, you can start exploring the codebase, running the application (see `running_the_application_v1.md`), and contributing to the project.

Remember to activate your virtual environment (`source .venv/bin/activate` or `.venv\Scripts\activate`) every time you start a new terminal session to work on the project. To deactivate, simply type `deactivate`.

If you encounter any issues, please refer to the project's main `README.md` or `CONTRIBUTING.md` for more information, or raise an issue on the project's repository.
