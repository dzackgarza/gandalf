import typer
from typing_extensions import Annotated
from typing import Optional # Added Optional
import os
from pathlib import Path
import yaml # For saving YAML output, though models.py also handles it.

from .extractor import MarkdownExtractor
from .config import LLMConfig
from .models import LogicalUnitsFile # For type hinting if needed

# Create a Typer app instance
app = typer.Typer(
    name="mdextract",
    help="CLI application to extract structured logical units from mathematics markdown files using LLMs.",
    add_completion=False,
)

@app.command(help="Extracts logical units from a markdown file and outputs them as YAML.")
def extract(
    markdown_file_path: Annotated[Path, typer.Argument(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True,
        help="Path to the input markdown file."
    )],
    output_yaml_path: Annotated[Optional[Path], typer.Option(
        "--output", "-o",
        file_okay=True, dir_okay=False, writable=True, resolve_path=True,
        help="Path to save the output YAML file. If not provided, prints to stdout."
    )] = None,
    llm_provider: Annotated[Optional[str], typer.Option(
        "--llm-provider", help="LLM provider (e.g., 'openai', 'azure'). Overrides LLM_PROVIDER env var."
    )] = None,
    llm_model_name: Annotated[Optional[str], typer.Option(
        "--llm-model", help="Specific LLM model name. Overrides LLM_MODEL_NAME env var."
    )] = None,
    api_key: Annotated[Optional[str], typer.Option(
        "--api-key", help="API key for the LLM provider. Overrides corresponding env var (e.g., OPENAI_API_KEY)."
    )] = None,
    azure_api_version: Annotated[Optional[str], typer.Option(
        "--azure-api-version", help="Azure API version. Overrides AZURE_OPENAI_API_VERSION env var."
    )] = None,
    azure_endpoint: Annotated[Optional[str], typer.Option(
        "--azure-endpoint", help="Azure endpoint. Overrides AZURE_OPENAI_ENDPOINT env var."
    )] = None,
    max_retries: Annotated[Optional[int], typer.Option(
        "--max-retries", min=0, help="Max retries for LLM calls. Overrides default in config."
    )] = None,
):
    """
    Processes a markdown file to extract structured logical units and outputs them in YAML format.
    """
    typer.echo(f"Starting extraction for: {markdown_file_path}")

    # Prepare LLM configuration, overriding defaults with CLI options if provided
    config_overrides = {}
    if llm_provider:
        config_overrides['provider'] = llm_provider
    if llm_model_name:
        config_overrides['model_name'] = llm_model_name
    if api_key:
        # This single api_key will be tried for the configured provider
        # The LLMConfig will pick the right env var if this isn't set
        config_overrides['api_key'] = api_key
    if azure_api_version:
        config_overrides['azure_api_version'] = azure_api_version
    if azure_endpoint:
        config_overrides['azure_endpoint'] = azure_endpoint
    if max_retries is not None: # Check for None because 0 is a valid value
        config_overrides['max_retries'] = max_retries

    try:
        llm_config = LLMConfig(**config_overrides)
    except Exception as e:
        typer.secho(f"Error initializing LLM configuration: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not llm_config.get_api_key_for_provider() and not os.getenv("OPENAI_API_BASE"): # Allow local models without key
        typer.secho(
            f"Warning: API key for provider '{llm_config.provider}' is not set, and OPENAI_API_BASE is not set. LLM calls may fail.",
            fg=typer.colors.YELLOW,
            err=True
        )
        # Allow proceeding if user intends to use a local model via OPENAI_API_BASE or similar mechanism

    try:
        with open(markdown_file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
    except Exception as e:
        typer.secho(f"Error reading markdown file '{markdown_file_path}': {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    extractor = MarkdownExtractor(config=llm_config)

    typer.echo(f"Using LLM: {llm_config.provider} - {llm_config.model_name}")
    if llm_config.provider == "azure":
        typer.echo(f"Azure Endpoint: {llm_config.azure_endpoint}")
        typer.echo(f"Azure API Version: {llm_config.azure_api_version}")


    logical_units_data = extractor.extract_logical_units_from_markdown(
        markdown_content=markdown_content,
        source_filename=markdown_file_path.name,
        max_llm_retries=llm_config.max_retries # LLMConfig already incorporates CLI override if any
    )

    if logical_units_data:
        yaml_output = extractor.units_to_yaml(logical_units_data)
        if output_yaml_path:
            try:
                # Ensure parent directory exists
                output_yaml_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_yaml_path, "w", encoding="utf-8") as f:
                    f.write(yaml_output)
                typer.secho(f"Successfully extracted and saved YAML to: {output_yaml_path}", fg=typer.colors.GREEN)
            except Exception as e:
                typer.secho(f"Error writing YAML to file '{output_yaml_path}': {e}", fg=typer.colors.RED, err=True)
                # Optionally print to stdout as a fallback
                # typer.echo("\nYAML Output:\n")
                # typer.echo(yaml_output)
                raise typer.Exit(code=1)
        else:
            typer.echo("\nYAML Output:\n")
            typer.echo(yaml_output)
    else:
        typer.secho("Extraction failed or produced no data.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command(name="config-check", help="Checks and displays the current LLM configuration resolution.")
def config_check(
    llm_provider: Annotated[Optional[str], typer.Option("--llm-provider")] = None,
    llm_model_name: Annotated[Optional[str], typer.Option("--llm-model")] = None,
    api_key: Annotated[Optional[str], typer.Option("--api-key")] = None,
    azure_api_version: Annotated[Optional[str], typer.Option("--azure-api-version")] = None,
    azure_endpoint: Annotated[Optional[str], typer.Option("--azure-endpoint")] = None,
):
    """
    Displays the LLM configuration that would be used, based on environment variables
    and any provided command-line overrides.
    """
    config_overrides = {}
    if llm_provider: config_overrides['provider'] = llm_provider
    if llm_model_name: config_overrides['model_name'] = llm_model_name
    if api_key: config_overrides['api_key'] = api_key
    if azure_api_version: config_overrides['azure_api_version'] = azure_api_version
    if azure_endpoint: config_overrides['azure_endpoint'] = azure_endpoint

    try:
        config = LLMConfig(**config_overrides)
        typer.secho("Resolved LLM Configuration:", fg=typer.colors.BLUE, bold=True)
        typer.echo(f"  Provider: {config.provider}")
        typer.echo(f"  Model Name: {config.model_name}")

        resolved_api_key = config.get_api_key_for_provider()
        api_key_status = f"'{resolved_api_key[:4]}...{resolved_api_key[-4:]}'" if resolved_api_key else "Not Set"

        if config.provider == "openai" and not resolved_api_key and os.getenv("OPENAI_API_BASE"):
             api_key_status += f" (OPENAI_API_BASE is set: {os.getenv('OPENAI_API_BASE')})"

        typer.echo(f"  API Key: {api_key_status}")

        if config.provider == "azure":
            typer.echo(f"  Azure API Version: {config.azure_api_version or 'Not Set (Required for Azure)'}")
            typer.echo(f"  Azure Endpoint: {config.azure_endpoint or 'Not Set (Required for Azure)'}")

        typer.echo(f"  Max Retries: {config.max_retries}")

        # Attempt to get client to see if essential configs are present
        try:
            client = config.get_configured_client()
            if client:
                 typer.secho("  Client Initialization: Successful", fg=typer.colors.GREEN)
            else:
                 typer.secho("  Client Initialization: Failed (Check provider support or config)", fg=typer.colors.RED)
        except ValueError as ve:
            typer.secho(f"  Client Initialization: Failed ({ve})", fg=typer.colors.RED)


    except Exception as e:
        typer.secho(f"Error determining configuration: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


# This makes the Typer app runnable when the script is executed directly
# e.g., python -m gandalf_workshop.structured_markdown_extractor.cli extract ...
if __name__ == "__main__":
    # For direct execution, you might want to load .env here if not loaded elsewhere
    from dotenv import load_dotenv
    load_dotenv()
    app()
