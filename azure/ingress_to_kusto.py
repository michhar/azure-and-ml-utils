"""
Ingress example for Kusto DB (from CSV file)

There must be a file called ".env" in this folder with the environment variables 
(each is NAME_OF_VAR=value, one per line).

It must be an AAD application that is cleared by the engineering team for access to 
the databases below and the variables needed are:
- TENANT_ID
- CLIENT_ID
- SECRET

To run you will need to pip install the following Python packages:

pandas==1.1.4
azure-kusto-data==1.0.3
azure-kusto-ingest==1.0.3
python-dotenv==0.12.0

Prerequisite:  correct schema in ingress Kusto DB that matches contents of csv's dataframe
"""
import os
import pandas as pd
import time
import logging

from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder

from azure.kusto.ingest import (
    IngestionProperties,
    DataFormat,
    KustoIngestClient
)

from dotenv import load_dotenv


# set logger to print at info level
logger_format = '%(asctime)s:%(message)s'
logging.basicConfig(format=logger_format, level=logging.INFO, datefmt="%H:%M:%S")

# Load my environment variables (looks for .env file - for Kusto auth)
load_dotenv()

# read more at https://docs.microsoft.com/en-us/onedrive/find-your-office-365-tenant-id 
AUTHORITY_ID = os.getenv("TENANT_ID", "")
# In case you want to authenticate with AAD username and password
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("SECRET", "")

# Kusto clusters (ingress and ingress for query)
CLUSTER_INGR = "https://ingest-<clusername>.<region>.kusto.windows.net"
CLUSTER_INGR_QUERY = "https://<clusername>.<region>.kusto.windows.net"

# Databases and tablenames
DB_INGR = '<database-name>'
TABLENAME_INGR = '<table-name>'

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
    kusto_client = KustoIngestClient(kcsb)
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

def get_last_ingress_date(client_ingr):
    """Example to get the last row of ingress table to retrieve last date
    so as not to ingest same data twice.  Use your timestamp column instead
    of 'PreciseTimeStamp' as needed."""
    query = """
    {}
    | order by PreciseTimeStamp desc
    | limit 1
    """.format(TABLENAME_INGR)
    
    dataframe_last = query_kusto(query, DB_INGR, client_ingr)

    return dataframe_last['PreciseTimeStamp'][0]

def ingress_kusto(dataframe_input, db, client):
    """Ingest into a kusto db give an input pandas dataframe"""
    t0 = time.time()
    logging.info('Ingest started.')
    ingestion_properties = IngestionProperties(database=DB_INGR, table=TABLENAME_INGR, data_format=DataFormat.CSV)
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

def main():
    # Authenticate main kusto db
    client_ingr = authenticate_to_kusto_ingress(CLUSTER_INGR)

    # Get last date in sequence in ingress kusto db - use to avoid duplicating data
    # Logic may be used when reading csv or pulling data from original source
    # Not used directly in this script, only added as example
    client_ingr_for_query = authenticate_to_kusto(CLUSTER_INGR_QUERY)
    first_date = pd.to_datetime(get_last_ingress_date(client_ingr_for_query))
    logging.info('Last date in kusto db is {}'.format(first_date))

    # Example of reading a csv into dataframe, parsing first column as dates
    # which will populate the index for dataframe.
    dataframe_final = pd.read_csv('new_data.csv',
                                    header=0,
                                    parse_dates=[0])

    # Check sizes and drop rows with NA/None
    print('Dataframe final size before dropna = {}'.format(dataframe_final.shape))
    dataframe_final.dropna(inplace=True)
    print('Dataframe final size after dropna = {}'.format(dataframe_final.shape))

    # Ingress to Kusto db...
    resp = ingress_kusto(dataframe_final, DB_INGR, client_ingr)

if __name__ == '__main__':
    main()
