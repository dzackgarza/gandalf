from typing import Optional, List
from .config import LLMConfig
from .models import LogicalUnitsFile, LogicalUnit, ExtractionResult
from .prompts import get_system_prompt, get_user_prompt
from .llm_utils import call_llm_with_structured_output
from .converters import convert_tex_to_markdown # Added converter import
import yaml

class MarkdownExtractor:
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initializes the MarkdownExtractor with an LLM configuration.

        Args:
            config: An LLMConfig instance. If None, a default config is created.
        """
        self.config = config if config is not None else LLMConfig()

    def extract_logical_units_from_file_content(
        self,
        file_content: str,
        source_filename: str, # This is the original filename, e.g., "document.tex" or "document.md"
        max_llm_retries: Optional[int] = None
    ) -> Optional[LogicalUnitsFile]:
        """
        Extracts logical units from file content (Markdown or TeX) using an LLM.
        If TeX content is provided, it's first converted to Markdown/plain text.

        Args:
            file_content: The raw text content of the file.
            source_filename: The original filename of the document.
            max_llm_retries: Specific number of retries for this extraction call,
                             overriding the config's default if provided.

        Returns:
            A LogicalUnitsFile object containing the extracted units, or None on failure.
        """
        if not file_content.strip():
            print("Warning: File content is empty or whitespace only. Skipping extraction.")
            return LogicalUnitsFile(root=[])

        processed_content = file_content
        is_tex = source_filename.lower().endswith(".tex")

        if is_tex:
            print(f"Detected TeX file: '{source_filename}'. Attempting conversion to Markdown/plain text...")
            converted_text = convert_tex_to_markdown(file_content)
            if converted_text is None:
                print(f"Failed to convert TeX file '{source_filename}' to Markdown. Skipping extraction.")
                return None
            processed_content = converted_text
            print(f"TeX file '{source_filename}' converted. Proceeding with extraction.")
        else:
            print(f"Processing Markdown file: '{source_filename}'.")


        system_prompt = get_system_prompt()
        # User prompt should receive the processed content (Markdown) but refer to the original source filename
        user_prompt = get_user_prompt(processed_content, source_filename)

        print(f"Starting LLM extraction for '{source_filename}' (using model '{self.config.model_name}')...")

        # The response_model tells instructor what Pydantic model to parse the LLM output into.
        # We now use ExtractionResult which has a `logical_units` field.
        extraction_result = call_llm_with_structured_output(
            config=self.config,
            response_model=ExtractionResult, # Use the new wrapper model
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_retries=max_llm_retries # Pass through retry override
        )

        if extraction_result and extraction_result.logical_units is not None:
            # Construct the LogicalUnitsFile (RootModel) from the list
            logical_units_file = LogicalUnitsFile(root=extraction_result.logical_units)
            print(f"Successfully extracted {len(logical_units_file.root)} logical unit(s) from '{source_filename}'.")
            return logical_units_file
        elif extraction_result and extraction_result.logical_units is None:
             print(f"Extraction for '{source_filename}' resulted in an empty list of logical units (or 'null' for logical_units field).")
             return LogicalUnitsFile(root=[]) # Return empty container
        else:
            print(f"Failed to extract logical units from '{source_filename}' after retries.")
            return None

    def units_to_yaml(self, logical_units_file: LogicalUnitsFile) -> str:
        """
        Serializes the LogicalUnitsFile object to a YAML string.
        """
        return logical_units_file.model_dump_yaml()

if __name__ == '__main__':
    from dotenv import load_dotenv
    import os

    load_dotenv() # Load .env file for API keys

    print("Running MarkdownExtractor example...")

    # 1. Setup LLM Configuration (ensure API keys are available in .env or environment)
    # Example: use OPENAI_API_KEY and default gpt-4o or specify others via env vars
    # os.environ["LLM_PROVIDER"] = "openai"
    # os.environ["LLM_MODEL_NAME"] = "gpt-3.5-turbo" # Use a cheaper model for quick tests if desired

    llm_config = LLMConfig()
    if not llm_config.get_api_key_for_provider():
        print("API Key not found for the configured provider. Skipping live LLM extraction test.")
        print("Please set the appropriate environment variables (e.g., OPENAI_API_KEY).")
    else:
        print(f"Using LLM provider: {llm_config.provider}, model: {llm_config.model_name}")

        extractor = MarkdownExtractor(config=llm_config)

        # 2. Sample Markdown Content (from prompts.py example)
        sample_markdown = """
# Chapter 1: Introduction to Frobnitz Theory

This chapter introduces the fundamental concepts of Frobnitz theory.

## 1.1 Definition of a Frobnitz

A **Frobnitz** is defined as a widget that exhibits schmangaroo properties.
Let $F$ be a Frobnitz. We denote its schmangaroo by $\\mathcal{S}(F)$.
This concept was first introduced in [Author2021].

## 1.2 Theorem: Frobnitz Existence

**Theorem 1.2.1.** Under conditions $C_1$ and $C_2$, a Frobnitz exists.

*Proof Sketch.*
The proof relies on constructing a Schmangaroo manifold and showing it's non-empty.
Details can be found in [Author2021, Theorem 3.4].
QED.

## 1.3 Example: The Trivial Frobnitz

Consider a widget where $\\mathcal{S}(F) = 0$. This is the trivial Frobnitz.
It is not very interesting.
"""
        filename = "sample_frobnitz_chapter.md"

        # 3. Perform Extraction
        print(f"\nAttempting to extract logical units from '{filename}'...")
        # Using max_llm_retries=0 for this example to make it faster and less costly if it fails.
        # For real use, you'd likely use the default from config or 1-2 retries.
        logical_units_data = extractor.extract_logical_units_from_markdown(
            markdown_content=sample_markdown,
            source_filename=filename,
            max_llm_retries=0
        )

        # 4. Process Results
        if logical_units_data and logical_units_data.root:
            print(f"\nSuccessfully extracted {len(logical_units_data.root)} logical units.")

            # Print the first unit as an example (if any extracted)
            # print("\nFirst extracted unit (raw Pydantic model):")
            # print(logical_units_data.root[0].model_dump_json(indent=2))

            # Convert to YAML
            yaml_output = extractor.units_to_yaml(logical_units_data)
            print("\nGenerated YAML output:")
            print(yaml_output)

            # You could save this YAML to a file:
            # with open(f"extracted_{filename}.yaml", "w") as f:
            #     f.write(yaml_output)
            # print(f"\nSaved YAML to extracted_{filename}.yaml")

        elif logical_units_data and not logical_units_data.root:
            print("\nExtraction returned an empty list of logical units (no content extracted).")
        else:
            print("\nExtraction failed or returned no data.")
            print("This could be due to API issues, prompt complexity, or the model's inability to satisfy the request with the given content/prompts.")

    print("\nMarkdownExtractor example finished.")
