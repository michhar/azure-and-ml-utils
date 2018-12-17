import os
from azure.storage.blob import BlockBlobService
import argparse

def arg_parse():
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser(description='This script is for downloading blob files from a blob storage container on Azure.')
    parser.add_argument("--container", dest='container', help="Blob storage container name", type=str)
    parser.add_argument("--account", dest='account', help="Storage account name", type=str)
    parser.add_argument("--key", dest='key', help="Storage account key", type=str)
    return parser.parse_args()

args = arg_parse()


block_blob_service = BlockBlobService(account_name=args.account, account_key=args.key)

container_name = args.container

generator = block_blob_service.list_blobs(container_name)
for blob in generator:
    print("\t Blob name: " + blob.name)
    os.makedirs(os.path.dirname(blob.name), exist_ok=True)
    # Download the blob(s).
    block_blob_service.get_blob_to_path(container_name, blob.name, blob.name)
