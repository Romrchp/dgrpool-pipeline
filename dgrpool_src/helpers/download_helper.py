import requests
import os
import tarfile
import json
import pygit2

import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET

from ftplib import FTP
from habanero import Crossref
from github import Github
from urllib import request


def create_adequate_dirs(studies_df,data_dir,studies_dir) :
    
    general_target_directory = data_dir + studies_dir
    
    for index,row in studies_df.iterrows():
        sub_directory_name = row['StudyID']

        if not(os.path.isdir(general_target_directory + {os.sep} + sub_directory_name)):
            os.mkdir(general_target_directory + {os.sep} + sub_directory_name)
        
        is_figshare_link =  not(np.isnan(studies_df.iloc[index]['Figshare_ID']))
        is_github_link = not(np.isnan(studies_df.iloc[index]['Github_Link']))
        is_FTP = not(np.isnan(studies_df.iloc[index]['FTP']))

        if ((is_figshare_link or is_github_link or is_FTP) and (not(os.path.isdir(general_target_directory + {os.sep} + sub_directory_name)))) :
            os.mkdir(general_target_directory + {os.sep} + sub_directory_name + {os.sep} + "Base_data")
        
        if(is_figshare_link and (not(os.path.isdir(general_target_directory + {os.sep} + sub_directory_name + {os.sep} + "FigshareDownload")))) :
            os.mkdir(general_target_directory + {os.sep} + sub_directory_name + {os.sep} + "Base_data" + {os.sep} +  "FigshareDownload" )

        if(is_github_link and (not(os.path.isdir(general_target_directory + {os.sep} + sub_directory_name + {os.sep} + "GithubDownload")))) :
            os.mkdir(general_target_directory + {os.sep} + sub_directory_name + {os.sep} + "Base_data" + {os.sep} +  "GithubDownload" )
        
        if(is_FTP and (not(os.path.isdir(general_target_directory + {os.sep} + sub_directory_name + {os.sep} + "FTPDownload")))) :
            os.mkdir(general_target_directory + {os.sep} + sub_directory_name + {os.sep} + "Base_data" + {os.sep} +  "FTPDownload" )


def FTP_download(studies_df,data_dir,studies_dir) :

    general_target_directory = data_dir + studies_dir

    ftp = FTP('ftp.ncbi.nlm.nih.gov') 
    ftp.login()              
    ftp.cwd("/pub/pmc/oa_package")

    for index,row in studies_df.iterrows():

        if (row['library'] == 'NCBI') and not(row['Downloaded']) and not(row['FTP_Downloaded']) and type(row['FTP']) == str :
            sub_directory_name = row['StudyID']
            variable_path = row['FTP'][46:]
            ftp.cwd(variable_path[:6])
            filename = variable_path[6:]
    
            handle = open(general_target_directory + "/" +  sub_directory_name + "/" + "Base_data" + "/" +  "FTPDownload"  + "/" + filename, 'wb')
            try:
                ftp.retrbinary('RETR %s' % filename, handle.write)
            except EOFError:
                pass
            handle.close()
            
            studies_df.loc[index, 'FTP_Downloaded'] = True
            ftp.cwd('./../..')
    
    ftp.close()

def figshare_download(studies_df,data_dir,studies_dir) :
    # Personal Access Token
    headers = {'Content-Type': 'application/json', 'Authorization': 'token 8c86c3260125d2a738d2cd90f13222a8da81c691dbc2ff0b700525a8c3001f78e15573226526b8ab85e78a1020beac288c30654ec0df8340e182bce6c792fd36'}
    BASE_URL = 'https://api.figshare.com/v2'

    for index,row in studies_df.iterrows():
        if (not(row['Downloaded'])) and (not(row['Figshare_Downloaded'])) and type(row['Figshare_ID']) == str:
            ids = row['Figshare_ID'].split('-')
            for id in ids:
                url = (BASE_URL + '/articles/§{}/files'.format(id))
                response = requests.get( url, headers = headers)
                figures = response.json()
                
                for figure in figures:
                    request.urlretrieve(figure['download_url'], data_dir + studies_dir + f"{os.sep}" + row['StudyID'] + os.sep + "Base_data" + f"{os.sep}" + 'FigshareDownload' + f"{os.sep}" + figure['name'])   
            
            
            studies_df.loc[index, 'Figshare_Downloaded'] = True


def github_download(studies_df,data_dir,studies_dir) :

    for index,row in studies_df.iterrows():
    
        if (not(row['Downloaded'])) and (not(row['Github_Downloaded'])) and str(row['Github_Link']) != 'nan' :
                   
                repoClone = pygit2.clone_repository(row['Github_Link'], data_dir + studies_dir + f"{os.sep}" +
                                                    row['StudyID'] + f"{os.sep}"+ "Base_data" + f"{os.sep}" + 'GithubDownload')
                                                    
                studies_df.loc[index, 'Github_Downloaded'] = True
