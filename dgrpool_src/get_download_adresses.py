from helpers.adresses_helper import *

import os
import pandas as pd
import numpy as np


DATA_DIRECTORY = f"..{os.sep}data" 
INFORMATION_DIRECTORY = f"{os.sep}information" 
STUDIES_DIRECTORY = f"{os.sep}studies" 
OUTPUT_DIRECTORY = f"{os.sep}output" 

STUDY_LIST = f"{os.sep}study_information.xlsx"


studies = pd.read_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + STUDY_LIST)

#We first append to our studies dataframe the github links, if it exists, containing the data for each of our studies.
studies = retrieve_github_links(studies)

# We now do the exact same thing for the Figshare IDs.
headers = {'Content-Type': 'application/json', 'Authorization': 'token 8c86c3260125d2a738d2cd90f13222a8da81c691dbc2ff0b700525a8c3001f78e15573226526b8ab85e78a1020beac288c30654ec0df8340e182bce6c792fd36'}
BASE_URL = 'https://api.figshare.com/v2'

studies = retrieve_figshare_ids(studies,headers,BASE_URL)

#We finally retrieve the FTP adresses of the papers, when it's possible.
studies = retrieve_ftp_adresses(studies)


studies.to_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + STUDY_LIST, index = False)  