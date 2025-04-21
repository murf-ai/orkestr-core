from ..base.datastore import Datastore

# Global datastore instance
datastore: Datastore = None

def set_global_datastore(ds: Datastore):
    print("SETTING GLOBAL DATASTORE")
    global datastore
    datastore = ds
    print(f"Datastore set to {datastore}")

def get_global_datastore() -> Datastore:
    if datastore is None:
        raise ValueError("Global datastore is not initialized.")
    return datastore