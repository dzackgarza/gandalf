import os
from dotenv import load_dotenv
import google.generativeai as genai
from together import Together
from mistralai import Mistral
from typing import Optional, Dict, Any, List

class LLMProviderManager:
    """
    Manages selection and configuration of Large Language Model providers.
    It loads API keys from a .env file and can find a working LLM provider
    from a predefined list (Gemini, Together AI, Mistral).
    """
    def __init__(self):
        """
        Initializes the LLMProviderManager by loading environment variables.
        """
        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.together_api_key = os.getenv("TOGETHER_AI_API_KEY")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        # Store available models discovered for each provider
        self.provider_models = {
            "gemini": [],
            "together_ai": [],
            "mistral": []
        }

    def _check_gemini(self) -> Optional[Dict[str, Any]]:
        """
        Checks if Gemini is operational and lists its available models.
        Returns a dictionary with client and models if successful, None otherwise.
        """
        if not self.gemini_api_key:
            print("DEBUG: Gemini API key not found.")
            return None
        try:
            genai.configure(api_key=self.gemini_api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if models:
                self.provider_models["gemini"] = models
                print(f"DEBUG: Gemini operational. Found models: {models}")
                return {"provider_name": "gemini", "api_key": self.gemini_api_key, "models": models, "client": genai}
            else:
                print("DEBUG: Gemini operational, but no usable models found.")
                return None
        except Exception as e:
            print(f"DEBUG: Error checking Gemini: {e}")
            return None

    def _check_together_ai(self) -> Optional[Dict[str, Any]]:
        """
        Checks if Together AI is operational and lists its available models.
        Returns a dictionary with client and models if successful, None otherwise.
        """
        if not self.together_api_key:
            print("DEBUG: Together AI API key not found.")
            return None
        try:
            client = Together(api_key=self.together_api_key)
            model_list = client.models.list()
            models = []
            if not model_list:
                print("DEBUG: Together AI client.models.list() returned an empty list or None.")
            else:
                print(f"DEBUG: Together AI raw model_list (first 3): {model_list[:3]}")
                for model_info in model_list:
                    model_id_to_add = None
                    if hasattr(model_info, 'id') and model_info.id:
                        model_id_to_add = model_info.id
                    elif hasattr(model_info, 'name') and model_info.name:
                        model_id_to_add = model_info.name

                    if model_id_to_add:
                        # Basic check: assume it's usable if it's a string and not an embedding model by name
                        # This is a guess; real capabilities would need deeper inspection or API documentation.
                        if isinstance(model_id_to_add, str) and 'embed' not in model_id_to_add.lower():
                            models.append(model_id_to_add)
                        else:
                            print(f"DEBUG: Together AI skipping model (not string or embedding-like): {model_id_to_add}")
                    else:
                        print(f"DEBUG: Together AI model_info lacks id or name: {model_info}")

            if models:
                self.provider_models["together_ai"] = models
                print(f"DEBUG: Together AI operational. Found usable models: {models}")
                return {"provider_name": "together_ai", "api_key": self.together_api_key, "models": models, "client": client}
            else:
                print("DEBUG: Together AI operational, but no usable (non-embedding) models found after filtering.")
                return None
        except Exception as e:
            print(f"DEBUG: Error checking Together AI: {e}")
            return None

    def _check_mistral(self) -> Optional[Dict[str, Any]]:
        """
        Checks if Mistral is operational and lists its available models.
        Returns a dictionary with client and models if successful, None otherwise.
        """
        if not self.mistral_api_key:
            print("DEBUG: Mistral API key not found.")
            return None
        try:
            client = Mistral(api_key=self.mistral_api_key)
            model_list = client.models.list()
            models = [model_info.id for model_info in model_list.data] # Assuming all listed are usable for now
            if models:
                self.provider_models["mistral"] = models
                print(f"DEBUG: Mistral operational. Found models: {models}")
                return {"provider_name": "mistral", "api_key": self.mistral_api_key, "models": models, "client": client}
            else:
                print("DEBUG: Mistral operational, but no usable models found.")
                return None
        except Exception as e:
            print(f"DEBUG: Error checking Mistral: {e}")
            return None

    def get_llm_provider(
        self,
        preferred_provider: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None # Placeholder for future use
    ) -> Optional[Dict[str, Any]]:
        """
        Finds and returns a working LLM provider.

        Args:
            preferred_provider: The name of the preferred LLM provider (e.g., "gemini", "together_ai", "mistral").
            required_capabilities: A list of capabilities the model must support (e.g., ['chat', 'function_calling']).
                                   Currently a placeholder.

        Returns:
            A dictionary containing the provider's name, API key, a list of available models,
            and a pre-initialized client instance if a working provider is found.
            Returns None otherwise.
        """
        print(f"DEBUG: Searching for LLM provider. Preferred: {preferred_provider}")
        # Define the order of checking providers
        provider_checks = {
            "gemini": self._check_gemini,
            "together_ai": self._check_together_ai,
            "mistral": self._check_mistral,
        }

        if preferred_provider and preferred_provider in provider_checks:
            print(f"DEBUG: Checking preferred provider: {preferred_provider}")
            provider_info = provider_checks[preferred_provider]()
            if provider_info and provider_info["models"]: # Ensure models are available
                print(f"DEBUG: Preferred provider {preferred_provider} is operational.")
                # Basic capability check (can be expanded)
                # For now, we assume if models are listed, basic chat/generation is possible
                return provider_info
            else:
                print(f"DEBUG: Preferred provider {preferred_provider} not operational or no models found.")

        # If preferred provider fails or is not specified, check others
        for provider_name, check_func in provider_checks.items():
            if preferred_provider and provider_name == preferred_provider:
                continue # Already checked

            print(f"DEBUG: Checking alternative provider: {provider_name}")
            provider_info = check_func()
            if provider_info and provider_info["models"]:
                print(f"DEBUG: Alternative provider {provider_name} is operational.")
                return provider_info
            else:
                print(f"DEBUG: Alternative provider {provider_name} not operational or no models found.")

        print("DEBUG: No operational LLM provider found.")
        return None

if __name__ == '__main__':
    # Example Usage:
    manager = LLMProviderManager()

    print("\nAttempting to get any provider:")
    provider = manager.get_llm_provider()
    if provider:
        print(f"Selected Provider: {provider['provider_name']}")
        print(f"First few models: {provider['models'][:3]}")
        # Example: if provider['provider_name'] == 'gemini':
        #    model = provider['client'].GenerativeModel(provider['models'][0]) # or a specific model
        #    response = model.generate_content("Hello!")
        #    print(response.text)
    else:
        print("No LLM provider could be configured.")

    print("\nAttempting to get 'mistral' provider:")
    provider = manager.get_llm_provider(preferred_provider="mistral")
    if provider:
        print(f"Selected Provider: {provider['provider_name']}")
        print(f"First few models: {provider['models'][:3]}")
    else:
        print("Mistral provider could not be configured or has no models.")

    print("\nAttempting to get 'gemini' provider:")
    provider = manager.get_llm_provider(preferred_provider="gemini")
    if provider:
        print(f"Selected Provider: {provider['provider_name']}")
        print(f"First few models: {provider['models'][:3]}")
    else:
        print("Gemini provider could not be configured or has no models.")

    print("\nAttempting to get 'together_ai' provider:")
    provider = manager.get_llm_provider(preferred_provider="together_ai")
    if provider:
        print(f"Selected Provider: {provider['provider_name']}")
        print(f"First few models: {provider['models'][:3]}")
    else:
        print("Together AI provider could not be configured or has no models.")

    print("\nAttempting to get a non-existent provider:")
    provider = manager.get_llm_provider(preferred_provider="non_existent_provider")
    if provider:
        print(f"Selected Provider: {provider['provider_name']}")
    else:
        print("Non_existent_provider could not be configured (as expected).")

    print(f"\nDiscovered models cache: {manager.provider_models}")

    # To make this runnable, ensure .env file is in the same directory or project root
    # and contains GEMINI_API_KEY, TOGETHER_AI_API_KEY, MISTRAL_API_KEY
    # Also, ensure google-generativeai, together, mistralai, python-dotenv are installed.
    # Example .env:
    # GEMINI_API_KEY=your_gemini_key
    # TOGETHER_AI_API_KEY=your_together_key
    # MISTRAL_API_KEY=your_mistral_key

    # Note: The example usage will print DEBUG messages from the methods.
    # These should be changed to logging in a production system.

    # For Gemini, ensure the model supports 'generateContent'.
    # For TogetherAI, the model type check is basic. Might need refinement.
    # For Mistral, it lists all models; further filtering might be needed based on task.

    # A simple test for Gemini client usability (if selected)
    # if provider and provider.get('provider_name') == 'gemini':
    #     try:
    #         gemini_client = provider['client']
    #         # Pick a model known for chat/text generation
    #         # Example: find a model like 'gemini-1.5-flash' or 'gemini-pro'
    #         suitable_model_name = next((m for m in provider['models'] if 'flash' in m or 'pro' in m), None)
    #         if suitable_model_name:
    #             print(f"Testing Gemini with model: {suitable_model_name}")
    #             model_instance = gemini_client.GenerativeModel(suitable_model_name)
    #             response = model_instance.generate_content("Explain quantum physics in one sentence.")
    #             print(f"Gemini test response: {response.text}")
    #         else:
    #             print("No suitable Gemini model found for quick test.")
    #     except Exception as e:
    #         print(f"Error during Gemini client test: {e}")
