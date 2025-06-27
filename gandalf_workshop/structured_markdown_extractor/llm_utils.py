import instructor
from openai import OpenAI
from pydantic import ValidationError, BaseModel as PydanticBaseModel
from typing import Type, TypeVar, List, Optional

from .models import LogicalUnit, LogicalUnitsFile # Assuming models.py is in the same directory
from .config import LLMConfig
from .prompts import get_system_prompt, get_user_prompt # Assuming prompts.py will be created

# Define a generic type for Pydantic models
T = TypeVar("T", bound=PydanticBaseModel) # Changed from instructor.BaseModel

def call_llm_with_structured_output(
    config: LLMConfig,
    response_model: Type[T],
    system_prompt: str,
    user_prompt: str,
    max_retries: Optional[int] = None
) -> Optional[T]:
    """
    Calls the configured LLM provider to get structured output.

    Args:
        config: The LLMConfig instance.
        response_model: The Pydantic model to parse the response into.
        system_prompt: The system prompt for the LLM.
        user_prompt: The user prompt for the LLM.
        max_retries: Override for the number of retries for this specific call.
                     If None, uses config.max_retries.

    Returns:
        An instance of the response_model if successful, None otherwise.
    """
    try:
        client = config.get_configured_client()
        if client is None:
            print("Error: LLM client could not be initialized.")
            return None
    except ValueError as e:
        print(f"Error initializing LLM client: {e}")
        return None

    effective_max_retries = max_retries if max_retries is not None else config.max_retries

    current_user_prompt = user_prompt
    error_context = ""

    for attempt in range(effective_max_retries + 1): # +1 because first attempt is not a "retry"
        print(f"LLM Call Attempt: {attempt + 1}/{effective_max_retries + 1}")
        if error_context:
            # Prepend error context to the user prompt for subsequent retries
            prompt_with_error_context = f"{error_context}\n\nOriginal User Prompt:\n{user_prompt}"
            # Alternatively, make it part of the conversation history if using chat models more directly
        else:
            prompt_with_error_context = current_user_prompt

        try:
            # Using chat completions as it's standard for structured output with instructor
            # The `instructor.patch(client)` modifies the client to handle `response_model`
            response = client.chat.completions.create(
                model=config.model_name,
                response_model=response_model, # This is the key for instructor
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_with_error_context},
                ],
                # max_tokens=4096, # Adjust as needed, some models have limits
                temperature=0.1, # Lower temperature for more deterministic output
            )
            # If successful, instructor has already validated and parsed into the response_model
            print("LLM call successful, output validated by Pydantic/Instructor.")
            return response
        except ValidationError as e:
            print(f"Pydantic Validation Error on attempt {attempt + 1}: {e}")
            error_context = (
                f"There was a validation error in the previous attempt: {e}. "
                "Please review your output and ensure it strictly adheres to the required format and all constraints. "
                "Pay close attention to required fields, data types, and any specific formatting rules mentioned in the schema."
            )
            if attempt >= effective_max_retries:
                print("Max retries reached after validation error.")
                return None
        except Exception as e:
            # This could be API errors, connection issues, etc.
            print(f"Error during LLM call on attempt {attempt + 1}: {e}")
            error_context = (
                f"An unexpected error occurred in the previous attempt: {e}. "
                "Please try generating the response again, ensuring all requirements are met."
            )
            if attempt >= effective_max_retries:
                print("Max retries reached after API/other error.")
                return None

        print("Retrying LLM call...")

    return None


async def acall_llm_with_structured_output(
    config: LLMConfig,
    response_model: Type[T],
    system_prompt: str,
    user_prompt: str,
    max_retries: Optional[int] = None
) -> Optional[T]:
    """
    Asynchronously calls the configured LLM provider to get structured output.
    (Implementation would be similar to the synchronous version but using async client methods)
    For now, this is a placeholder. `instructor` supports async clients.
    """
    # Placeholder: Actual implementation would use an async client from config
    # and `await client.chat.completions.create(...)`
    print("Async LLM call not fully implemented in this example, using synchronous for now.")
    return call_llm_with_structured_output(config, response_model, system_prompt, user_prompt, max_retries)


