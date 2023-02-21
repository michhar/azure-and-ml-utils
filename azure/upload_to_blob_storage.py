"""
Python script to upload data to blob storage (tested with azure-storage-blob==12.3.1)

Make sure to set the environment variables before running:
- STORAGE_CONNECTION_STRING
- STORAGE_CONTAINER_NAME
"""
import os
from azure.storage.blob import BlobServiceClient
import argparse
import glob

def arg_parse():
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser(description='This script is for uploading a directory to Azure Blob Storage.')
    parser.add_argument("--dir", dest='directory', help="The directory to upload")
    return parser.parse_args()

args = arg_parse()

CONN_STRING = os.getenv("STORAGE_CONNECTION_STRING", "")
CONTAINER = os.getenv("STORAGE_CONTAINER_NAME", "")

# Instantiate a BlobServiceClient using a connection string
blob_service_client = BlobServiceClient.from_connection_string(CONN_STRING)

# Instantiate a ContainerClient
container_client = blob_service_client.get_container_client(CONTAINER) 

# Create new Container
try:
    container_client.create_container()
except Exception as err:
    print("WARNING: problem creating new container (the container may already exist)")
    pass

for filename in glob.iglob(os.path.join(args.directory, '**', '*'), recursive=True):
    if os.path.isfile(filename):

        # Upload a blob to the container
        with open(filename, "rb") as data:
            try:
                print('Uploading ', filename)
                container_client.upload_blob(name=filename, data=data)
            except Exception as err:
                print("WARNING: issue uploading (the file may already exist)")
                pass

# Check that the files uploaded correctly to blob
generator = container_client.list_blobs()
print('Current Blobs in Azure for this folder: ')
for blob in generator:
    print("  Blob/file: " + blob.name)