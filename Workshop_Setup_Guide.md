# Workshop Setup Guide

This guide provides instructions for setting up the Gandalf Workshop environment. Following these steps will ensure that all necessary tools are available and the workspace is correctly configured for undertaking new Commissions.

## 1. Tool Inventory (requirements.txt)

The Gandalf Workshop relies on a collection of specialized tools (Python libraries) to function. To ensure all Artisans have what they need, the following tools must be present in the environment:

```text
# Core Orchestration & Agent Frameworks
crewai
openagent
langchain

# For Software Development Commissions
pytest
flake8
pyyaml
bandit

# For Research Report Commissions
# (Assuming APIs are accessed via requests or specific client libraries)
requests
beautifulsoup4
# Add any specific academic API client libraries here, e.g.:
# arxiv
# semanticscholar

# For Data Handling & RAG
PyMuPDF
chromadb
# or
faiss-cpu # or faiss-gpu
# sentence-transformers (often used with RAG for embeddings)

# General Utilities
python-dotenv
gitpython
```

**To install these tools:**

Save the list above into a file named `requirements.txt` in the root directory of the Workshop. Then, run the following command in your terminal:

```bash
pip install -r requirements.txt
```

## 2. Preparing the Workspace (Virtual Environment)

To keep the Workshop's tools and dependencies organized and separate from other projects, it's crucial to set up a dedicated virtual environment. This is like preparing a clean, dedicated workbench for each new type of Commission.

**Steps:**

1.  **Navigate to your project directory (the Workshop's root):**
    ```bash
    cd path/to/gandalf_workshop
    ```

2.  **Create a virtual environment:**
    We'll name our environment `.venv`, a common convention.
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\.venv\Scripts\activate
        ```
    Your terminal prompt should now indicate that you are in the `.venv` environment.

4.  **Install the tools (as per Section 1) within this activated environment.**

## 3. Securing the Keys (.env file)

Many tools and services the Workshop uses (like Large Language Model APIs or specialized data sources) require access keys. These are like the keys to secure cabinets or special machinery in the Workshop. They must be kept confidential.

We will use a `.env` file to store these keys securely. This file will be ignored by version control systems (like Git) to prevent accidental exposure.

**Steps:**

1.  **Create a file named `.env` in the root directory of the Workshop:**
    ```bash
    touch .env
    ```
    Or create it using your text editor.

2.  **Add your API keys and other sensitive configuration to this file in the following format:**
    ```env
    OPENAI_API_KEY="your_openai_api_key_here"
    # Example for a hypothetical academic API
    ACADEMIC_DB_API_KEY="your_academic_db_key_here"
    # Add other keys as needed
    # e.g., GITHUB_TOKEN for accessing private repositories if required
    ```

3.  **Ensure this file is never committed to version control.** If you are using Git, add `.env` to your `.gitignore` file:
    ```text
    # .gitignore
    .venv/
    .env
    __pycache__/
    *.pyc
    ```

With these steps completed, your Gandalf Workshop environment is set up and ready for its first Commission!
