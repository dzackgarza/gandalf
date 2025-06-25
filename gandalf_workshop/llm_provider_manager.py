import os
from dotenv import load_dotenv
import google.generativeai as genai
from together import Together
from mistralai import Mistral # Corrected import name if it was MistralClient before
from typing import Optional, Dict, Any, List

class LLMProviderManager:
    """
    Manages selection and configuration of Large Language Model providers.
    It loads API keys from a .env file and can find a working LLM provider
    from a predefined list (Mistral, Gemini, Together AI).
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
            client = Mistral(api_key=self.mistral_api_key) # Use Mistral directly
            model_list = client.models.list()
            models = [model_info.id for model_info in model_list.data]
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
        The default search order is Mistral, Gemini, Together AI.
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

        provider_checks_ordered = [
            ("mistral", self._check_mistral),
            ("gemini", self._check_gemini),
            ("together_ai", self._check_together_ai),
        ]

        provider_map = dict(provider_checks_ordered)

        # 1. If a preferred provider is specified, try it first.
        if preferred_provider and preferred_provider in provider_map:
            print(f"DEBUG: Checking preferred provider: {preferred_provider}")
            check_func_preferred = provider_map[preferred_provider]
            provider_info = check_func_preferred()
            if provider_info and provider_info.get("models"):
                print(f"DEBUG: Preferred provider {preferred_provider} is operational.")
                return provider_info
            else:
                # If preferred provider is not operational, we still print a message
                # and then fall through to the ordered list check below.
                # The ordered list check will skip this preferred provider if it's encountered again.
                print(f"DEBUG: Preferred provider {preferred_provider} not operational, no models, or API key missing. Will try other providers.")

        # 2. Iterate through providers in the defined order.
        for provider_name_ordered, check_func_ordered in provider_checks_ordered:
            # If a preferred provider was specified and failed, and we encounter it here, skip it.
            if preferred_provider and provider_name_ordered == preferred_provider:
                continue

            print(f"DEBUG: Checking provider: {provider_name_ordered}")
            provider_info = check_func_ordered()
            if provider_info and provider_info.get("models"):
                print(f"DEBUG: Provider {provider_name_ordered} is operational.")
                return provider_info
            else:
                print(f"DEBUG: Provider {provider_name_ordered} not operational, no models, or API key missing.")

        print("DEBUG: No operational LLM provider found after checking all options.")
        return None

if __name__ == '__main__':
    manager = LLMProviderManager()

    print("\nAttempting to get any provider (Mistral should be first if key is valid):")
    provider = manager.get_llm_provider()
    if provider:
        print(f"Selected Provider: {provider['provider_name']}")
        print(f"First few models: {provider['models'][:3] if provider.get('models') else 'No models listed'}")
    else:
        print("No LLM provider could be configured.")

    print("\nAttempting to get 'mistral' provider explicitly:")
    provider = manager.get_llm_provider(preferred_provider="mistral")
    if provider:
        print(f"Selected Provider: {provider['provider_name']}")
        print(f"First few models: {provider['models'][:3] if provider.get('models') else 'No models listed'}")
    else:
        print("Mistral provider could not be configured or has no models.")

    print("\nAttempting to get 'gemini' provider explicitly:")
    provider = manager.get_llm_provider(preferred_provider="gemini")
    if provider:
        print(f"Selected Provider: {provider['provider_name']}")
        print(f"First few models: {provider['models'][:3] if provider.get('models') else 'No models listed'}")
    else:
        print("Gemini provider could not be configured or has no models.")

    print("\nAttempting to get 'together_ai' provider explicitly:")
    provider = manager.get_llm_provider(preferred_provider="together_ai")
    if provider:
        print(f"Selected Provider: {provider['provider_name']}")
        print(f"First few models: {provider['models'][:3] if provider.get('models') else 'No models listed'}")
    else:
        print("Together AI provider could not be configured or has no models.")

    print(f"\nFinal discovered models cache: {manager.provider_models}")
