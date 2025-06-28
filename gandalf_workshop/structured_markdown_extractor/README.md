# Structured Content Extractor (Markdown & TeX)

This CLI application extracts structured logical units from mathematics documents (Markdown or TeX files) using a user-configurable LLM provider. It aims to transform dense research paper content into a structured YAML output suitable for further processing, such as thesis generation.

## Features

-   Parses Markdown files directly.
-   Converts TeX files to a processable plain text/Markdown format before extraction.
    -   Prioritizes using **Pandoc** if available in the system PATH for high-quality TeX conversion.
    -   Falls back to the **pylatexenc** Python library for TeX to plain text conversion if Pandoc is not found or fails.
-   Utilizes LLMs (e.g., OpenAI GPT models, Azure OpenAI) for content analysis and structuring based on the (potentially converted) text.
-   Enforces a strict YAML output format defined by Pydantic models.
-   Supports configurable LLM providers and models.
-   Includes retry logic for LLM calls to improve robustness.

## Setup

### Dependencies

Ensure all dependencies are installed from the main `requirements.txt` file in the repository root:
```bash
pip install -r requirements.txt
```
This project specifically uses `typer`, `pydantic`, `openai`, `instructor`, `pyyaml`, `python-dotenv`, and `pylatexenc`.

### System Dependencies (Optional but Recommended for TeX)

