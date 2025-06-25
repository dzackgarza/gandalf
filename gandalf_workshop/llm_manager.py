#!/usr/bin/env python3
"""
Smart LLM Provider Cycling System

A production-ready multi-provider LLM system with automatic rate limit handling,
provider switching, and model cycling. Supports Gemini, Mistral, Grok, and Together AI.

Author: Assistant (Claude)
License: MIT
"""

import os
import time
import json
import random
from typing import Type, Any, List, Dict, Callable, Optional, Annotated
from dataclasses import dataclass, field

try:
    from crewai import (
        Agent,
        Task,
        Crew,
    )  # , LLM (LLM class itself is not directly used here)
    from crewai.tools import BaseTool
    from pydantic import (
        BaseModel,
        Field as PydanticField,
    )  # Alias to avoid conflict with dataclass field

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print(
        "⚠️  CrewAI not available. Core cycling system will work, but CrewAI integration disabled."
    )


# Multi-Provider Configuration
@dataclass
class ProviderConfig:
    """Configuration for a specific LLM provider"""

    name: str
    models: List[str]
    api_key_env: str
    rate_limit_patterns: List[str] = field(default_factory=list)
    max_requests_per_minute: int = 60
    cooldown_time: int = 300  # 5 minutes
    priority: int = 1  # Lower is higher priority

    def __post_init__(self):
        if not self.rate_limit_patterns:
            self.rate_limit_patterns = [
                f"{self.name.lower()}",
                "rate limit",
                "quota",
                "429",
                "503",
            ]


# Default provider configurations
DEFAULT_PROVIDER_CONFIGS = [
    ProviderConfig(
        name="gemini",
        models=[
            "gemini/gemini-2.0-flash",  # Example model names, actual might differ for Langchain
            "gemini/gemini-1.5-pro",
            "gemini/gemini-1.5-flash",
            "gemini/gemini-pro",
        ],
        api_key_env="GEMINI_API_KEY",
        rate_limit_patterns=["gemini", "google", "rate limit", "quota exceeded"],
        max_requests_per_minute=60,
        priority=1,
    ),
    ProviderConfig(
        name="mistral",
        models=[
            "mistral/mistral-large-latest",  # Example model names
            "mistral/mistral-medium-latest",
            "mistral/mistral-small-latest",
            "mistral/pixtral-12b-2409",
        ],
        api_key_env="MISTRAL_API_KEY",
        rate_limit_patterns=["mistral", "rate limit", "quota"],
        max_requests_per_minute=1000,  # Mistral typically has higher limits
        priority=2,
    ),
    ProviderConfig(
        name="groq",  # Changed from 'grok' to 'groq' for langchain compatibility
        models=[
            "llama3-8b-8192",  # Groq uses specific model IDs like this
            "llama3-70b-8192",
            "gemma-7b-it",
            "mixtral-8x7b-32768",  # This one was decommissioned, but good to have a list
            # Will need to be updated with current valid Groq models
        ],
        api_key_env="GROQ_API_KEY",  # Changed from GROK_API_KEY to GROQ_API_KEY
        rate_limit_patterns=[
            "groq",
            "xai",
            "rate limit",
            "429",
            "model_decommissioned",
        ],
        max_requests_per_minute=200,  # Placeholder, actual limits vary by model on Groq
        priority=3,
    ),
    ProviderConfig(
        name="together",
        models=[
            "together/meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",  # Example model names
            "together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "together/mistralai/Mixtral-8x7B-Instruct-v0.1",
            "together/Qwen/Qwen2.5-7B-Instruct-Turbo",
        ],
        api_key_env="TOGETHER_AI_API_KEY",
        rate_limit_patterns=["together", "rate limit", "quota"],
        max_requests_per_minute=500,
        priority=4,
    ),
]