if __name__ == "__main__":
    # This is a basic test. For a real test, you'd need API keys and potentially mock the LLM.
    # Ensure your .env file is loaded or environment variables are set (e.g., OPENAI_API_KEY)
    from dotenv import load_dotenv
    load_dotenv()

    print("Running llm_utils.py example...")

    # 1. Configure LLM (assumes OPENAI_API_KEY is in .env or environment)
    # You might need to set LLM_PROVIDER and LLM_MODEL_NAME if they are not the defaults you want
    # os.environ["LLM_PROVIDER"] = "openai"
    # os.environ["LLM_MODEL_NAME"] = "gpt-3.5-turbo" # Cheaper model for testing

    try:
        llm_config = LLMConfig() # Loads from env or defaults
        print(f"Using LLM Provider: {llm_config.provider}, Model: {llm_config.model_name}")

        if not llm_config.get_api_key_for_provider():
            print("API key not configured. Skipping live LLM call test.")
        else:
            # 2. Define a simple Pydantic model for the expected response (for testing)
            class TestName(instructor.BaseModel):
                first_name: str = instructor.Field(description="The first name of a person")
                last_name: str

            # 3. Define prompts
            test_system_prompt = "You are a helpful assistant that extracts information."
            test_user_prompt = "Extract the first and last name from the text: 'My name is John Doe.'"

            # 4. Call the LLM
            print("\nAttempting LLM call with structured output (TestName model)...")
            structured_response = call_llm_with_structured_output(
                config=llm_config,
                response_model=TestName,
                system_prompt=test_system_prompt,
                user_prompt=test_user_prompt,
                max_retries=1 # For testing, limit retries
            )

            if structured_response:
                print("\nSuccessfully received structured response:")
                print(f"  First Name: {structured_response.first_name}")
                print(f"  Last Name: {structured_response.last_name}")
                assert structured_response.first_name == "John"
                assert structured_response.last_name == "Doe"
            else:
                print("\nFailed to get structured response after retries.")

            # Test with the actual LogicalUnitsFile model (more complex)
            # This requires a much more sophisticated prompt and a powerful model.
            # For a simple test, we'll use a mock prompt that asks for a very simple version.
            print("\nAttempting LLM call with structured output (LogicalUnitsFile model - simplified)...")

            # Create a dummy markdown content for the test user prompt
            sample_md_for_llm_test = """
            # Section 1: Introduction
            This is an intro. It defines a widget.
            A widget is a device.
            ## Subsection 1.1: Widget Properties
            Widgets are blue.
            """

            simplified_user_prompt_for_lus = get_user_prompt(sample_md_for_llm_test, "sample_doc.md") # Use actual prompt getter
            simplified_system_prompt_for_lus = get_system_prompt() # Use actual prompt getter

            # To make this test runnable without a perfect LLM response for the full complex model,
            # one might mock the LLM or use a very capable model with a very detailed prompt.
            # For now, we'll just see if it attempts the call.
            # A real test for this would involve a small, well-defined markdown and expected YAML.

            # Temporarily use a simpler model for the complex task if needed, or expect it to fail/take time
            # llm_config_for_complex = LLMConfig(model_name="gpt-4o") # Ensure a capable model

            # print(f"System Prompt for LogicalUnitsFile:\n{simplified_system_prompt_for_lus[:300]}...")
            # print(f"User Prompt for LogicalUnitsFile:\n{simplified_user_prompt_for_lus[:300]}...")

            # logical_units_response = call_llm_with_structured_output(
            #     config=llm_config, # or llm_config_for_complex
            #     response_model=LogicalUnitsFile,
            #     system_prompt=simplified_system_prompt_for_lus,
            #     user_prompt=simplified_user_prompt_for_lus,
            #     max_retries=0 # No retries for this quick test to avoid long waits/costs
            # )

            # if logical_units_response:
            #     print("\nSuccessfully received structured response for LogicalUnitsFile:")
            #     print(f"Number of logical units: {len(logical_units_response.root)}")
            #     if logical_units_response.root:
            #         print(f"First unit ID: {logical_units_response.root[0].unit_id}")
            # else:
            #     print("\nFailed to get structured response for LogicalUnitsFile (this might be expected with a simple prompt/model).")
            print("\nSkipping complex LogicalUnitsFile LLM call in this basic test to save time/cost.")
            print("A dedicated integration test with a suitable model and prompts would be needed.")


    except ImportError:
        print("Skipping llm_utils example: `dotenv` or other dependencies might be missing for this test script.")
    except Exception as e:
        print(f"An error occurred during llm_utils example: {e}")

    print("\nllm_utils.py example finished.")
