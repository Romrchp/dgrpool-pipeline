import pandas as pd
import numpy as np
import json

import requests
from bs4 import BeautifulSoup
from urllib import request
import urllib.request
import re
from Levenshtein import distance as lev
import xml.etree.ElementTree as ET
from ftplib import FTP


def retrieve_github_links(studies_df) :

    studies = studies_df

    for index, row in studies.iterrows():
        
        # If the paper info has not been already downloaded, get the Data Availability Statement of the NCBI page
        if not(row['Downloaded']):
            
            full_response = requests.get(row['Link'])
            soup = BeautifulSoup(full_response.text, 'html.parser')
            
            statement_bs4 = soup.find(id = "data-avl-stmnt")
            
            # We get all the urls of the Data Availability Statement Section (only the ones under http and https)
            if statement_bs4 is not None:
              statement = statement_bs4.get_text()   
              all_links = re.findall(r'(http[s]?://[^\s]+)', statement)
              
              # We proceed only if we find some valid links
              if all_links :
                good_links = []
                  
                # Checks and keeps only github or Figshare (DOI) links in all the valid URL links    
                for link in all_links :
                    if ((link.find('doi.org') != -1) or (link.find('github.com') != -1)) :
                        good_links.append(link)
                        
                # Remove unwanted characters that can occur at the end of the links ( . or () generally )
                for gl in good_links:
                        while (gl[-1] == '.' or gl[-1] == ')') :
                               gl = gl[:-1]
                    
                        # Adds the link to the right place
                        
                        if (gl.find('doi.org') != -1) :
                            pass
                           #studies.loc[index, 'Figshare_Link'] = gl
                        else :
                            pass
                           #studies.loc[index, 'Figshare_Link'] = np.nan
                    
                        if (gl.find('github.com') != -1) :
                           studies.loc[index, 'Github_Link'] = gl
                        else :
                           studies.loc[index, 'Github_Link'] = np.nan

    return studies;

def retrieve_figshare_ids(studies_df,headers,base_url) :

    tmp_studies_df = studies_df

    for index, row in tmp_studies_df.iterrows():
        if not(row['Downloaded']) and not(row['Figshare_Downloaded']) and type(row['Figshare_ID']) != type(str):
              query = {
              'search_for' :':resource_title: {}'.format(row['Title of study']),
              'page_size' : '100'
              }
      
              r = requests.post(base_url + "/articles/search", params = query, headers = headers)
              articles = json.loads(r.text)
              resource_title = list([ item['resource_title'] for item in articles])
      
              ids = []
      
              for i,title in enumerate(resource_title):
                  if lev(title, row['Title of study']) < 3:
                      ids.append(articles[i]['id'])
                      
              if len(ids) > 0:
                  ids = list([str(id) for id in ids])
                  string_ids = '-'.join(ids)
                  tmp_studies_df.loc[index, 'Figshare_ID'] = string_ids
              else:
                  tmp_studies_df.loc[index, 'Figshare_ID'] = np.nan

    return(tmp_studies_df)


class ClosedAccess(Exception):
    pass

def find_ftp_adress_ncbi(pmc_id):

    # https://www.ncbi.nlm.nih.gov/pmc/tools/oa-service/ 
    response = requests.get(f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmc_id}")
    
    if str(response) == '<Response [200]>':
        doc = (ET.fromstring(response.text))
        errors = doc.findall('error')
        if len(errors) == 0:
            records = doc.findall('records')
            if len(records) == 1:
                link_count = int(records[0].attrib['returned-count'])
                # Test for attribute presence ? Test for only one record ? Test if first link is really the tar ?
                if len(records[0][0]) == link_count:
                        ftp_adress = doc[2][0][0].attrib['href']
                else :
                    print(f"Malformed Response for PMC_ID :{pmc_id}")
                    ftp_adress[pmc_id] = np.nan
                    print(response.text)
            else :
                print(f"Malformed Response for PMC_ID :{pmc_id}")
                ftp_adress = np.nan
        else:
            for error in errors:
                if "not Open Access" in error.text:
                    raise ClosedAccess()
                else:
                    print(f"Error for PMC_ID :{pmc_id} - {error.text}")
                    ftp_adress = np.nan
    else:
        print(f"Error for PMC_ID :{pmc_id} - {str(response)}")
        ftp_adress = np.nan
        
    return ftp_adress

def retrieve_ftp_adresses(studies_df) :

    tmp_studies_df = studies_df

    for index, row in studies_df.iterrows():
        if not(row['Downloaded']) and type(row['FTP']) != str and not(row['Closed_Access_Identified']):
            #NCBI
            if row['library'] == 'NCBI':
                pmc_id = row['Link'][row['Link'].find('/PMC')+1:-1]
                try :
                    ftp_adress = find_ftp_adress_ncbi(pmc_id)
                except ClosedAccess:
                    studies_df.loc[index, 'Closed_Access_Identified'] = True
            else:
                ftp_adress = np.nan
    
            studies_df.loc[index, 'FTP'] = ftp_adress
    