# Provider state tracking
@dataclass
class ProviderState:
    """Track the state of each provider"""

    config: ProviderConfig
    current_model_index: int = 0
    request_count: int = 0
    last_request_time: float = 0
    last_rate_limit_time: float = 0
    consecutive_failures: int = 0
    is_rate_limited: bool = False

    def get_current_model(self) -> str:
        """Get the current model for this provider"""
        if not self.config.models:
            # This case should ideally be prevented by _initialize_providers
            raise ValueError(f"No models configured for provider {self.config.name}")
        return self.config.models[self.current_model_index % len(self.config.models)]

    def cycle_to_next_model(self):
        """Switch to the next model in this provider"""
        if not self.config.models:
            return
        self.current_model_index = (self.current_model_index + 1) % len(
            self.config.models
        )
        print(f"🔄 Cycling {self.config.name} to model: {self.get_current_model()}")

    def record_request(self):
        """Record a successful request"""
        self.request_count += 1
        self.last_request_time = time.time()
        self.consecutive_failures = 0
        # self.is_rate_limited = False # A successful request might not mean it's not rate limited for next one.
        # Let is_available manage this state.

    def record_rate_limit(self):
        """Record a rate limit hit"""
        self.last_rate_limit_time = time.time()
        self.consecutive_failures += 1
        self.is_rate_limited = True
        print(
            f"⏱️  {self.config.name} rate limited - cooling down for {self.config.cooldown_time}s"
        )

    def is_available(self) -> bool:
        """Check if this provider is available (not rate limited)"""
        if not self.is_rate_limited:
            return True

        # Check if cooldown period has passed
        time_since_limit = time.time() - self.last_rate_limit_time
        if time_since_limit > self.config.cooldown_time:
            self.is_rate_limited = False
            self.consecutive_failures = 0  # Reset failures after cooldown
            print(f"✅ {self.config.name} cooldown complete - available again")
            return True

        return False

    def should_cycle_model(self) -> bool:
        """Check if we should cycle to next model in this provider"""
        # Cycle after N consecutive failures OR after M successful requests to try other models
        return self.consecutive_failures >= 2 or (
            self.request_count > 0 and self.request_count % 10 == 0
        )


