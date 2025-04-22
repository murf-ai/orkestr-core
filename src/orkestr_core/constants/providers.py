from enum import Enum, auto
from typing import Dict, Optional
import json
class ProviderName(str, Enum):
    LAMBDA_LABS = "lambda_labs"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    TEST_PROVIDER = "test"

class LambdaLabsRegions(Enum):
    ASIA_NORTHEAST_1 = "asia-northeast-1"
    ASIA_NORTHEAST_2 = "asia-northeast-2"
    ASIA_SOUTH_1 = "asia-south-1"
    EUROPE_CENTRAL_1 = "europe-central-1"
    ME_WEST_1 = "me-west-1"
    US_EAST_1 = "us-east-1"
    US_EAST_2 = "us-east-2"
    US_MIDWEST_1 = "us-midwest-1"
    US_SOUTH_1 = "us-south-1"
    US_SOUTH_2 = "us-south-2"
    US_SOUTH_3 = "us-south-3"
    US_WEST_1 = "us-west-1"
    US_WEST_2 = "us-west-2"
    US_WEST_3 = "us-west-3"

class OrkestrRegion(Enum):
    """Orkestr's internal region representation."""
    US_EAST_1 = "US_EAST_1"
    US_EAST_2 = "US_EAST_2"
    US_EAST_3 = "US_EAST_3"
    US_WEST_1 = "US_WEST_1"
    US_WEST_2 = "US_WEST_2"
    US_WEST_3 = "US_WEST_3"
    US_SOUTH_1 = "US_SOUTH_1"
    US_SOUTH_2 = "US_SOUTH_2"
    US_SOUTH_3 = "US_SOUTH_3"
    US_CENTRAL = "US_CENTRAL"
    EU_WEST = "EU_WEST"
    EU_CENTRAL = "EU_CENTRAL"
    ASIA_EAST = "ASIA_EAST"
    ASIA_SOUTHEAST = "ASIA_SOUTHEAST"
    AUSTRALIA = "AUSTRALIA"
    SOUTH_AMERICA = "SOUTH_AMERICA"

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name  # Serialize the enum's name
        return super().default(obj)

