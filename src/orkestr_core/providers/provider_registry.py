from typing import Dict, Type
from orkestr_core.base.provider import Provider
from orkestr_core.constants.providers import ProviderName
from orkestr_core.providers.lambda_labs.provider import LambdaLabsProvider
from orkestr_core.providers.test_provider import TestProvider
from orkestr_core.util.logger import setup_logger

logger = setup_logger(__name__)

# Registry to store provider-specific implementations
class ProviderRegistry:
    _provider_implementations: Dict[str, Type[Provider]] = {}

    def __init__(self):
        self._provider_implementations = {
            ProviderName.LAMBDA_LABS: LambdaLabsProvider,
            ProviderName.TEST_PROVIDER: TestProvider,
        }
    
    def register_provider(self, provider_name: str, provider_class: Type[Provider]):
        """
        Registers a new provider implementation.
        """
        if provider_name in self._provider_implementations:
            raise ValueError(f"Provider {provider_name} is already registered.")
        self._provider_implementations[provider_name] = provider_class
        logger.info(f"Provider {provider_name} registered successfully.")

    def get_provider(self, provider_name: str) -> Type[Provider]:
        """
        Retrieves a provider implementation by name.
        """
        provider_class = self._provider_implementations.get(provider_name)
        if not provider_class:
            raise ValueError(f"Provider {provider_name} is not registered.")
        return provider_class