class SmartLLMProviderManager:
    """
    Smart LLM Provider Manager with automatic cycling and rate limit handling
    """

    def __init__(
        self, provider_configs: List[ProviderConfig] = None, auto_load_env: bool = True
    ):
        # Explicitly load .env here to ensure keys are available for this instance
        try:
            from dotenv import load_dotenv

            if load_dotenv():  # Returns True if .env was found and loaded
                print("✅ SmartLLMProviderManager: .env loaded by manager constructor.")
            else:
                print(
                    "⚠️ SmartLLMProviderManager: .env not found by manager constructor or already loaded."
                )
        except ImportError:
            print(
                "⚠️ SmartLLMProviderManager: python-dotenv not installed, cannot load .env from manager."
            )
            # auto_load_env = False # Or rely on prior loading

        if auto_load_env and not os.path.exists(
            ".env"
        ):  # Redundant if load_dotenv handles it, but for clarity
            print(
                "⚠️ SmartLLMProviderManager: auto_load_env is True, but .env file not found at start of __init__."
            )

        # The original _load_env_file was simplified; this explicit call is more direct.

        # Use a copy of default configs to avoid modifying the global list
        self.provider_configs_template = provider_configs or [
            cfg for cfg in DEFAULT_PROVIDER_CONFIGS
        ]
        self.providers: Dict[str, ProviderState] = {}
        self.current_provider_name: Optional[str] = None  # Changed name for clarity
        self.total_requests = 0
        self.total_failures = 0
        self.provider_switch_count = 0

        self._initialize_providers()

    def _load_env_file(self):
        """Load environment variables from .env file"""
        # Simplified: relies on python-dotenv being called by the main script (run_commission.py)
        if os.path.exists(".env"):
            print(
                f"✅ SmartLLMProviderManager: .env file found. Assuming it's loaded by main script."
            )
        else:
            print(
                "⚠️  SmartLLMProviderManager: No .env file found. Make sure API keys are set in environment."
            )

    def _initialize_providers(self):
        """Initialize provider states based on available API keys"""
        groq_api_key = os.getenv("GROQ_API_KEY")

        live_groq_models = []
        if groq_api_key:
            try:
                import requests

                response = requests.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {groq_api_key}"},
                    timeout=5,
                )
                response.raise_for_status()
                models_data = response.json()
                for model_info in models_data.get("data", []):
                    model_id = model_info.get("id")
                    if model_id and not any(
                        kw in model_id
                        for kw in ["whisper", "guard", "embedding", "rerank"]
                    ):
                        live_groq_models.append(model_id)
                if live_groq_models:
                    print(f"✅ Fetched live models from Groq: {live_groq_models}")
                else:
                    print(
                        "⚠️ Could not fetch any suitable live models from Groq, will use defaults if any."
                    )
            except Exception as e:
                print(
                    f"⚠️ Error fetching live Groq models: {e}. Will use default/static list for Groq if configured."
                )

        for config_template in self.provider_configs_template:
            if os.getenv(config_template.api_key_env):
                config = ProviderConfig(
                    name=config_template.name,
                    models=list(config_template.models),
                    api_key_env=config_template.api_key_env,
                    rate_limit_patterns=list(config_template.rate_limit_patterns),
                    max_requests_per_minute=config_template.max_requests_per_minute,
                    cooldown_time=config_template.cooldown_time,
                    priority=config_template.priority,
                )

                if config.name == "grok":
                    config.name = "groq"
                    config.api_key_env = "GROQ_API_KEY"
                    if live_groq_models:
                        config.models = live_groq_models
                    else:
                        config.models = [
                            "llama3-8b-8192",
                            "gemma2-9b-it",
                            "llama-3.1-8b-instant",
                        ]

                if not config.models:
                    print(
                        f"⚠️  Skipping {config.name} - no models configured or fetched."
                    )
                    continue

                self.providers[config.name] = ProviderState(config)
                print(
                    f"✅ Initialized provider: {config.name} with models: {config.models}"
                )
            else:
                # Use config_template here as config is not defined in this branch
                print(
                    f"⚠️  Skipping {config_template.name} - no API key found ({config_template.api_key_env})"
                )

        self.current_provider_name = self._get_best_available_provider_name()
        if self.current_provider_name:
            print(
                f"🎯 Initial provider: {self.current_provider_name} - Model: {self.providers[self.current_provider_name].get_current_model()}"
            )
        else:
            print(
                "❌ FATAL: No LLM providers could be initialized by SmartLLMProviderManager. Check API key configurations and provider availability."
            )
            raise RuntimeError(
                "FATAL: No LLM providers could be initialized. Check API key configurations and provider availability."
            )

    def _get_best_available_provider_name(self) -> Optional[str]:
        available_providers = [
            (name, state)
            for name, state in self.providers.items()
            if state.is_available() and state.config.models
        ]

        if not available_providers:
            print("⚠️  No providers currently available for selection!")
            if self.providers:
                sorted_by_priority = sorted(
                    self.providers.values(), key=lambda s: s.config.priority
                )
                if sorted_by_priority:
                    print(
                        f"⚠️ No providers immediately available. Defaulting to highest priority: {sorted_by_priority[0].config.name}"
                    )
                    return sorted_by_priority[0].config.name
            return None

        available_providers.sort(key=lambda x: x[1].config.priority)
        return available_providers[0][0]

    def _detect_rate_limit_for_provider(
        self, error_msg: str, provider_name: str
    ) -> bool:
        if not error_msg:
            print(
                f"⚠️ Empty error message received for {provider_name}, treating as potential rate limit."
            )
            return True

        error_lower = error_msg.lower()
        if provider_name not in self.providers:
            print(
                f"⚠️ Provider {provider_name} not found in configured providers for rate limit detection."
            )
            return any(
                pattern in error_lower
                for pattern in ["rate limit", "429", "quota", "503"]
            )

        provider_config = self.providers[provider_name].config

        for pattern in provider_config.rate_limit_patterns:
            if pattern.lower() in error_lower:
                print(
                    f"🔍 Detected rate limit for {provider_name} due to pattern: '{pattern}' in error: '{error_msg[:100]}...'"
                )
                return True

        general_patterns = [
            "rate limit",
            "429",
            "quota exceeded",
            "too many requests",
            "model_decommissioned",
        ]
        if any(pattern in error_lower for pattern in general_patterns):
            print(
                f"🔍 Detected general rate limit pattern for {provider_name} in error: '{error_msg[:100]}...'"
            )
            return True
        return False

    def get_current_llm_instance(self) -> Optional[Any]:
        if not self.current_provider_name:
            print(
                "❌ Attempting to get LLM instance, but no current provider selected. Trying to handle..."
            )
            self._handle_no_available_provider()  # This might set a provider or wait
            if not self.current_provider_name:  # Check again after handling
                print(
                    "❌ FATAL: No LLM provider could be selected or made available after attempting to handle."
                )
                raise RuntimeError(
                    "FATAL: No LLM provider could be selected or made available after attempting to handle."
                )

        state = self.providers[self.current_provider_name]
        model_id = state.get_current_model()
        api_key = os.getenv(state.config.api_key_env)

        if not api_key:
            print(
                f"❌ FATAL: API key {state.config.api_key_env} not found for provider {self.current_provider_name} although provider was selected."
            )
            # This state should ideally not be reached if _initialize_providers works correctly,
            # but as a safeguard:
            current_provider_before_failure = self.current_provider_name
            failure_report = self.handle_llm_failure(
                f"API key {state.config.api_key_env} missing",
                is_explicit_rate_limit=False,
            )
            if (
                self.current_provider_name == current_provider_before_failure
                and not failure_report.get("switch_occurred")
            ):
                # If handler couldn't switch away from this provider lacking a key, it's a fatal setup error for this provider.
                raise RuntimeError(
                    f"FATAL: API key {state.config.api_key_env} for {self.current_provider_name} not found, and could not switch provider."
                )
            return (
                self.get_current_llm_instance()
            )  # Retry with potentially new provider

        print(
            f"🔧 Attempting to instantiate LLM for Provider: {self.current_provider_name}, Model: {model_id}"
        )

        try:
            if self.current_provider_name == "groq":
                from langchain_groq import ChatGroq

                return ChatGroq(model=model_id, api_key=api_key)
            elif self.current_provider_name == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI

                langchain_model_id = (
                    model_id.split("/")[-1] if "/" in model_id else model_id
                )
                return ChatGoogleGenerativeAI(
                    model=langchain_model_id, google_api_key=api_key
                )
            elif self.current_provider_name == "mistral":
                from langchain_mistralai import ChatMistralAI

                langchain_model_id = (
                    model_id.split("/")[-1] if "/" in model_id else model_id
                )
                return ChatMistralAI(model=langchain_model_id, api_key=api_key)
            elif self.current_provider_name == "together":
                from langchain_together import ChatTogether

                langchain_model_id = (
                    model_id.split("/")[-1]
                    if model_id.startswith("together/")
                    else model_id
                )
                if not any(
                    p in langchain_model_id
                    for p in ["meta-llama/", "mistralai/", "Qwen/"]
                ):
                    pass
                return ChatTogether(model=langchain_model_id, api_key=api_key)
            else:
                print(
                    f"⚠️ LLM client for provider '{self.current_provider_name}' is not implemented in SmartLLMProviderManager."
                )
                return None
        except ImportError as e:
            print(
                f"⚠️ Failed to import Langchain client for {self.current_provider_name}: {e}. Make sure related packages are installed."
            )
            state.is_rate_limited = True
            state.last_rate_limit_time = time.time()
            print(
                f"Temporarily disabling {self.current_provider_name} due to import error."
            )
            self.current_provider_name = self._get_best_available_provider_name()
            if self.current_provider_name:
                return self.get_current_llm_instance()
            else:  # No other provider available or switch failed
                raise RuntimeError(
                    f"FATAL: Failed to import LLM client for {state.config.name} and no fallback provider could be selected."
                )

        except Exception as e:  # Catch any other error during LLM instantiation
            print(
                f"❌ Error instantiating LLM for {self.current_provider_name} with model {model_id}: {e}"
            )
            current_provider_before_failure = self.current_provider_name
            failure_report = self.handle_llm_failure(
                str(e), is_explicit_rate_limit=False
            )  # Try to handle (e.g. cycle model or provider)

            if (
                self.current_provider_name == current_provider_before_failure
                and not failure_report.get("switch_occurred")
            ):
                # If provider and model are still the same, and no switch occurred (e.g. only one model, one provider)
                raise RuntimeError(
                    f"FATAL: Failed to instantiate LLM for {self.current_provider_name} with model {model_id} and could not switch: {e}"
                )
            elif failure_report.get("switch_occurred"):
                print(
                    f"Retrying LLM instantiation after failure handling resulted in a switch: {failure_report}"
                )
                return (
                    self.get_current_llm_instance()
                )  # Recursive call with new provider/model
            else:  # Should not be reached if logic is correct, but as a fallback
                raise RuntimeError(
                    f"FATAL: Unhandled error during LLM instantiation for {self.current_provider_name}, model {model_id}: {e}"
                )

    def _handle_no_available_provider(self):
        print(
            "Attempting to handle situation with no immediately available providers..."
        )
        recovering_providers = sorted(
            [p for p in self.providers.values() if p.is_rate_limited],
            key=lambda p: (p.last_rate_limit_time + p.config.cooldown_time),
        )
        if recovering_providers:
            next_available_provider = recovering_providers[0]
            wait_time = (
                next_available_provider.last_rate_limit_time
                + next_available_provider.config.cooldown_time
            ) - time.time()
            if wait_time > 0:
                print(
                    f"⏳ Waiting for {next_available_provider.config.name} to become available in {wait_time:.0f}s..."
                )
            self.current_provider_name = self._get_best_available_provider_name()
            if self.current_provider_name:
                print(
                    f"✅ Provider {self.current_provider_name} selected after handling no-availability."
                )
                return
        print("❌ Critical: No providers are configured or can become available.")

    def get_current_provider_info(self) -> Dict[str, Any]:
        if not self.current_provider_name:
            return {"error": "No current provider"}

        state = self.providers[self.current_provider_name]
        return {
            "name": self.current_provider_name,
            "model": state.get_current_model(),
            "api_key_env": state.config.api_key_env,
            "requests_on_model": state.request_count,
            "consecutive_failures_on_model": state.consecutive_failures,
            "is_available": state.is_available(),
            "is_rate_limited": state.is_rate_limited,
            "max_rpm": state.config.max_requests_per_minute,
            "priority": state.config.priority,
        }

    def handle_llm_failure(
        self, error_msg: str, is_explicit_rate_limit: Optional[bool] = None
    ) -> Dict[str, Any]:
        self.total_failures += 1
        action_taken_details = {"switch_occurred": False, "action_taken": "none"}

        if not self.current_provider_name:
            print("❌ Cannot handle LLM failure: No current provider selected.")
            self.current_provider_name = self._get_best_available_provider_name()
            if not self.current_provider_name:
                action_taken_details["error"] = "No provider available to switch to."
                return action_taken_details
            else:
                action_taken_details["info"] = (
                    f"Switched to {self.current_provider_name} as no provider was current."
                )

        current_state = self.providers[self.current_provider_name]

        if is_explicit_rate_limit is None:
            is_rate_limit_detected = self._detect_rate_limit_for_provider(
                error_msg, self.current_provider_name
            )
        else:
            is_rate_limit_detected = is_explicit_rate_limit

        if is_rate_limit_detected:
            print(
                f"🔄 Rate limit determined for {self.current_provider_name}. Error: {error_msg[:100]}..."
            )
            current_state.record_rate_limit()

            if len(current_state.config.models) > 1:
                current_state.cycle_to_next_model()
                action_taken_details.update(
                    {
                        "switch_occurred": True,
                        "new_provider": self.current_provider_name,
                        "action_taken": "model_cycle_due_to_rate_limit",
                        "new_model": current_state.get_current_model(),
                    }
                )
                print(
                    f"✅ Cycled model for {self.current_provider_name} to {current_state.get_current_model()} due to rate limit."
                )

            new_provider_name = self._get_best_available_provider_name()

            if new_provider_name and new_provider_name != self.current_provider_name:
                old_provider_name = self.current_provider_name
                self.current_provider_name = new_provider_name
                self.provider_switch_count += 1
                action_taken_details.update(
                    {
                        "switch_occurred": True,
                        "new_provider": new_provider_name,
                        "action_taken": "provider_switch_due_to_rate_limit",
                        "old_provider": old_provider_name,
                        "new_model": self.providers[
                            new_provider_name
                        ].get_current_model(),
                    }
                )
                print(
                    f"🔀 Switched from rate-limited {old_provider_name} to {new_provider_name} (Model: {action_taken_details['new_model']})."
                )
            elif new_provider_name and new_provider_name == self.current_provider_name:
                print(
                    f"⚠️  {self.current_provider_name} is rate limited, and no other providers are immediately available or better. Cooldown active."
                )
                action_taken_details["info"] = (
                    f"{self.current_provider_name} is rate-limited; awaiting cooldown."
                )
            elif not new_provider_name:
                print(
                    f"⚠️ All providers appear to be rate-limited or unavailable. {self.current_provider_name} is in cooldown."
                )
                action_taken_details["error"] = (
                    "All providers unavailable or rate-limited."
                )
        else:
            current_state.consecutive_failures += 1
            print(
                f"⚠️ Non-rate-limit failure for {self.current_provider_name} (consecutive: {current_state.consecutive_failures}). Error: {error_msg[:100]}..."
            )
            if (
                current_state.should_cycle_model()
                and len(current_state.config.models) > 1
            ):
                current_state.cycle_to_next_model()
                action_taken_details.update(
                    {
                        "switch_occurred": True,
                        "new_provider": self.current_provider_name,
                        "action_taken": "model_cycle_due_to_other_failures",
                        "new_model": current_state.get_current_model(),
                    }
                )
                print(
                    f"✅ Cycled model for {self.current_provider_name} to {current_state.get_current_model()} due to consecutive failures."
                )
            else:
                if current_state.consecutive_failures >= 3:
                    print(
                        f"⚠️ Too many consecutive generic failures on {self.current_provider_name}. Attempting provider switch."
                    )
                    current_state.is_rate_limited = True
                    current_state.last_rate_limit_time = time.time()

                    new_provider_name = self._get_best_available_provider_name()
                    if (
                        new_provider_name
                        and new_provider_name != self.current_provider_name
                    ):
                        old_provider_name = self.current_provider_name
                        self.current_provider_name = new_provider_name
                        self.provider_switch_count += 1
                        action_taken_details.update(
                            {
                                "switch_occurred": True,
                                "new_provider": new_provider_name,
                                "action_taken": "provider_switch_due_to_generic_failures",
                                "old_provider": old_provider_name,
                                "new_model": self.providers[
                                    new_provider_name
                                ].get_current_model(),
                            }
                        )
                        print(
                            f"🔀 Switched from {old_provider_name} (due to generic failures) to {new_provider_name} (Model: {action_taken_details['new_model']})."
                        )
                    else:
                        current_state.is_rate_limited = False
                        print(
                            f"⚠️ Could not switch provider away from {self.current_provider_name} despite multiple generic failures."
                        )
                        action_taken_details["info"] = (
                            "Could not switch provider despite generic failures."
                        )
        return action_taken_details

    def record_success(self):
        self.total_requests += 1
        if self.current_provider_name and self.current_provider_name in self.providers:
            self.providers[self.current_provider_name].record_request()

    def get_status_report(self) -> Dict[str, Any]:
        provider_statuses = {}
        for name, state in self.providers.items():
            provider_statuses[name] = {
                "current_model": (
                    state.get_current_model() if state.config.models else "N/A"
                ),
                "is_available": state.is_available(),
                "is_rate_limited": state.is_rate_limited,
                "consecutive_failures": state.consecutive_failures,
                "request_count": state.request_count,
                "max_rpm": state.config.max_requests_per_minute,
                "priority": state.config.priority,
                "api_key_env": state.config.api_key_env,
            }

        success_rate = (
            (
                (self.total_requests - self.total_failures)
                / max(self.total_requests, 1)
                * 100
            )
            if self.total_requests > 0
            else 0.0
        )

        current_model_display = "N/A"
        if self.current_provider_name and self.current_provider_name in self.providers:
            current_model_display = self.providers[
                self.current_provider_name
            ].get_current_model()

        return {
            "current_provider": self.current_provider_name,
            "current_model_overall": current_model_display,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "provider_switches": self.provider_switch_count,
            "success_rate": f"{success_rate:.1f}%",
            "providers": provider_statuses,
        }

    def force_switch_provider(self, provider_name: str = None) -> bool:
        if not self.providers:
            print("❌ Cannot force switch: No providers initialized.")
            return False

        old_provider = self.current_provider_name

        if provider_name:
            if (
                provider_name in self.providers
                and self.providers[provider_name].is_available()
            ):
                self.current_provider_name = provider_name
            else:
                print(
                    f"❌ Cannot switch to {provider_name} - not available or not configured. Trying auto-switch."
                )
                new_provider_name = self._get_best_available_provider_name()
                if new_provider_name:
                    self.current_provider_name = new_provider_name
                else:
                    print(f"❌ Auto-switch failed: No other provider available.")
                    return False
        else:
            new_provider_name = self._get_best_available_provider_name()
            if new_provider_name:
                self.current_provider_name = new_provider_name
            else:
                print(f"❌ Auto-switch failed: No other provider available.")
                return False

        if self.current_provider_name != old_provider:
            self.provider_switch_count += 1
            print(
                f"🔀 Forced switch: Previous: {old_provider}, New: {self.current_provider_name} (Model: {self.providers[self.current_provider_name].get_current_model()})"
            )
            return True
        elif self.current_provider_name == old_provider:
            print(
                f"ℹ️  Forced switch resulted in same provider: {self.current_provider_name}. No actual switch occurred beyond potential model cycle if applicable."
            )
            return False
        return False


def create_smart_llm_manager(**kwargs) -> SmartLLMProviderManager:
    """Create a smart LLM provider manager with default settings"""
    return SmartLLMProviderManager(**kwargs)


# Removed demo_smart_provider_cycling and if __name__ == "__main__": block
# to prevent SyntaxError when imported as a module.
