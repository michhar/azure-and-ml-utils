# Azure Resource-Related Scripts/Examples

| Script | Description | Necessary Installs | Docs |
|---|---|---|---|
| download_from_blob_legacy.py | Download files from Azure Blob Storage | [Microsoft Azure Storage SDK for Python v2.1](https://pypi.org/project/azure-storage-blob/2.1.0/) | |
| extract_tenantids.py | Simple script to extract tenant ids | [Azure SDK](https://github.com/Azure/azure-sdk-for-python#installation) | |
| ingress_to_kusto.py | Ingress local csv timeseries data to Kusto/ADX | `pandas`, `azure-kusto-data`, `azure-kusto-ingest`, `python-dotenv` (versions in the script header) | |
| upload_to_blob_storage.py | Upload files from local folder(s) to Azure Blob Storage | [Azure Storage Blobs client library for Python v12.14.1](https://pypi.org/project/azure-storage-blob/12.14.1/)  | |