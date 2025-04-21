from orkestr_core.constants.providers import ProviderName, OrkestrRegion
from orkestr_core.providers.provider_registry import ProviderRegistry
from orkestr_core.base.provider import Provider 
from typing import Type, List
from orkestr_core.util.logger import setup_logger
from orkestr_core.base.service import Service
from orkestr_core.base.scheduler import AsyncScheduler, SchedulerAction
from orkestr_core.base.events.event_bus import AsyncEventBus

logger = setup_logger(__name__)

class Orkestr:

    def __init__(self, providers: list[ProviderName], regions: list[OrkestrRegion] ):
        self.provider_names = providers
        self.regions = regions
        self.services: List[Service] = []
        self.scheduler = AsyncScheduler(interval=15, actions=[])
        self.event_bus = AsyncEventBus()
        self.providers = self.initialize_providers()
        self.cluster_orchestrator = None
        self.node_orchestrator = None
        self.node_event_handler = None
        self.cluster_event_handler = None
        self.initialize_orchestrators()
        self.initialize_scheduler()
        logger.info("Orkestr initialized and scheduler started.")        

    def initialize_providers(self) -> list[Type[Provider]]:
        """
        Initialize the providers and their configurations.
        """
        providers = []
        for provider in self.provider_names:
            provider_registry = ProviderRegistry()
            provider_class = provider_registry.get_provider(provider)
            provider_instance = provider_class(event_bus=self.event_bus)
            providers.append(provider_instance)
        return providers
    
    def initialize_orchestrators(self):
        """
        Initialize the orchestrators and event handlers.
        Event handlers will start listening to events.
        The orchestrators will be responsible for managing the clusters and nodes on the cloud providers.
        """
        from orkestr_core.base.orchestrator import NodeOrchestrator, ClusterOrchestrator
        from orkestr_core.base.events import NodeEventHandler, ClusterEventHandler

        self.cluster_orchestrator = ClusterOrchestrator(event_bus=self.event_bus, provider_registry=ProviderRegistry())
        self.node_orchestrator = NodeOrchestrator(event_bus=self.event_bus, provider_registry=ProviderRegistry())
        self.node_event_handler = NodeEventHandler(event_bus=self.event_bus, orchestrator=self.node_orchestrator)
        self.cluster_event_handler = ClusterEventHandler(event_bus=self.event_bus, orchestrator=self.cluster_orchestrator)

        self.node_event_handler.register_event_handlers()
        self.cluster_event_handler.register_event_handlers()
    
    def initialize_scheduler(self):
        """
        Initialize the scheduler.
        """
        for provider in self.providers:
            sync_action = SchedulerAction(
                name=f"Sync {provider.__class__.__name__}",
                action_func=provider.acheck_and_sync_infra,
                action_parameters={
                    "regions": self.regions,
                }
            )
            self.scheduler.add_actions(
                [sync_action]
            )

    async def start_scheduler(self):
        """
        Start the scheduler.
        """
        await self.scheduler.start()

    async def stop_scheduler(self):
        """
        Stop the scheduler.
        """
        await self.scheduler.stop()
