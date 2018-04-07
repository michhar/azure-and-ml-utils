#!/usr/bin/env python
"""

Description:  A script to get Tenant IDs using the Azure CLI
from Azure logins provided in a csv file with specific headers.
There is an optional flag if a certain type of csv file
is used, which collects Azure logins into teams.

"""

import csv
import argparse
import os
import json
from collections import defaultdict
import inflect

__author__ = "Micheleen Harris"
__license__ = "MIT"
__status__ = "Development"

def num2word(num):
    """This util converts an integer to it's word represenation"""
    p = inflect.engine()
    numword = list(p.number_to_words(num))
    # Capitalize first letter
    numword[0] = str.upper(numword[0])
    numword = ''.join(numword)
    return numword

def main(file, teaminfoflag):
    """Function to read a file with Azure subs, IDs, passwords
    and output a comma separated string of Tenant IDs plus (optionally) 
    team assigments.  This was made for ML OpenHack.
    
    Expected column names currently (replace as needed): Team Account Log-In,Team Account Password , CSP Subscription Id, Azure DisplayName,Azure Account Log-In,Azure Account Password

    Parameters
    ----------
    file : str
        The csv file with Azure login info of a certain format, however 
        this script may be modified under different conditions.
    teaminfoflag : command line flag, False when not present
        Simple flag for whether or not to produce a json representation
        of the User, Sub and Team assignments (for a particular use case)

    Returns
    -------
    tuple of str
        A comma separated, quoted, list of tenant ids and
        A json representation of User, Subscription ID, and a Team
        from the special csv file from a vendor (script could be generalized)
    """
    with open(file) as csvfile:
        tenantids = set()
        reader = csv.DictReader(csvfile)
        rowlist = list(reader)

        # Move past the header
        next(reader, None)

        if teaminfoflag:
            # Initialize everything
            teaminfolist, smalldict, tmpusernames, teamnum, subid = [], defaultdict(), [], 1, ''

        for i in range(len(rowlist)):
            row = rowlist[i]

            # Blank row, add collated info to list
            if not row['Azure Account Log-In']:
            # kindly, the creator of this particular file left blank lines between teams
                if teaminfoflag and subid:
                    smalldict['SubscriptionId'] = subid
                    smalldict['Usernames'] = tmpusernames
                    smalldict['TeamName'] = 'Team {}'.format(num2word(teamnum))
                    teaminfolist.append(smalldict)
                    # Set up for next team - reset things
                    tmpusernames, smalldict = [], defaultdict()
                    teamnum += 1
                continue

            user = row['Azure Account Log-In'].replace(' Azure UserName: ','')
            if teaminfoflag:
                tmpusernames.append(user)
                subid = row[' CSP Subscription Id'].replace(' CSP Subscription Id: ', '')
            passwd = row['Azure Account Password'].replace(' Azure Password: ', '')

            # Log in to Azure using Azure CLI
            cmd = "az login -u {} -p \"{}\"".format(user, passwd)
            out = os.popen(cmd).read()
            if not out:
                # this may be due to a tricky password character
                continue
            data = json.loads(out)
            tenantids.add('"' + data[0]['tenantId'] + '"')

    tenantids_str = ",\n".join(tenantids)
    print(tenantids_str)

    # Populate with the last team's info
    if teaminfoflag:
        smalldict['SubscriptionId'] = subid
        smalldict['Usernames'] = tmpusernames
        smalldict['TeamName'] = 'Team {}'.format(num2word(teamnum))
        teaminfolist.append(smalldict)
    print(json.dumps(teaminfolist, indent=4))

    return tenantids_str, teaminfolist
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Azure sub file")
    # Optional flag for gleaning info around "teams" of users
    parser.add_argument('--teaminfo', action='store_true')

    args = parser.parse_args()
    main(args.file, args.teaminfo)