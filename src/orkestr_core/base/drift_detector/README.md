# Drift Detector

The Drift Detector ensures that the desired state of infrastructure and services matches the actual state by identifying and resolving discrepancies (drift).

## How It Works

Every `Provider` implementation will have a `check_and_sync_infra` or `acheck_and_sync_infra` function. This fetches the current state of all the nodes in that provider. The provider state is then compared with the state in the datastore. If there are any discrepancies, the drift detector will detect it, and the provider will take the necessary action to resolve the drift.
