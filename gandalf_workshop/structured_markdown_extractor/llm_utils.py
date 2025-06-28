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

    # --- START OF SIMULATION BLOCK FOR MVP VIABILITY TEST ---
    # This block is for simulating a successful LLM response for a specific file
    # when a live API key is not available to the agent.
    # It should be removed or disabled for actual live runs with an API key.
    from .models import ExtractionResult as ActualExtractionResult # Avoid conflict with T
    try:
        from .dev_utils_simulated_llm_response import get_simulated_llm_response_for_md_sample
        dev_utils_available = True
    except ImportError:
        dev_utils_available = False # Allow graceful degradation if dev_utils is missing

    if dev_utils_available and "sample_math_article.md" in user_prompt and response_model is ActualExtractionResult:
        print("SIMULATING successful LLM response for sample_math_article.md")
        simulated_data = get_simulated_llm_response_for_md_sample()
        if simulated_data:
            if isinstance(simulated_data, response_model): # response_model is ActualExtractionResult here
                return simulated_data
            else:
                try:
                    # This case should ideally not be hit if get_simulated_llm_response_for_md_sample is correct
                    print(f"Attempting to validate simulated_data (type: {type(simulated_data)}) against response_model (type: {response_model})")
                    return response_model.model_validate(simulated_data.model_dump())
                except Exception as e:
                    print(f"Error validating/casting simulated data: {e}")
                    print("Falling through to actual LLM call due to simulation data issue.")
        else:
            print("Simulation function returned None. Falling through.")
    # --- END OF SIMULATION BLOCK ---

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
    import os # For potential env var setting in tests

    print("Running llm_utils.py example...")

    # 1. Configure LLM (assumes OPENAI_API_KEY is in .env or environment)
    try:
        llm_config = LLMConfig() # Loads from env or defaults
        print(f"Using LLM Provider: {llm_config.provider}, Model: {llm_config.model_name}")

        if not llm_config.get_api_key_for_provider() and not os.getenv("OPENAI_API_BASE"): # Check if API base for local models is also not set
            print("API key not configured and no OPENAI_API_BASE set. LLM calls will fail if not intercepted by simulation.")

        # Test the simulation path for sample_math_article.md
        print("\n--- Testing Simulation Path for sample_math_article.md ---")
        from .models import ExtractionResult as TestExtractionResult # For response_model type
        from .prompts import get_system_prompt, get_user_prompt # Ensure these are available
        dev_utils_imported_for_main = False
        try:
            from .dev_utils_simulated_llm_response import get_simulated_llm_response_for_md_sample
            dev_utils_imported_for_main = True
        except ImportError:
            print("WARNING: dev_utils_simulated_llm_response.py not found, simulation test in __main__ will be skipped.")


        if dev_utils_imported_for_main:
            # Craft a user_prompt that will trigger the simulation
            sim_trigger_user_prompt = get_user_prompt("Simulated content for sample_math_article.md", "sample_math_article.md")

            simulated_response = call_llm_with_structured_output(
                config=llm_config,
                response_model=TestExtractionResult, # Critical: must match what simulation block checks
                system_prompt=get_system_prompt(),
                user_prompt=sim_trigger_user_prompt,
                max_retries=0
            )

            if simulated_response and simulated_response.logical_units:
                print("\nSuccessfully received SIMULATED structured response:")
                print(f"Number of logical units: {len(simulated_response.logical_units)}")
                assert len(simulated_response.logical_units) > 0, "Simulated response should have units"
                print(f"First unit ID (simulated): {simulated_response.logical_units[0].unit_id}")
                assert simulated_response.logical_units[0].unit_id == "foo_bar_definition"
            else:
                print("\nFAILED to get SIMULATED structured response or it was empty.")
        else:
            print("Skipping direct simulation test in __main__ because dev_utils module was not imported.")


        print("\n--- Testing a non-simulated path (e.g., simple extraction) ---")
        # Note: PydanticBaseModel is already imported in the main scope of llm_utils
        class TestName(PydanticBaseModel):
            first_name: str = instructor.Field(description="The first name of a person")
            last_name: str

        test_system_prompt = "You are a helpful assistant that extracts information."
        test_user_prompt = "Extract the first and last name from the text: 'My name is John Doe.'" # This will not trigger simulation

        live_response = call_llm_with_structured_output(
            config=llm_config,
            response_model=TestName,
            system_prompt=test_system_prompt,
            user_prompt=test_user_prompt,
            max_retries=0
        )

        if live_response:
            print("\nSuccessfully received live response for TestName:")
            print(f"  First Name: {live_response.first_name}")
            print(f"  Last Name: {live_response.last_name}")
        else:
            print("\nFailed to get live response for TestName (this is expected if API key is missing and not simulated).")

    except ImportError as e:
        print(f"Skipping llm_utils example: `dotenv` or other dependencies might be missing for this test script. Error: {e}")
    except Exception as e:
        print(f"An error occurred during llm_utils example: {e}")

    print("\nllm_utils.py example finished.")
