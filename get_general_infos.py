import parse
import os
import pandas as pd
import numpy as np
from helpers.general_info_helper import *


# We set the different directories and then excel files to be accessed for the code to be more clear
DATA_DIRECTORY = f"..{os.sep}data" 
INFORMATION_DIRECTORY = f"{os.sep}information" 
STUDIES_DIRECTORY = f"{os.sep}studies" 
OUTPUT_DIRECTORY = f"{os.sep}output" 

UNREFINDE_STUDY_LIST = f"{os.sep}unrefined_study_information.xlsx"
STUDY_LIST = f"{os.sep}study_information.xlsx"
STUDY_ANNOTATION = f"{os.sep}study_annotation.xlsx"

#We want to be able to add a library for each of our studies. 
#The following dictionnary will be used to associate each of our studies to one of these libraries later on.
libraries = {
    "https://www.ncbi.nlm.nih.gov" : 'NCBI',
    "https://onlinelibrary.wiley.com" : 'Wiley',
    "https://besjournals.onlinelibrary.wiley.com" : 'BES-Wiley',
    "https://academic.oup.com" : 'Oxford Academic',
    "https://www.sciencedirect.com" : 'Science Direct',
    "https://journals.biologists.com" : 'The company of biologists'
}


# We load both of the excel sheets containing, respectively, the unrefined/unadded studies, the different annotations concerning our studies
# and the list of studies we already have into two distinct dataframes
unrefined_studies = pd.read_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + UNREFINDE_STUDY_LIST)
annotations = pd.read_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + STUDY_ANNOTATION)
studies = pd.read_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + STUDY_LIST)


#We populate the unrefined_studies df columns (DOI, Journal, Year, Authors, Abbreviation) using the info_from_titles function (see general_info_helper.py)
unrefined_studies['DOI'], unrefined_studies['Journal'], unrefined_studies['Year'], unrefined_studies['Authors'], unrefined_studies['Abbreviation'] = get_general_info_from_titles(unrefined_studies['Title of study'])
try:
 not unrefined_studies['DOI'].isnull().values.any()
except ValueError:
    raise ValueError("One or several of the DOIs is/are empty in unrefined_studies.xlsx.")


#We make all our studies correspond to a library, from the libraries dictionnary declared earlier.
for key in libraries.keys():
    unrefined_studies.loc[unrefined_studies['Link'].str.contains(key),'library'] = libraries[key]
try:
 not unrefined_studies['library'].isnull().values.any()
except ValueError:
    raise ValueError("One or several of the papers in unrefined_studies.xlsx do not belong to any of the libraries.")

#Keeping only the new studies in the unrefined_studies df
unrefined_studies['New'] = unrefined_studies.apply(lambda x: isNew(x['DOI'], studies), axis=1)
unrefined_studies = unrefined_studies.loc[unrefined_studies['New']]

#Adding identifiers, annotations and blank download informations for all our studies.
unrefined_studies = set_identifiers(unrefined_studies,studies)
unrefined_studies = add_annotations(unrefined_studies,annotations)
unrefined_studies = prepare_download_infos(unrefined_studies)


unrefined_studies = unrefined_studies.rename(columns={"Authors": "AuthorCitation"})
unrefined_studies['AuthorCitation'] = unrefined_studies['AuthorCitation'] + ' ' + unrefined_studies['Year'].astype(str)

unrefined_studies['Populated'] = True

unrefined_studies = unrefined_studies[['StudyID', 'Abbreviation', 'AuthorCitation','Year', 'Journal', 'Title of study', 'DOI', 'Populated', 'Phenotype_Keywords', 'Mother_Class', 'Corresponding_Author', 'Data_Availability_Comment', 'Other_Comments', 'Annotated', 'Downloaded', 'library', 'Link', 'FTP_Downloaded', 'FTP', 'Figshare_Downloaded', 'Figshare_ID', 'Github_Downloaded', 'Github_Link', 'Closed_Access_Identified']]

final_studies = pd.concat([studies, unrefined_studies], ignore_index = True)

final_studies.to_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + STUDY_LIST, index = False)  