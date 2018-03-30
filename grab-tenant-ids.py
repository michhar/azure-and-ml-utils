import csv
import argparse
import os
import json

def main(file):
    """Function to read a file with Azure subs, IDs, passwords
    and output a comma separated string of Tenant IDs
    
    Parameters
    ----------
    file : str
        The csv file with Azure login info
    
    Returns
    -------
    str
        A comma separated, quoted, list of tenant ids
    """
    with open(file) as csvfile:
        tenantids = set()
        reader = csv.DictReader(csvfile)
        for row in reader:
            user = row['Azure UserName']
            passwd = row['Azure Password']

            cmd = "az login -u {} -p {}".format(user, passwd)

            out = os.popen(cmd).read()
            data = json.loads(out)
            tenantids.add('"' + data[0]['tenantId'] + '"')

    idout = ",".join(tenantids)
    print(idout)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Azure sub file")
    args = parser.parse_args()
    main(args.file)