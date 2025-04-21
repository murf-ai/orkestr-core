# Test Provider

The **Test Provider** is a mock implementation of the `Provider` interface in Orkestr. It is designed solely for testing and development purposes. This provider simulates the behavior of a real cloud provider without actually interacting with any external systems or APIs.

## Usage

The test provider can be used to validate the functionality of Orkestr components, such as clusters, services, and the scheduler, without incurring any costs or requiring access to a cloud provider.

To enable the test provider, include it in the list of providers when initializing Orkestr:

```python
from orkestr_core.constants.providers import ProviderName, OrkestrRegion

orkestr = Orkestr(
    providers=[ProviderName.TEST_PROVIDER],
    regions=[OrkestrRegion.US_EAST_1]
)
```

## Disclaimer

The test provider is strictly for testing and development purposes. **Do not use it in production environments.**