class RegionMapper:
    """Maps Orkestr regions to provider-specific regions with fallback to default."""
    
    _REGION_MAPPINGS: Dict[OrkestrRegion, Dict[ProviderName, str]] = {
        OrkestrRegion.US_EAST_1: {
            ProviderName.AWS: "us-east-1",
            ProviderName.AZURE: "eastus",
            ProviderName.GCP: "us-east1",
            ProviderName.LAMBDA_LABS: "us-east-1",
        },
        OrkestrRegion.US_EAST_2: {
            ProviderName.AWS: "us-east-2",
            ProviderName.AZURE: "eastus2",
            ProviderName.GCP: "us-east4",
            ProviderName.LAMBDA_LABS: "us-east-2",
        },
        OrkestrRegion.US_EAST_3: {
            ProviderName.AWS: "us-east-2",  # AWS doesn't have east-3, using east-2
            ProviderName.AZURE: "eastus",   # Azure doesn't have east-3, using eastus
            ProviderName.GCP: "us-east1",  # GCP doesn't have east-3, using east-1
            ProviderName.LAMBDA_LABS: "us-east-3",
        },
        OrkestrRegion.US_WEST_1: {
            ProviderName.AWS: "us-west-2",
            ProviderName.AZURE: "westus2",
            ProviderName.GCP: "us-west1",
            ProviderName.LAMBDA_LABS: "us-west-1",
        },
        OrkestrRegion.US_WEST_2: {
            ProviderName.AWS: "us-west-1",
            ProviderName.AZURE: "westus",
            ProviderName.GCP: "us-west2",
            ProviderName.LAMBDA_LABS: "us-west-2",
        },
        OrkestrRegion.US_WEST_3: {
            ProviderName.AWS: "us-west-2",  # AWS doesn't have west-3, using west-2
            ProviderName.AZURE: "westus3",
            ProviderName.GCP: "us-west3",
            ProviderName.LAMBDA_LABS: "us-west-3",
        },
        OrkestrRegion.US_SOUTH_1: {
            ProviderName.LAMBDA_LABS: "us-south-1",
        },
        OrkestrRegion.US_SOUTH_2: {
            ProviderName.LAMBDA_LABS: "us-south-2",
        },
        OrkestrRegion.US_SOUTH_3: {
            ProviderName.LAMBDA_LABS: "us-south-3",
        },
        OrkestrRegion.US_CENTRAL: {
            ProviderName.AWS: "us-east-2",  # AWS doesn't have central, using east-2
            ProviderName.AZURE: "centralus",
            ProviderName.GCP: "us-central1",
            ProviderName.LAMBDA_LABS: "us-midwest-1",
        },
        OrkestrRegion.EU_WEST: {
            ProviderName.AWS: "eu-west-1",
            ProviderName.AZURE: "westeurope",
            ProviderName.GCP: "europe-west1",
            ProviderName.LAMBDA_LABS: "europe-central-1",
        },
        OrkestrRegion.EU_CENTRAL: {
            ProviderName.AWS: "eu-central-1",
            ProviderName.AZURE: "germanywestcentral",
            ProviderName.GCP: "europe-central2",
            ProviderName.LAMBDA_LABS: "europe-central-1",
        },
        OrkestrRegion.ASIA_EAST: {
            ProviderName.AWS: "ap-east-1",
            ProviderName.AZURE: "eastasia",
            ProviderName.GCP: "asia-east1",
            ProviderName.LAMBDA_LABS: "asia-northeast-1",
        },
        OrkestrRegion.ASIA_SOUTHEAST: {
            ProviderName.AWS: "ap-southeast-1",
            ProviderName.AZURE: "southeastasia",
            ProviderName.GCP: "asia-southeast1",
            ProviderName.LAMBDA_LABS: "asia-south-1",
        },
        OrkestrRegion.AUSTRALIA: {
            ProviderName.AWS: "ap-southeast-2",
            ProviderName.AZURE: "australiaeast",
            ProviderName.GCP: "australia-southeast1",
            ProviderName.LAMBDA_LABS: "asia-northeast-2",
        },
        OrkestrRegion.SOUTH_AMERICA: {
            ProviderName.AWS: "sa-east-1",
            ProviderName.AZURE: "brazilsouth",
            ProviderName.GCP: "southamerica-east1",
            ProviderName.LAMBDA_LABS: "me-west-1",
        },
    }
    
    # Default regions for each provider
    _DEFAULT_REGIONS: Dict[ProviderName, str] = {
        ProviderName.AWS: "us-east-1",
        ProviderName.AZURE: "eastus",
        ProviderName.GCP: "us-central1",
        ProviderName.LAMBDA_LABS: "us-east-3",
        ProviderName.TEST_PROVIDER: "us-east-1",
    }
    
    @classmethod
    def get_provider_region(cls, orkestr_region: OrkestrRegion, provider: ProviderName) -> str:
        """
        Get the provider-specific region ID for a given Orkestr region.
        Falls back to the default region if mapping doesn't exist.
        """
        try:
            return cls._REGION_MAPPINGS[orkestr_region][provider]
        except KeyError:
            # Region mapping not found, return default region for provider
            return cls._DEFAULT_REGIONS[provider]
    
    @classmethod
    def add_region_mapping(cls, orkestr_region: OrkestrRegion, provider: ProviderName, provider_region: str) -> None:
        """Add or update a region mapping."""
        if orkestr_region not in cls._REGION_MAPPINGS:
            cls._REGION_MAPPINGS[orkestr_region] = {}
        
        cls._REGION_MAPPINGS[orkestr_region][provider] = provider_region
    
    @classmethod
    def set_default_region(cls, provider: ProviderName, region: str) -> None:
        """Set the default region for a provider."""
        cls._DEFAULT_REGIONS[provider] = region
