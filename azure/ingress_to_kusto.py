"""
Python ingress example for Kusto DB (from CSV file)

usage: ingress_to_kusto.py --csv CSV_FILENAME --cluster ADX_CLUSTER --region AZ_REGION --db ADX_DB_NAME --table ADX_TABLE_NAME --timestamp-name TIMESTAMP_NAME

There must be a file called ".env" in this folder with the environment variables 
(each is NAME_OF_VAR=value, one per line).

It must be an AAD application / Service Principal that is cleared for access to 
the ADX databases (give this Service Principal access to ADX first). The variables needed are:
- TENANT_ID
- CLIENT_ID
- SECRET

To run you will need to pip install the following Python packages:

pandas==1.5.1
azure-kusto-data==3.1.3
azure-kusto-ingest==3.1.3
python-dotenv==0.12.0

Prerequisites:
- CSV file with data with timestamp in first column and a single header at the top
- An ADX database
- An ADX table with correct schema in ingress Kusto DB that matches contents of csv (order matters)
- A Service Principal that has been given permission to the ADX cluster and database

Hint to use KQL to create an empty table in an existing DB:
// Create table command example:
.create table ['IngestTest']  (['timestamp']:datetime, ['id']:int, ['name']:string, ['value']:long)
"""
import os
import pandas as pd
import time
import logging
import argparse

from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.data_format import DataFormat
from azure.kusto.ingest import IngestionProperties, QueuedIngestClient

from dotenv import load_dotenv


# set logger to print at info level
logger_format = '%(asctime)s:%(message)s'
logging.basicConfig(format=logger_format, level=logging.INFO, datefmt="%H:%M:%S")

# Load my environment variables (looks for .env file - for Kusto auth)
load_dotenv()

# Authenticate with following AAD username and password
# read more at https://docs.microsoft.com/en-us/onedrive/find-your-office-365-tenant-id 
AUTHORITY_ID = os.getenv("TENANT_ID", "")
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

def authenticate_to_kusto(cluster):
    """Authenticate and return kusto connection client"""
    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster,
                                                                                CLIENT_ID,
                                                                                CLIENT_SECRET,
                                                                                AUTHORITY_ID)
    # The authentication method will be taken from the chosen KustoConnectionStringBuilder.
    kusto_client = KustoClient(kcsb)
    return kusto_client

def authenticate_to_kusto_ingress(cluster):
    """Authenticate and return kusto connection client"""
    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster,
                                                                                CLIENT_ID,
                                                                                CLIENT_SECRET,
                                                                                AUTHORITY_ID)
    # The authentication method will be taken from the chosen KustoConnectionStringBuilder.
    kusto_client = QueuedIngestClient(kcsb)
    return kusto_client

def query_kusto(query, db, client):
    """Query a kusto DB given client object, returns pandas dataframe"""
    dataframe = pd.DataFrame([])
    logging.info('Retry is set to 3 times.')

    for i in range(4):
        if i > 0:
            logging.info('Retry {}'.format(i))
        try:
            # Execute query
            response = client.execute(db, query)
            # Convert to pandas dataframe
            res = response.primary_results[0]
            if res:
                dataframe = dataframe_from_result_table(res)
                if dataframe.empty:
                    time.sleep(10)
                    continue
                return dataframe
        except Exception as exp:
            logging.error('Exception occured: {}'.format(exp))
            # wait 10 seconds, then retry
            time.sleep(10)
            continue

    return dataframe

def get_last_ingress_date(client_ingr, adx_db_name, adx_table_name, timestamp_name):
    """Example to get the last row of ingress table to retrieve last date
    so as not to ingest same data twice.  Use your timestamp column instead
    of 'PreciseTimeStamp' as needed."""
    query = """
    {}
    | order by {} desc
    | limit 1
    """.format(adx_table_name, timestamp_name)
    
    dataframe_last = query_kusto(query, adx_db_name, client_ingr)
    if dataframe_last.shape[0] > 0:
        return dataframe_last[timestamp_name][0]
    else:
        return None

def ingress_kusto(dataframe_input, adx_db_name, adx_table_name, client):
    """Ingest into a kusto db give an input pandas dataframe"""
    t0 = time.time()
    logging.info('Ingest started.')
    ingestion_properties = IngestionProperties(database=adx_db_name,
                                               table=adx_table_name,
                                               data_format=DataFormat.CSV)
    try:
        response = client.ingest_from_dataframe(dataframe_input, ingestion_properties=ingestion_properties)
        return response
    except KustoServiceError as error:
        print("1. Error:", error)
        print("2. Is semantic error:", error.is_semantic_error())
        print("3. Has partial results:", error.has_partial_results())
        print("3. Result size:", len(error.get_partial_results()))
    except Exception as exp:
        print("Error {}", exp)
    t1 = time.time()
    logging.info('Ingest took {:.04f} minutes.'.format((t1-t0)/60))

def main(args):
    # ADX URLs
    cluster_ingress_url = f'https://ingest-{args.adx_cluster}.{args.az_region}.kusto.windows.net'
    cluster_ingress_query_url = f'https://{args.adx_cluster}.{args.az_region}.kusto.windows.net'

    # Authenticate main kusto db
    client_ingr = authenticate_to_kusto_ingress(cluster_ingress_url)

    # Get last date in sequence in ingress kusto db - use to avoid duplicating data
    # Logic may be used when reading csv or pulling data from original source
    # Not used directly in this script, only added as example
    client_ingr_for_query = authenticate_to_kusto(cluster_ingress_query_url)
    last_ingress_date = get_last_ingress_date(client_ingr_for_query,
                                            args.adx_db_name,
                                            args.adx_table_name,
                                            args.timestamp_name)
    first_date = None
    if last_ingress_date != None:
        first_date = pd.to_datetime(last_ingress_date)
    logging.info('Last date in kusto db is {}'.format(first_date))

    # Example of reading a csv into dataframe, parsing first column as dates
    # which will populate the index for dataframe.
    try:
        dataframe_final = pd.read_csv(args.csv_filename,
                                      sep=',',
                                      header=0,
                                      parse_dates=[0])
    except Exception as excp:
        print(f'Exception reading csv file: {excp}')
        return None

    # Only ingest new data
    if first_date != None:
        dataframe_final = dataframe_final[dataframe_final.index > first_date]

    # Check sizes and drop rows with NA/None
    print('Dataframe final size before dropna = {}'.format(dataframe_final.shape))
    dataframe_final.dropna(inplace=True)
    print('Dataframe final size after dropna = {}'.format(dataframe_final.shape))

    # Ingress to Kusto db...
    resp = ingress_kusto(dataframe_final,
                         args.adx_db_name,
                         args.adx_table_name,
                         client_ingr)

    print(resp)
    return resp

if __name__ == '__main__':
    """Main"""
    # For command line options
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--csv', type=str, dest='csv_filename',
        help='CSV timeseries file', required=True
    )
    parser.add_argument(
        '--cluster', type=str, dest='adx_cluster',
        help='ADX cluster name', required=True
    )
    parser.add_argument(
        '--region', type=str, dest='az_region', default='westus',
        help='Azure region (all lowercase), e.g., westus', required=True
    )
    parser.add_argument(
        '--db', type=str, dest='adx_db_name',
        help='ADX database name', required=True
    )
    parser.add_argument(
        '--table', type=str, dest='adx_table_name',
        help='ADX database table name', required=True
    )
    parser.add_argument(
        '--timestamp-name', type=str, dest='timestamp_name',
        help='Name of timestamp column (case sensitive)', required=True
    )

    args = parser.parse_args()
    main(args)