*   **Pandoc**: For the best TeX to Markdown conversion quality, installing Pandoc is highly recommended. The tool will automatically use it if found in your system's PATH.
    *   Installation: Visit [https://pandoc.org/installing.html](https://pandoc.org/installing.html). On Debian/Ubuntu, you might use `sudo apt-get install pandoc`.

    If Pandoc is not found, the tool will fall back to using the `pylatexenc` Python library for a more basic TeX to plain text conversion.

### API Keys and Configuration

The application requires API keys for the chosen LLM provider. Configuration is primarily managed through environment variables.

1.  **Create a `.env` file** in the root of the `gandalf_workshop` project (or ensure the required environment variables are set in your system).
    A `.env` file in the *repository root* (where `main.py` or your top-level script might be) will be loaded by `python-dotenv` if you run the CLI from there or if the main application loads it. The CLI itself will also try to load it if executed as a module in some contexts.

2.  **Required Environment Variables (depending on provider)**:

    *   **For OpenAI**:
        ```env
        OPENAI_API_KEY="your_openai_api_key_here"
        # Optional:
        # LLM_PROVIDER="openai" (this is the default)
        # LLM_MODEL_NAME="gpt-4o" (or another model like gpt-3.5-turbo)
        ```

    *   **For Azure OpenAI**:
        ```env
        LLM_PROVIDER="azure"
        AZURE_OPENAI_API_KEY="your_azure_api_key"
        AZURE_OPENAI_ENDPOINT="your_azure_endpoint_here" # e.g., https://your-resource-name.openai.azure.com/
        AZURE_OPENAI_API_VERSION="your_api_version" # e.g., 2023-07-01-preview
        LLM_MODEL_NAME="your_deployment_name_for_the_model"
        ```
    *   **For other providers (e.g., Groq, TogetherAI, local models via OpenAI-compatible API)**:
        You might need to set `OPENAI_API_BASE` if using the OpenAI client with a compatible endpoint.
        ```env
        OPENAI_API_KEY="your_provider_api_key" # Often optional if OPENAI_API_BASE is a local model
        OPENAI_API_BASE="your_provider_openai_compatible_endpoint"
        LLM_PROVIDER="openai" # Or the specific provider name if you extend config.py
        LLM_MODEL_NAME="the_model_name_on_that_provider"
        ```

    Refer to `config.py` for more details on supported providers and environment variables.

## Usage

The CLI is built using Typer. You can run it as a Python module.

### Basic Command Structure

```bash
python -m gandalf_workshop.structured_markdown_extractor.cli [COMMAND] [OPTIONS]
```

### Commands

1.  **`extract`**: Extracts logical units from a markdown file.

    ```bash
    python -m gandalf_workshop.structured_markdown_extractor.cli extract [FILE_PATH] [OPTIONS]
    ```
    **Arguments**:
    *   `FILE_PATH`: Path to the input Markdown (.md) or TeX (.tex) file.

    **Options**:
    *   `--output, -o PATH`: Path to save the output YAML file. If not provided, prints to stdout.
    *   `--llm-provider TEXT`: LLM provider (e.g., 'openai', 'azure'). Overrides `LLM_PROVIDER` env var.
    *   `--llm-model TEXT`: Specific LLM model name. Overrides `LLM_MODEL_NAME` env var.
    *   `--api-key TEXT`: API key for the LLM provider.
    *   `--azure-api-version TEXT`: Azure API version.
    *   `--azure-endpoint TEXT`: Azure endpoint.
    *   `--max-retries INTEGER`: Max retries for LLM calls.

2.  **`config-check`**: Checks and displays the current LLM configuration resolution.
    ```bash
    python -m gandalf_workshop.structured_markdown_extractor.cli config-check [OPTIONS]
    ```
    This command helps verify that your environment variables and CLI overrides are being correctly interpreted.

### Example: Live Test Run

1.  **Ensure your API key is set** in your environment (e.g., in a `.env` file in the project root, or exported). For example, for OpenAI:
    ```
    OPENAI_API_KEY="sk-..."
    LLM_MODEL_NAME="gpt-4o" # Or a cheaper model like "gpt-3.5-turbo" for testing
    ```

2.  **Prepare a sample markdown file.** You can use the one provided in the tests:
    `gandalf_workshop/structured_markdown_extractor/tests/sample_markdown/sample1.md`
    (This file contains the problem description itself, which is a complex document. For a quicker test, you might want a very short mathematical markdown snippet.)

    Let's create a simpler one for a quick live test, e.g., `live_test.md`:
    ```markdown
    # Chapter 1: Basic Definitions

    ## Definition: Group
    A group is a set $G$ equipped with a binary operation $\\cdot: G \\times G \\to G$ satisfying:
    1. Associativity: $(a \\cdot b) \\cdot c = a \\cdot (b \\cdot c)$ for all $a, b, c \\in G$.
    2. Identity element: There exists an element $e \\in G$ such that $e \\cdot a = a \\cdot e = a$ for all $a \\in G$.
    3. Inverse element: For each $a \\in G$, there exists an element $a^{-1} \\in G$ such that $a \\cdot a^{-1} = a^{-1} \\cdot a = e$.

    This is a fundamental concept.
    ```
    Save this as `live_test.md` in the root of the repository or a known path.

3.  **Run the extractor**:
    Assuming `live_test.md` is in your current directory:
    ```bash
    python -m gandalf_workshop.structured_markdown_extractor.cli extract live_test.md -o extracted_live_test.yaml --llm-model "gpt-3.5-turbo"
    ```
    (Using `gpt-3.5-turbo` as an example for a faster/cheaper test. You might need a more powerful model like `gpt-4o` for better adherence to the complex instructions, especially for larger documents or more nuanced mathematical content.)

4.  **Inspect the output**:
    Check `extracted_live_test.yaml`. It should contain the structured YAML output based on the content of `live_test.md`.

    **Expected (conceptual) output for `live_test.md`**:
    You should see at least one logical unit, likely of `unit_type: "definition"`, with fields populated. For example:
    ```yaml
    logical_units:
      - unit_id: "group_definition"
        unit_type: "definition"
        thesis_title: "Definition of a Group"
        dependencies: []
        paper_source:
          file_path: "live_test.md"
          start_line: # Some estimated line number
          end_line: # Some estimated line number
          verbatim_content: |
            A group is a set $G$ equipped with a binary operation $\cdot: G \times G \to G$ satisfying:
            1. Associativity: $(a \cdot b) \cdot c = a \cdot (b \cdot c)$ for all $a, b, c \in G$.
            2. Identity element: There exists an element $e \in G$ such that $e \cdot a = a \cdot e = a$ for all $a \in G$.
            3. Inverse element: For each $a \in G$, there exists an element $a^{-1} \in G$ such that $a \cdot a^{-1} = a^{-1} \cdot a = e$.
        notation_explanations:
          latex_macros: {}
          mathematical_context:
            "G": "A set representing the group."
            "\\cdot": "The binary operation of the group."
            "e": "The identity element of the group."
            "a^{-1}": "The inverse of element a."
        thesis_content:
          condensed_summary: "This unit defines a group, which is a set with an associative binary operation, an identity element, and inverse elements for all its members."
          detailed_analysis: |
            A group is a fundamental algebraic structure consisting of a set of elements and a binary operation that combines any two elements to form a third element. For the structure to be a group, this operation must satisfy four axioms: closure (implied by the operation's codomain), associativity, the existence of an identity element, and the existence of an inverse element for every element in the set. These axioms ensure that groups have a rich mathematical structure that is extensively studied in abstract algebra.
          expansion_notes: "The definition is standard. For a thesis, one might expand on the historical context, provide more non-standard examples, or discuss the importance of each axiom."
        # proof_development would be null or omitted for a definition
        audits:
          - audit_id: "extractor_initial_..." # Dynamic ID
            auditor_role: "extractor"
            audit_date: "..." # Dynamic timestamp
            suspicion_scores:
              source_fidelity: 1.0
              # ... all scores 1.0
            audit_notes: "Initial extraction by LLM..."
      # Potentially another unit for "This is a fundamental concept." if granularity is high
      # or if the LLM decides to make the introductory sentence its own unit.
    ```
    When processing TeX files, the `paper_source.verbatim_content`, `start_line`, and `end_line` fields in the YAML will refer to the intermediate Markdown/text representation that the LLM processes, not the original TeX file. The `paper_source.file_path` will correctly point to your original `.tex` file. The quality of TeX conversion (Pandoc vs. `pylatexenc` fallback) can impact the LLM's ability to extract information accurately.

## Development & Testing

-   Unit tests are located in the `tests/` subdirectory.
-   Run tests using `pytest`:
    ```bash
    python -m pytest gandalf_workshop/structured_markdown_extractor/tests/
    ```
    (Ensure you are using the correct Python environment where dependencies are installed, e.g., a pyenv environment.)
```
